-- Active: 1790792345299@@127.0.0.1@5432@radar_combustivel
CREATE TABLE IF NOT EXISTS precos_combustiveis (
    id BIGSERIAL PRIMARY KEY,

    regiao VARCHAR(2) NOT NULL,
    uf CHAR(2) NOT NULL,
    municipio VARCHAR(100) NOT NULL,

    revenda VARCHAR(200) NOT NULL,
    cnpj CHAR(18) NOT NULL,

    rua VARCHAR(200),
    numero VARCHAR(30),
    bairro VARCHAR(100),
    cep CHAR(9),

    produto VARCHAR(50) NOT NULL,

    data_coleta DATE NOT NULL,

    valor_venda NUMERIC(6, 3) NOT NULL
        CHECK (valor_venda > 0),

    unidade_medida VARCHAR(20) NOT NULL,
    bandeira VARCHAR(100)
);