"""
Script para corrigir duplicatas nas tabelas de contas a pagar e receber.
Adiciona índices únicos e remove registros duplicados.
"""
import sys
from src.database.manager import DatabaseManager
from src.config import Settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fix_duplicatas():
    """Corrige duplicatas nas tabelas de contas."""
    try:
        settings = Settings()
        db_manager = DatabaseManager(settings.database)
        
        print("\n" + "="*80)
        print("CORREÇÃO DE DUPLICATAS - CONTAS A PAGAR E RECEBER")
        print("="*80 + "\n")
        
        # Processa contas a pagar
        print("1. Processando CONTAS A PAGAR...")
        processar_tabela(db_manager, "contas_pagar", "codigo_lancamento")
        
        # Processa contas a receber
        print("\n2. Processando CONTAS A RECEBER...")
        processar_tabela(db_manager, "contas_receber", "codigo_lancamento")
        
        print("\n" + "="*80)
        print("CORREÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*80 + "\n")
        
    except Exception as e:
        logger.error(f"Erro ao corrigir duplicatas: {str(e)}", exc_info=True)
        sys.exit(1)


def processar_tabela(db_manager: DatabaseManager, tabela: str, campo_unico: str):
    """Processa uma tabela: remove duplicatas e adiciona índice único."""
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Verifica se a tabela existe
            cursor.execute(f"SHOW TABLES LIKE '{tabela}'")
            if not cursor.fetchone():
                print(f"  ⚠️  Tabela '{tabela}' não existe. Pulando...")
                cursor.close()
                return
            
            # Conta registros antes
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            total_antes = cursor.fetchone()[0]
            print(f"  📊 Total de registros antes: {total_antes:,}")
            
            # Verifica se há duplicatas
            cursor.execute(f"""
                SELECT {campo_unico}, COUNT(*) as qtd
                FROM {tabela}
                WHERE {campo_unico} IS NOT NULL AND {campo_unico} != ''
                GROUP BY {campo_unico}
                HAVING COUNT(*) > 1
            """)
            duplicatas = cursor.fetchall()
            
            if duplicatas:
                print(f"  ⚠️  Encontradas {len(duplicatas):,} chaves com duplicatas")
                
                # Remove duplicatas, mantendo apenas o registro mais recente
                print(f"  🧹 Removendo duplicatas (mantendo o registro mais recente)...")
                
                # Primeiro, remove o índice único se existir (para evitar erro)
                try:
                    cursor.execute(f"ALTER TABLE {tabela} DROP INDEX {campo_unico}")
                    print(f"  ✓ Índice antigo removido")
                except:
                    pass  # Índice não existe, continua
                
                # Remove duplicatas mantendo o ID mais alto (mais recente)
                cursor.execute(f"""
                    DELETE t1 FROM {tabela} t1
                    INNER JOIN {tabela} t2
                    WHERE t1.{campo_unico} = t2.{campo_unico}
                    AND t1.{campo_unico} IS NOT NULL
                    AND t1.{campo_unico} != ''
                    AND t1.id < t2.id
                """)
                removidos = cursor.rowcount
                print(f"  ✓ {removidos:,} registros duplicados removidos")
            else:
                print(f"  ✓ Nenhuma duplicata encontrada")
            
            # Adiciona índice único
            print(f"  🔧 Adicionando índice único em '{campo_unico}'...")
            try:
                # Verifica quantos registros têm valor NULL/vazio
                cursor.execute(f"""
                    SELECT COUNT(*) FROM {tabela}
                    WHERE {campo_unico} IS NULL OR {campo_unico} = ''
                """)
                null_count = cursor.fetchone()[0]
                
                if null_count > 0:
                    print(f"  ⚠️  {null_count:,} registros com {campo_unico} NULL/vazio encontrados")
                    print(f"  🔧 Gerando valores temporários únicos para registros NULL...")
                    # Gera valores únicos temporários para registros NULL/vazios
                    cursor.execute(f"""
                        UPDATE {tabela}
                        SET {campo_unico} = CONCAT('TEMP_', id)
                        WHERE {campo_unico} IS NULL OR {campo_unico} = ''
                    """)
                
                # Adiciona índice único
                cursor.execute(f"""
                    ALTER TABLE {tabela}
                    ADD UNIQUE INDEX idx_{campo_unico} ({campo_unico})
                """)
                print(f"  ✓ Índice único criado com sucesso")
            except Exception as e:
                if "Duplicate entry" in str(e) or "Duplicate key" in str(e):
                    print(f"  ⚠️  Ainda existem duplicatas. Tentando remover novamente...")
                    # Remove duplicatas novamente
                    cursor.execute(f"""
                        DELETE t1 FROM {tabela} t1
                        INNER JOIN {tabela} t2
                        WHERE t1.{campo_unico} = t2.{campo_unico}
                        AND t1.id < t2.id
                    """)
                    # Tenta criar o índice novamente
                    cursor.execute(f"""
                        ALTER TABLE {tabela}
                        ADD UNIQUE INDEX idx_{campo_unico} ({campo_unico})
                    """)
                    print(f"  ✓ Índice único criado após limpeza adicional")
                else:
                    raise
            
            # Conta registros depois
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            total_depois = cursor.fetchone()[0]
            print(f"  📊 Total de registros depois: {total_depois:,}")
            print(f"  📉 Registros removidos: {total_antes - total_depois:,}")
            
            cursor.close()
            
    except Exception as e:
        logger.error(f"Erro ao processar tabela '{tabela}': {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    fix_duplicatas()
