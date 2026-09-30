from pathlib import Path

import pandas as pd


# ============================================================
# CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# ============================================================
# LOCALIZAR ARQUIVO MAIS RECENTE
# ============================================================

arquivos = list(
    RAW_DIR.glob("anp_gasolina_etanol_*.csv")
)

if not arquivos:
    raise FileNotFoundError(
        "Nenhum arquivo da ANP encontrado em data/raw/"
    )

arquivo_mais_recente = max(
    arquivos,
    key=lambda arquivo: arquivo.stat().st_mtime
)


# ============================================================
# CARREGAR DADOS
# ============================================================

print("=" * 60)
print("RADAR COMBUSTÍVEL - TRANSFORMAÇÃO")
print("=" * 60)

print(f"\nArquivo utilizado: {arquivo_mais_recente.name}")

df = pd.read_csv(
    arquivo_mais_recente,
    sep=";",
    encoding="utf-8-sig",
    decimal=",",
    low_memory=False
)

print(f"\nRegistros recebidos: {len(df):,}")


# ============================================================
# REMOVER COLUNAS NÃO UTILIZADAS
# ============================================================

colunas_remover = [
    "Valor de Compra",
    "Complemento"
]

df = df.drop(
    columns=colunas_remover,
    errors="ignore"
)


# ============================================================
# RENOMEAR COLUNAS
# ============================================================

df = df.rename(
    columns={
        "Regiao - Sigla": "regiao",
        "Estado - Sigla": "uf",
        "Municipio": "municipio",
        "Revenda": "revenda",
        "CNPJ da Revenda": "cnpj",
        "Nome da Rua": "rua",
        "Numero Rua": "numero",
        "Bairro": "bairro",
        "Cep": "cep",
        "Produto": "produto",
        "Data da Coleta": "data_coleta",
        "Valor de Venda": "valor_venda",
        "Unidade de Medida": "unidade_medida",
        "Bandeira": "bandeira",
    }
)


# ============================================================
# TRATAR CAMPOS DE TEXTO
# ============================================================

colunas_texto = [
    "regiao",
    "uf",
    "municipio",
    "revenda",
    "cnpj",
    "rua",
    "numero",
    "bairro",
    "cep",
    "produto",
    "unidade_medida",
    "bandeira",
]

for coluna in colunas_texto:
    if coluna in df.columns:
        df[coluna] = df[coluna].astype("string").str.strip()


# ============================================================
# CONVERTER DATA
# ============================================================

df["data_coleta"] = pd.to_datetime(
    df["data_coleta"],
    format="%d/%m/%Y",
    errors="coerce"
)


# ============================================================
# VALIDAÇÃO DO PREÇO
# ============================================================

df["valor_venda"] = pd.to_numeric(
    df["valor_venda"],
    errors="coerce"
)

precos_invalidos = (
    df["valor_venda"].isna()
    | (df["valor_venda"] <= 0)
)

quantidade_invalidos = precos_invalidos.sum()

print(
    f"Preços inválidos encontrados: "
    f"{quantidade_invalidos:,}"
)

df = df[~precos_invalidos].copy()


# ============================================================
# CRIAR DIRETÓRIO PROCESSED
# ============================================================

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SALVAR DADOS PROCESSADOS
# ============================================================

arquivo_saida = (
    PROCESSED_DIR
    / "anp_gasolina_etanol_processed.csv"
)

df.to_csv(
    arquivo_saida,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# RESULTADO
# ============================================================

print("\nTransformação concluída!")

print(f"Registros finais: {len(df):,}")
print(f"Colunas finais: {len(df.columns)}")

print(f"\nArquivo salvo em:")
print(arquivo_saida)

print("\nTipos finais:")
print(df.dtypes)