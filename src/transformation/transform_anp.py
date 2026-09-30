from pathlib import Path

import pandas as pd


# ============================================================
# CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)


# ============================================================
# TRANSFORMAÇÃO
# ============================================================

def transformar_dados_anp(arquivo_raw=None):

    print("\n" + "=" * 60)
    print("RADAR COMBUSTÍVEL - TRANSFORMAÇÃO")
    print("=" * 60)

    # --------------------------------------------------------
    # Localizar arquivo
    # --------------------------------------------------------

    if arquivo_raw is None:

        arquivos = list(
            RAW_DIR.glob(
                "anp_gasolina_etanol_*.csv"
            )
        )

        if not arquivos:
            raise FileNotFoundError(
                "Nenhum arquivo da ANP encontrado "
                "em data/raw/"
            )

        arquivo_raw = max(
            arquivos,
            key=lambda arquivo: arquivo.stat().st_mtime
        )

    arquivo_raw = Path(arquivo_raw)

    print(
        f"\nArquivo utilizado: "
        f"{arquivo_raw.name}"
    )


    # --------------------------------------------------------
    # Carregar dados
    # --------------------------------------------------------

    df = pd.read_csv(
        arquivo_raw,
        sep=";",
        encoding="utf-8-sig",
        decimal=",",
        low_memory=False
    )

    print(
        f"\nRegistros recebidos: "
        f"{len(df):,}"
    )


    # --------------------------------------------------------
    # Remover colunas
    # --------------------------------------------------------

    colunas_remover = [
        "Valor de Compra",
        "Complemento"
    ]

    df = df.drop(
        columns=colunas_remover,
        errors="ignore"
    )


    # --------------------------------------------------------
    # Renomear colunas
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Tratar textos
    # --------------------------------------------------------

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

            df[coluna] = (
                df[coluna]
                .astype("string")
                .str.strip()
            )


    # --------------------------------------------------------
    # Converter data
    # --------------------------------------------------------

    df["data_coleta"] = pd.to_datetime(
        df["data_coleta"],
        format="%d/%m/%Y",
        errors="coerce"
    )


    # --------------------------------------------------------
    # Validar preços
    # --------------------------------------------------------

    df["valor_venda"] = pd.to_numeric(
        df["valor_venda"],
        errors="coerce"
    )

    precos_invalidos = (
        df["valor_venda"].isna()
        | (df["valor_venda"] <= 0)
    )

    quantidade_invalidos = (
        precos_invalidos.sum()
    )

    print(
        f"Preços inválidos encontrados: "
        f"{quantidade_invalidos:,}"
    )

    df = df[
        ~precos_invalidos
    ].copy()


    # --------------------------------------------------------
    # Salvar processed
    # --------------------------------------------------------

    PROCESSED_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    arquivo_saida = (
        PROCESSED_DIR
        / "anp_gasolina_etanol_processed.csv"
    )

    df.to_csv(
        arquivo_saida,
        index=False,
        encoding="utf-8-sig"
    )


    print("\nTransformação concluída!")

    print(
        f"Registros finais: {len(df):,}"
    )

    print(
        f"Colunas finais: {len(df.columns)}"
    )

    print(
        f"\nArquivo salvo em:\n"
        f"{arquivo_saida}"
    )

    return arquivo_saida


# ============================================================
# EXECUÇÃO DIRETA
# ============================================================

if __name__ == "__main__":
    transformar_dados_anp()