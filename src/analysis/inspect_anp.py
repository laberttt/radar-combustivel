from pathlib import Path

import pandas as pd


# ============================================================
# CAMINHOS DO PROJETO
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"


# ============================================================
# LOCALIZAR ARQUIVO MAIS RECENTE
# ============================================================

arquivos = list(
    RAW_DIR.glob("anp_gasolina_etanol_*.csv")
)

if not arquivos:
    raise FileNotFoundError(
        "Nenhum arquivo da ANP foi encontrado em data/raw/"
    )

arquivo_mais_recente = max(
    arquivos,
    key=lambda arquivo: arquivo.stat().st_mtime
)

print("=" * 60)
print("RADAR COMBUSTÍVEL - EXPLORAÇÃO INICIAL")
print("=" * 60)

print(f"\nArquivo analisado:")
print(arquivo_mais_recente.name)


# ============================================================
# CARREGAMENTO
# ============================================================

df = pd.read_csv(
    arquivo_mais_recente,
    sep=";",
    encoding="utf-8-sig",
    decimal=",",
    low_memory=False
)


# ============================================================
# INFORMAÇÕES GERAIS
# ============================================================

print("\n" + "=" * 60)
print("DIMENSÕES DO DATASET")
print("=" * 60)

print(f"Linhas: {df.shape[0]:,}")
print(f"Colunas: {df.shape[1]}")


# ============================================================
# COLUNAS
# ============================================================

print("\n" + "=" * 60)
print("COLUNAS")
print("=" * 60)

for numero, coluna in enumerate(df.columns, start=1):
    print(f"{numero}. {coluna}")


# ============================================================
# TIPOS DOS DADOS
# ============================================================

print("\n" + "=" * 60)
print("TIPOS DOS DADOS")
print("=" * 60)

print(df.dtypes)


# ============================================================
# PRIMEIRAS LINHAS
# ============================================================

print("\n" + "=" * 60)
print("PRIMEIRAS 5 LINHAS")
print("=" * 60)

print(df.head())


# ============================================================
# VALORES NULOS
# ============================================================

print("\n" + "=" * 60)
print("VALORES NULOS")
print("=" * 60)

nulos = df.isnull().sum()

print(
    nulos[nulos > 0]
    .sort_values(ascending=False)
)


# ============================================================
# DUPLICADOS
# ============================================================

print("\n" + "=" * 60)
print("DUPLICADOS")
print("=" * 60)

print(
    f"Linhas duplicadas: {df.duplicated().sum():,}"
)


# ============================================================
# PRODUTOS
# ============================================================

if "Produto" in df.columns:

    print("\n" + "=" * 60)
    print("PRODUTOS ENCONTRADOS")
    print("=" * 60)

    print(
        df["Produto"]
        .value_counts(dropna=False)
    )


# ============================================================
# ESTADOS
# ============================================================

if "Estado - Sigla" in df.columns:

    print("\n" + "=" * 60)
    print("REGISTROS POR ESTADO")
    print("=" * 60)

    print(
        df["Estado - Sigla"]
        .value_counts()
        .sort_index()
    )