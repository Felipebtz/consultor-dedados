-- Tabelas para os coletores de faturamento (servico_resumo, vendas_resumo, nfse, nf_consultar)
-- Execute no MySQL antes de rodar a coleta.

-- Resumo de faturamento de serviços (NFS-e, recibo)
CREATE TABLE IF NOT EXISTS servico_resumo (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    data_inicio VARCHAR(20),
    data_fim VARCHAR(20),
    n_faturadas INT,
    v_faturadas DECIMAL(18,2),
    n_pendentes INT,
    v_pendentes DECIMAL(18,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resumo de vendas (NF-e, CT-e, cupom fiscal)
CREATE TABLE IF NOT EXISTS vendas_resumo (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    data_inicio VARCHAR(20),
    data_fim VARCHAR(20),
    total_nf INT,
    valor_total DECIMAL(18,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Listagem de NFS-e emitidas
CREATE TABLE IF NOT EXISTS nfse (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(30),
    codigo_nfse VARCHAR(50),
    data_emissao VARCHAR(20),
    cod_cliente VARCHAR(30),
    valor_total DECIMAL(18,2),
    situacao VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Listagem de NF-e emitidas
CREATE TABLE IF NOT EXISTS nf_consultar (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    numero VARCHAR(30),
    serie VARCHAR(10),
    data_emissao VARCHAR(20),
    cod_cliente VARCHAR(30),
    valor_total DECIMAL(18,2),
    situacao VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
