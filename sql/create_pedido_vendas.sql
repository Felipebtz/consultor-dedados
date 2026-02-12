-- Tabela pedido_vendas (uma linha por pedido = total_de_registros da API Omie).
-- Chave única cod_pedido. Execute: mysql -u root -p coleta_dados < sql/create_pedido_vendas.sql

USE coleta_dados;

CREATE TABLE IF NOT EXISTS pedido_vendas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    cod_pedido VARCHAR(50),
    nr_pedido VARCHAR(50),
    nr_sequencial_pedido VARCHAR(50),
    cod_cliente VARCHAR(50),
    cod_etapa_faturamento VARCHAR(20),
    fl_faturado CHAR(1),
    fl_cancelado CHAR(1),
    dt_pedido VARCHAR(30),
    dt_previsao VARCHAR(30),
    cod_vendedor VARCHAR(50),
    total_vlr_pedido DECIMAL(15,2),
    quantidade_itens INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_cod_pedido (cod_pedido),
    INDEX idx_dt_pedido (dt_pedido),
    INDEX idx_cod_cliente (cod_cliente)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
