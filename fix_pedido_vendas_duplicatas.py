"""
Corrige duplicatas na tabela pedido_vendas e adiciona chave única (pedido_item_key)
para que novas coletas atualizem em vez de duplicar.
Execute UMA VEZ: python fix_pedido_vendas_duplicatas.py
"""
import sys
from src.database.manager import DatabaseManager
from src.config import Settings
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main():
    try:
        settings = Settings()
        db = DatabaseManager(settings.database)
        db.create_database_if_not_exists()

        with db.get_connection() as conn:
            cur = conn.cursor()

            cur.execute("SHOW TABLES LIKE 'pedido_vendas'")
            if not cur.fetchone():
                print("Tabela pedido_vendas não existe. Nada a fazer.")
                return

            cur.execute("SELECT COUNT(*) FROM pedido_vendas")
            total_antes = cur.fetchone()[0]
            print(f"Total de registros antes: {total_antes:,}")

            # 1. Adiciona coluna pedido_item_key se não existir
            cur.execute("""
                SELECT COUNT(*) FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pedido_vendas' AND COLUMN_NAME = 'pedido_item_key'
            """)
            if cur.fetchone()[0] == 0:
                cur.execute("ALTER TABLE pedido_vendas ADD COLUMN pedido_item_key VARCHAR(255) NULL AFTER id")
                print("Coluna pedido_item_key criada.")
            else:
                print("Coluna pedido_item_key já existe.")

            # 2. Preenche pedido_item_key
            cur.execute("""
                UPDATE pedido_vendas
                SET pedido_item_key = CONCAT(IFNULL(cod_pedido,''), '|', IFNULL(nr_sequencial_pedido,''), '|', IFNULL(produto_codigo_produto,''))
                WHERE pedido_item_key IS NULL OR pedido_item_key = ''
            """)
            cur.execute("""
                UPDATE pedido_vendas
                SET pedido_item_key = CONCAT('_id:', id)
                WHERE pedido_item_key = '' OR pedido_item_key = '||'
            """)
            print("Chave pedido_item_key preenchida.")

            # 3. Remove duplicatas (mantém o de menor id por chave)
            cur.execute("""
                DELETE t1 FROM pedido_vendas t1
                INNER JOIN pedido_vendas t2
                ON t1.pedido_item_key = t2.pedido_item_key
                AND t1.pedido_item_key IS NOT NULL AND t1.pedido_item_key != ''
                AND t1.id > t2.id
            """)
            removidos = cur.rowcount
            print(f"Registros duplicados removidos: {removidos:,}")

            # 4. Índice único (remove antes se existir)
            try:
                cur.execute("ALTER TABLE pedido_vendas DROP INDEX idx_pedido_item_key")
            except Exception:
                pass
            cur.execute("ALTER TABLE pedido_vendas ADD UNIQUE INDEX idx_pedido_item_key (pedido_item_key)")
            print("Índice único idx_pedido_item_key criado.")

            cur.execute("SELECT COUNT(*) FROM pedido_vendas")
            total_depois = cur.fetchone()[0]
            print(f"Total de registros depois: {total_depois:,}")
            print("Concluído. Próximas coletas não duplicarão pedidos de venda.")
            cur.close()

    except Exception as e:
        logger.error(str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
