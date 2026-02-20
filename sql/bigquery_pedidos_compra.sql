-- BigQuery: cria a tabela pedidos_compra (Pedidos de Compra - API Omie produtos/pedidocompra/).
-- Método: PesquisarPedCompra. Uma linha por pedido (cabeçalho).
--
-- 1) No console do BigQuery, troque lille-422512 e p79_maqtools pelo seu projeto e dataset.
-- 2) Execute esta query para criar a tabela manualmente (opcional; a coleta também cria automaticamente).

CREATE TABLE IF NOT EXISTS `lille-422512.p79_maqtools.pedidos_compra` (
  id INT64,
  cod_pedido STRING,
  cod_pedido_integracao STRING,
  numero STRING,
  cod_fornecedor STRING,
  cod_fornecedor_integracao STRING,
  cnpj_cpf_fornecedor STRING,
  data_previsao STRING,
  cod_parc STRING,
  qtde_parc INT64,
  cod_categoria STRING,
  cod_comprador STRING,
  contato STRING,
  numero_contrato STRING,
  numero_pedido_fornecedor STRING,
  cod_conta_corrente STRING,
  cod_conta_corrente_integracao STRING,
  cod_projeto STRING,
  observacao STRING,
  observacao_interna STRING,
  quantidade_itens INT64,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Para recriar a tabela do zero (apaga e depois rode a coleta para recriar):
-- DROP TABLE IF EXISTS `lille-422512.p79_maqtools.pedidos_compra`;
