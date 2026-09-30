-- ============================================================
-- RADAR COMBUSTÍVEL
-- Consultas analíticas
-- ============================================================


-- ============================================================
-- 1. QUANTIDADE TOTAL DE REGISTROS
-- ============================================================

SELECT
    COUNT(*) AS total_registros
FROM precos_combustiveis;


-- ============================================================
-- 2. PERÍODO DISPONÍVEL NO BANCO
-- ============================================================

SELECT
    MIN(data_coleta) AS primeira_coleta,
    MAX(data_coleta) AS ultima_coleta
FROM precos_combustiveis;


-- ============================================================
-- 3. DADOS DA PARAÍBA
-- ============================================================

SELECT
    COUNT(*) AS registros,
    COUNT(DISTINCT municipio) AS municipios,
    COUNT(DISTINCT cnpj) AS postos
FROM precos_combustiveis
WHERE uf = 'PB';


-- ============================================================
-- 4. ESTATÍSTICAS DE PREÇOS NA PARAÍBA
-- ============================================================

SELECT
    produto,
    COUNT(*) AS quantidade,
    ROUND(AVG(valor_venda), 3) AS media,
    ROUND(
        PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY valor_venda)::numeric,
        3
    ) AS mediana,
    MIN(valor_venda) AS minimo,
    MAX(valor_venda) AS maximo
FROM precos_combustiveis
WHERE uf = 'PB'
GROUP BY produto
ORDER BY produto;


-- ============================================================
-- 5. DADOS DE JOÃO PESSOA
-- ============================================================

SELECT
    COUNT(*) AS registros,
    COUNT(DISTINCT cnpj) AS postos
FROM precos_combustiveis
WHERE
    uf = 'PB'
    AND municipio = 'JOAO PESSOA';


-- ============================================================
-- 6. ESTATÍSTICAS DE PREÇOS EM JOÃO PESSOA
-- ============================================================

SELECT
    produto,
    COUNT(*) AS quantidade,
    ROUND(AVG(valor_venda), 3) AS media,
    ROUND(
        PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY valor_venda)::numeric,
        3
    ) AS mediana,
    MIN(valor_venda) AS minimo,
    MAX(valor_venda) AS maximo
FROM precos_combustiveis
WHERE
    uf = 'PB'
    AND municipio = 'JOAO PESSOA'
GROUP BY produto
ORDER BY produto;


-- ============================================================
-- 7. PREÇO MÉDIO POR DATA EM JOÃO PESSOA
-- ============================================================

SELECT
    data_coleta,
    produto,
    ROUND(AVG(valor_venda), 3) AS preco_medio
FROM precos_combustiveis
WHERE
    uf = 'PB'
    AND municipio = 'JOAO PESSOA'
GROUP BY
    data_coleta,
    produto
ORDER BY
    data_coleta,
    produto;


-- ============================================================
-- 8. CINCO MENORES PREÇOS MAIS RECENTES POR COMBUSTÍVEL
-- ============================================================

WITH ultimo_preco AS (

    SELECT DISTINCT ON (cnpj, produto)
        cnpj,
        revenda,
        bairro,
        produto,
        valor_venda,
        data_coleta
    FROM precos_combustiveis
    WHERE
        uf = 'PB'
        AND municipio = 'JOAO PESSOA'
    ORDER BY
        cnpj,
        produto,
        data_coleta DESC
),

ranking AS (

    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY produto
            ORDER BY valor_venda ASC
        ) AS posicao
    FROM ultimo_preco
)

SELECT
    produto,
    revenda,
    bairro,
    valor_venda,
    data_coleta
FROM ranking
WHERE posicao <= 5
ORDER BY
    produto,
    valor_venda;