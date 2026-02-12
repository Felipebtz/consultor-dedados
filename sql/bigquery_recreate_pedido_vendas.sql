-- BigQuery: apaga a tabela pedido_vendas para ser recriada na próxima coleta
-- com o novo schema (uma linha por pedido = total_de_registros da API ~9.354).
--
-- 1) No console do BigQuery, troque lille-422512 e p79_maqtools pelo seu projeto e dataset.
-- 2) Execute esta query UMA VEZ.
-- 3) Rode a coleta de novo (python -m src ou testar_coletor.py). A tabela será criada com o novo schema e preenchida.

DROP TABLE IF EXISTS `lille-422512.p79_maqtools.pedido_vendas`;
