from pathlib import Path
import os

import pandas as pd
import psycopg

from dotenv import load_dotenv


# ============================================================
# CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_PROCESSED_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "anp_gasolina_etanol_processed.csv"
)

ENV_FILE = PROJECT_ROOT / ".env"


# ============================================================
# VARIÁVEIS DE AMBIENTE
# ============================================================

load_dotenv(ENV_FILE)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ============================================================
# FUNÇÃO DE CARGA
# ============================================================

def carregar_postgres(arquivo_processado=None):

    print("\n" + "=" * 60)
    print("RADAR COMBUSTÍVEL - CARGA POSTGRESQL")
    print("=" * 60)

    # --------------------------------------------------------
    # Definir arquivo processado
    # --------------------------------------------------------

    if arquivo_processado is None:
        arquivo_processado = DEFAULT_PROCESSED_FILE

    arquivo_processado = Path(arquivo_processado)


    # --------------------------------------------------------
    # Validar arquivo
    # --------------------------------------------------------

    if not arquivo_processado.exists():
        raise FileNotFoundError(
            "Arquivo processado não encontrado. "
            "Execute primeiro a transformação."
        )


    # --------------------------------------------------------
    # Validar variáveis do .env
    # --------------------------------------------------------

    variaveis_obrigatorias = {
        "DB_HOST": DB_HOST,
        "DB_PORT": DB_PORT,
        "DB_NAME": DB_NAME,
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD,
    }

    faltando = [
        nome
        for nome, valor in variaveis_obrigatorias.items()
        if not valor
    ]

    if faltando:
        raise ValueError(
            "Variáveis ausentes no .env: "
            + ", ".join(faltando)
        )


    # --------------------------------------------------------
    # Carregar CSV processado
    # --------------------------------------------------------

    print(
        f"\nArquivo utilizado: "
        f"{arquivo_processado.name}"
    )

    df = pd.read_csv(
        arquivo_processado,

        parse_dates=[
            "data_coleta"
        ],

        dtype={
            "regiao": "string",
            "uf": "string",
            "municipio": "string",
            "revenda": "string",
            "cnpj": "string",
            "rua": "string",
            "numero": "string",
            "bairro": "string",
            "cep": "string",
            "produto": "string",
            "unidade_medida": "string",
            "bandeira": "string",
        }
    )

    print(
        f"Registros encontrados no CSV: "
        f"{len(df):,}"
    )


    # --------------------------------------------------------
    # Conectar ao PostgreSQL
    # --------------------------------------------------------

    print("\nConectando ao PostgreSQL...")

    with psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    ) as conn:

        with conn.cursor() as cursor:

            print("Conexão realizada com sucesso!")


            # =================================================
            # FULL REFRESH
            # =================================================

            print(
                "\nLimpando dados anteriores da tabela..."
            )

            cursor.execute(
                """
                TRUNCATE TABLE precos_combustiveis
                RESTART IDENTITY;
                """
            )


            # =================================================
            # PREPARAR REGISTROS
            # =================================================

            registros = []

            for linha in df.itertuples(index=False):

                registros.append(
                    (
                        linha.regiao,
                        linha.uf,
                        linha.municipio,
                        linha.revenda,
                        linha.cnpj,

                        None
                        if pd.isna(linha.rua)
                        else linha.rua,

                        None
                        if pd.isna(linha.numero)
                        else linha.numero,

                        None
                        if pd.isna(linha.bairro)
                        else linha.bairro,

                        None
                        if pd.isna(linha.cep)
                        else linha.cep,

                        linha.produto,

                        linha.data_coleta.date(),

                        linha.valor_venda,

                        linha.unidade_medida,

                        None
                        if pd.isna(linha.bandeira)
                        else linha.bandeira,
                    )
                )


            # =================================================
            # INSERT
            # =================================================

            print("\nInserindo dados no PostgreSQL...")

            comando_insert = """
                INSERT INTO precos_combustiveis (
                    regiao,
                    uf,
                    municipio,
                    revenda,
                    cnpj,
                    rua,
                    numero,
                    bairro,
                    cep,
                    produto,
                    data_coleta,
                    valor_venda,
                    unidade_medida,
                    bandeira
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s
                );
            """

            cursor.executemany(
                comando_insert,
                registros
            )


            # =================================================
            # VALIDAR CARGA
            # =================================================

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM precos_combustiveis;
                """
            )

            total_banco = cursor.fetchone()[0]


    print("\nCarga concluída!")

    print(
        f"Registros inseridos: "
        f"{len(registros):,}"
    )

    print(
        f"Registros no banco: "
        f"{total_banco:,}"
    )

    return total_banco


# ============================================================
# EXECUÇÃO DIRETA
# ============================================================

if __name__ == "__main__":
    carregar_postgres()