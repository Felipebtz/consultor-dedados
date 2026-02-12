-- Corrige duplicatas em pedido_vendas e adiciona chave única para evitar novas duplicações.
-- Execute no MySQL UMA VEZ (ex.: mysql -u root -p coleta_dados < sql/fix_pedido_vendas_duplicatas.sql)
-- Se a coluna pedido_item_key já existir, pule o passo 1.

USE coleta_dados;

-- 1. Adiciona coluna de chave única (ignore erro se já existir)
ALTER TABLE pedido_vendas ADD COLUMN pedido_item_key VARCHAR(255) NULL AFTER id;

-- 2. Preenche pedido_item_key nos registros existentes
UPDATE pedido_vendas
SET pedido_item_key = CONCAT(IFNULL(cod_pedido,''), '|', IFNULL(nr_sequencial_pedido,''), '|', IFNULL(produto_codigo_produto,''))
WHERE pedido_item_key IS NULL OR pedido_item_key = '';

UPDATE pedido_vendas
SET pedido_item_key = CONCAT('_id:', id)
WHERE pedido_item_key = '' OR pedido_item_key = '||';

-- 3. Remove duplicatas mantendo o registro com menor id por chave
DELETE t1 FROM pedido_vendas t1
INNER JOIN pedido_vendas t2
ON t1.pedido_item_key = t2.pedido_item_key
AND t1.pedido_item_key IS NOT NULL
AND t1.pedido_item_key != ''
AND t1.id > t2.id;

-- 4. Remove índice único antigo se existir (para re-executar)
-- ALTER TABLE pedido_vendas DROP INDEX idx_pedido_item_key;

-- 5. Adiciona índice único (evita novas duplicatas na coleta)
ALTER TABLE pedido_vendas ADD UNIQUE INDEX idx_pedido_item_key (pedido_item_key);
