from pathlib import Path

import pandas as pd


# ============================================================
# CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "anp_gasolina_etanol_processed.csv"
)


# ============================================================
# CARREGAR DADOS
# ============================================================

if not PROCESSED_FILE.exists():
    raise FileNotFoundError(
        "Arquivo processado não encontrado. "
        "Execute primeiro transform_anp.py"
    )


print("=" * 70)
print("RADAR COMBUSTÍVEL - ANÁLISE PARAÍBA / JOÃO PESSOA")
print("=" * 70)


df = pd.read_csv(
    PROCESSED_FILE,
    parse_dates=["data_coleta"]
)


print(f"\nRegistros carregados: {len(df):,}")


# ============================================================
# PERÍODO DOS DADOS
# ============================================================

data_inicial = df["data_coleta"].min()
data_final = df["data_coleta"].max()

print("\n" + "=" * 70)
print("PERÍODO ANALISADO")
print("=" * 70)

print(
    f"De {data_inicial.strftime('%d/%m/%Y')} "
    f"até {data_final.strftime('%d/%m/%Y')}"
)


# ============================================================
# PARAÍBA
# ============================================================

df_pb = df[
    df["uf"] == "PB"
].copy()


print("\n" + "=" * 70)
print("PARAÍBA")
print("=" * 70)

print(
    f"Registros encontrados: {len(df_pb):,}"
)

print(
    f"Municípios pesquisados: "
    f"{df_pb['municipio'].nunique()}"
)

print(
    f"Postos diferentes: "
    f"{df_pb['cnpj'].nunique()}"
)


# ============================================================
# ESTATÍSTICAS DA PARAÍBA
# ============================================================

estatisticas_pb = (
    df_pb
    .groupby("produto")["valor_venda"]
    .agg(
        quantidade="count",
        media="mean",
        mediana="median",
        minimo="min",
        maximo="max"
    )
    .round(3)
)


print("\n" + "=" * 70)
print("PREÇOS NA PARAÍBA")
print("=" * 70)

print(estatisticas_pb)


# ============================================================
# JOÃO PESSOA
# ============================================================

df_jp = df_pb[
    df_pb["municipio"] == "JOAO PESSOA"
].copy()


print("\n" + "=" * 70)
print("JOÃO PESSOA")
print("=" * 70)

print(
    f"Registros encontrados: {len(df_jp):,}"
)

print(
    f"Postos diferentes: "
    f"{df_jp['cnpj'].nunique()}"
)


# ============================================================
# ESTATÍSTICAS DE JOÃO PESSOA
# ============================================================

estatisticas_jp = (
    df_jp
    .groupby("produto")["valor_venda"]
    .agg(
        quantidade="count",
        media="mean",
        mediana="median",
        minimo="min",
        maximo="max"
    )
    .round(3)
)


print("\n" + "=" * 70)
print("PREÇOS EM JOÃO PESSOA")
print("=" * 70)

print(estatisticas_jp)


# ============================================================
# PREÇO MÉDIO POR DATA
# ============================================================

media_diaria_jp = (
    df_jp
    .groupby(
        ["data_coleta", "produto"]
    )["valor_venda"]
    .mean()
    .reset_index()
)


media_diaria_jp["valor_venda"] = (
    media_diaria_jp["valor_venda"]
    .round(3)
)


print("\n" + "=" * 70)
print("PREÇO MÉDIO POR DATA - JOÃO PESSOA")
print("=" * 70)

print(
    media_diaria_jp.to_string(
        index=False
    )
)


# ============================================================
# ÚLTIMO PREÇO REGISTRADO POR POSTO
# ============================================================

ultimos_precos = (
    df_jp
    .sort_values("data_coleta")
    .drop_duplicates(
        subset=["cnpj", "produto"],
        keep="last"
    )
)


# ============================================================
# POSTOS MAIS BARATOS
# ============================================================

print("\n" + "=" * 70)
print("POSTOS COM MENORES PREÇOS REGISTRADOS")
print("=" * 70)


for produto in sorted(
    ultimos_precos["produto"].dropna().unique()
):

    print(f"\n{produto}")
    print("-" * 70)

    resultado = (
        ultimos_precos[
            ultimos_precos["produto"] == produto
        ]
        .sort_values("valor_venda")
        [
            [
                "revenda",
                "bairro",
                "valor_venda",
                "data_coleta"
            ]
        ]
        .head(5)
        .copy()
    )

    resultado["data_coleta"] = (
        resultado["data_coleta"]
        .dt.strftime("%d/%m/%Y")
    )

    print(
        resultado.to_string(
            index=False
        )
    )