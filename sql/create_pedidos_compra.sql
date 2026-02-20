-- MySQL: tabela pedidos_compra (produtos/pedidocompra/ - PesquisarPedCompra).
-- Execute no MySQL. Para BigQuery use: sql/bigquery_pedidos_compra.sql (sintaxe diferente, sem AUTO_INCREMENT).

CREATE TABLE IF NOT EXISTS pedidos_compra (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cod_pedido VARCHAR(50),
    cod_pedido_integracao VARCHAR(50),
    numero VARCHAR(30),
    cod_fornecedor VARCHAR(50),
    cod_fornecedor_integracao VARCHAR(50),
    cnpj_cpf_fornecedor VARCHAR(20),
    data_previsao VARCHAR(20),
    cod_parc VARCHAR(10),
    qtde_parc INT,
    cod_categoria VARCHAR(30),
    cod_comprador VARCHAR(20),
    contato VARCHAR(120),
    numero_contrato VARCHAR(30),
    numero_pedido_fornecedor VARCHAR(30),
    cod_conta_corrente VARCHAR(50),
    cod_conta_corrente_integracao VARCHAR(50),
    cod_projeto VARCHAR(50),
    observacao TEXT,
    observacao_interna TEXT,
    quantidade_itens INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
