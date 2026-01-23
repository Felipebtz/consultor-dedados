"""
Script para resetar o banco de dados (opcional).
Use apenas se quiser começar do zero.
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


def resetar_banco():
    """Remove e recria o banco de dados."""
    try:
        settings = Settings()
        db_name = settings.database.DB_NAME
        
        print("\n" + "="*80)
        print("⚠️  ATENÇÃO: RESETAR BANCO DE DADOS")
        print("="*80)
        print(f"\nEste script irá:")
        print(f"  1. REMOVER o banco de dados '{db_name}'")
        print(f"  2. RECRIAR o banco de dados vazio")
        print(f"  3. As tabelas serão recriadas na próxima execução de 'executar.bat'")
        print("\n⚠️  TODOS OS DADOS SERÃO PERDIDOS!")
        print("="*80)
        
        resposta = input("\nDeseja continuar? (digite 'SIM' para confirmar): ")
        
        if resposta.upper() != 'SIM':
            print("\n❌ Operação cancelada pelo usuário.")
            return
        
        print("\n🔄 Removendo banco de dados...")
        
        # Conecta sem especificar o banco
        import mysql.connector
        config = {
            "host": settings.database.DB_HOST,
            "port": settings.database.DB_PORT,
            "user": settings.database.DB_USER,
            "password": settings.database.DB_PASSWORD,
            "charset": "utf8mb4",
            "collation": "utf8mb4_unicode_ci"
        }
        
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Remove o banco
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        print(f"✓ Banco '{db_name}' removido")
        
        # Recria o banco
        cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ Banco '{db_name}' recriado")
        
        cursor.close()
        connection.close()
        
        # Recria o pool de conexões
        db_manager = DatabaseManager(settings.database)
        db_manager.create_database_if_not_exists()
        
        print("\n" + "="*80)
        print("✅ BANCO DE DADOS RESETADO COM SUCESSO!")
        print("="*80)
        print("\nPróximos passos:")
        print("  1. Execute 'executar.bat' para recriar as tabelas e coletar dados")
        print("  2. As tabelas serão criadas com os índices únicos corretos")
        print("="*80 + "\n")
        
    except Exception as e:
        logger.error(f"Erro ao resetar banco: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    resetar_banco()
