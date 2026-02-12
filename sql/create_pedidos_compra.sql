-- Tabela para o coletor de Pedidos de Compra (produtos/pedidocompra/ - PesquisarPedCompra).
-- Execute no MySQL antes de rodar a coleta (opcional; a coleta também cria automaticamente).

CREATE TABLE IF NOT EXISTS pedidos_compra (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cod_pedido VARCHAR(50),
    cod_pedido_integracao VARCHAR(50),
    numero VARCHAR(30),
    cod_fornecedor VARCHAR(50),
    data_previsao VARCHAR(20),
    cod_conta_corrente VARCHAR(50),
    cod_projeto VARCHAR(50),
    observacao TEXT,
    quantidade_itens INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
