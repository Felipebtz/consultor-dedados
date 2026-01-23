"""
Gerenciador de banco de dados MySQL com pool de conexões.
"""
import mysql.connector
from mysql.connector import pooling, Error
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
import logging
import json
from src.core.interfaces import IDatabaseManager
from src.config import DatabaseSettings

logger = logging.getLogger(__name__)


class DatabaseManager(IDatabaseManager):
    """
    Gerenciador de banco de dados MySQL com pool de conexões.
    Implementa padrão Singleton para reutilização de conexões.
    """
    
    _instance = None
    _pool = None
    
    def __new__(cls, settings: DatabaseSettings = None):
        """Implementa padrão Singleton."""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, settings: DatabaseSettings = None):
        """
        Inicializa o gerenciador de banco de dados.
        
        Args:
            settings: Configurações do banco de dados
        """
        if settings is None:
            from src.config import Settings
            settings = Settings().database
        
        self.settings = settings
        
        if self._pool is None:
            self._create_pool()
    
    def _create_pool(self):
        """Cria o pool de conexões."""
        try:
            config = {
                "host": self.settings.DB_HOST,
                "port": self.settings.DB_PORT,
                "user": self.settings.DB_USER,
                "password": self.settings.DB_PASSWORD,
                "database": self.settings.DB_NAME,
                "pool_name": "omie_pool",
                "pool_size": self.settings.DB_POOL_SIZE,
                "pool_reset_session": True,
                "autocommit": False,
                "charset": "utf8mb4",
                "collation": "utf8mb4_unicode_ci"
            }
            
            self._pool = pooling.MySQLConnectionPool(**config)
            logger.info("Pool de conexões criado com sucesso")
            
        except Error as e:
            logger.error(f"Erro ao criar pool de conexões: {str(e)}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager para obter conexão do pool.
        
        Yields:
            Conexão MySQL
        """
        connection = None
        try:
            connection = self._pool.get_connection()
            yield connection
            connection.commit()
        except Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Erro na conexão: {str(e)}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def create_database_if_not_exists(self):
        """Cria o banco de dados se não existir."""
        try:
            config = {
                "host": self.settings.DB_HOST,
                "port": self.settings.DB_PORT,
                "user": self.settings.DB_USER,
                "password": self.settings.DB_PASSWORD,
                "charset": "utf8mb4",
                "collation": "utf8mb4_unicode_ci"
            }
            
            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()
            
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.settings.DB_NAME}")
            logger.info(f"Banco de dados '{self.settings.DB_NAME}' verificado/criado")
            
            cursor.close()
            connection.close()
            
            # Recria o pool com o banco de dados
            self._pool = None
            self._create_pool()
            
        except Error as e:
            logger.error(f"Erro ao criar banco de dados: {str(e)}")
            raise
    
    def create_table(self, table_name: str, schema: Dict[str, str]) -> bool:
        """
        Cria uma tabela no banco de dados.
        
        Args:
            table_name: Nome da tabela
            schema: Dicionário com nome da coluna e tipo SQL
            
        Returns:
            True se criada com sucesso
        """
        try:
            columns = ", ".join([f"{col} {type_def}" for col, type_def in schema.items()])
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns}) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                cursor.close()
            
            logger.info(f"Tabela '{table_name}' criada/verificada com sucesso")
            return True
            
        except Error as e:
            logger.error(f"Erro ao criar tabela '{table_name}': {str(e)}")
            return False
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """
        Achata um dicionário aninhado.
        
        Args:
            d: Dicionário a ser achatado
            parent_key: Chave pai (para recursão)
            sep: Separador para chaves aninhadas
            
        Returns:
            Dicionário achatado
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                # Se é um dict, achata recursivamente
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Se é uma lista, converte para JSON string
                items.append((new_key, json.dumps(v, ensure_ascii=False) if v else None))
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    def _prepare_value(self, value: Any) -> Any:
        """
        Prepara um valor para inserção no MySQL.
        Converte dict/list para JSON string.
        
        Args:
            value: Valor a ser preparado
            
        Returns:
            Valor preparado para MySQL
        """
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        elif isinstance(value, list):
            return json.dumps(value, ensure_ascii=False) if value else None
        elif value is None:
            return None
        else:
            return value
    
    def insert_batch(self, table_name: str, data: List[Dict[str, Any]]) -> int:
        """
        Insere dados em lote usando executemany para melhor performance.
        Trata dados aninhados convertendo para JSON ou achatando.
        
        Args:
            table_name: Nome da tabela
            data: Lista de dicionários com os dados
            
        Returns:
            Número de registros inseridos
        """
        if not data:
            return 0
        
        try:
            # Remove campos que não existem no schema
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Obtém as colunas da tabela
                cursor.execute(f"DESCRIBE {table_name}")
                columns = [row[0] for row in cursor.fetchall()]
                
                # Filtra e prepara os dados
                filtered_data = []
                for record in data:
                    # Achata dicionários aninhados
                    flattened = self._flatten_dict(record)
                    
                    # Filtra apenas colunas válidas e prepara valores
                    filtered_record = {}
                    for k, v in flattened.items():
                        if k in columns:
                            filtered_record[k] = self._prepare_value(v)
                    
                    if filtered_record:
                        filtered_data.append(filtered_record)
                
                if not filtered_data:
                    logger.warning(f"Nenhum dado válido para inserir na tabela '{table_name}'")
                    return 0
                
                # Prepara os dados para inserção
                columns_to_insert = list(filtered_data[0].keys())
                placeholders = ", ".join(["%s"] * len(columns_to_insert))
                columns_str = ", ".join(columns_to_insert)
                
                # Query com ON DUPLICATE KEY UPDATE para evitar duplicatas
                # Exclui id (auto-increment), created_at (mantém data original) e updated_at (será atualizado automaticamente)
                update_clause = ", ".join([
                    f"{col} = VALUES({col})" 
                    for col in columns_to_insert 
                    if col not in ["id", "created_at", "updated_at"]
                ])
                # Adiciona updated_at manualmente para atualizar timestamp
                if "updated_at" in columns_to_insert:
                    update_clause += ", updated_at = CURRENT_TIMESTAMP"
                
                query = f"""
                    INSERT INTO {table_name} ({columns_str})
                    VALUES ({placeholders})
                    ON DUPLICATE KEY UPDATE {update_clause}
                """
                
                # Prepara os valores
                values = []
                for record in filtered_data:
                    values.append([record.get(col) for col in columns_to_insert])
                
                # Insere em lote
                cursor.executemany(query, values)
                affected_rows = cursor.rowcount
                
                cursor.close()
                
            logger.info(f"Inseridos {affected_rows} registros na tabela '{table_name}'")
            return affected_rows
            
        except Error as e:
            logger.error(f"Erro ao inserir dados na tabela '{table_name}': {str(e)}")
            raise
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """
        Executa uma query SQL.
        
        Args:
            query: Query SQL
            params: Parâmetros da query (opcional)
            
        Returns:
            Resultado da query
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                result = cursor.fetchall()
                cursor.close()
                
                return result
                
        except Error as e:
            logger.error(f"Erro ao executar query: {str(e)}")
            raise
    
    def close_pool(self):
        """Fecha todas as conexões do pool."""
        if self._pool:
            # MySQL Connector não tem método direto para fechar o pool
            # As conexões serão fechadas automaticamente quando não houver mais referências
            self._pool = None
            logger.info("Pool de conexões fechado")
