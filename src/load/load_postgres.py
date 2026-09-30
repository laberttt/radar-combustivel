from pathlib import Path
import os

import pandas as pd
import psycopg

from dotenv import load_dotenv


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
# VALIDAÇÕES
# ============================================================

if not PROCESSED_FILE.exists():
    raise FileNotFoundError(
        "Arquivo processado não encontrado. "
        "Execute primeiro transform_anp.py."
    )


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


# ============================================================
# CARREGAR CSV
# ============================================================

print("=" * 60)
print("RADAR COMBUSTÍVEL - CARGA POSTGRESQL")
print("=" * 60)


df = pd.read_csv(
    PROCESSED_FILE,
    parse_dates=["data_coleta"]
)


print(f"\nRegistros encontrados no CSV: {len(df):,}")


# ============================================================
# CONECTAR AO POSTGRESQL
# ============================================================

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

        # ====================================================
        # VERIFICAR SE A TABELA JÁ POSSUI DADOS
        # ====================================================

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM precos_combustiveis;
            """
        )

        registros_existentes = cursor.fetchone()[0]

        if registros_existentes > 0:
            print(
                "\nCarga cancelada."
            )

            print(
                "A tabela precos_combustiveis já possui "
                f"{registros_existentes:,} registros."
            )

            print(
                "Isso evita inserir os mesmos dados novamente."
            )

        else:

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
                        linha.rua,
                        linha.numero,
                        linha.bairro,
                        linha.cep,
                        linha.produto,
                        linha.data_coleta.date(),
                        linha.valor_venda,
                        linha.unidade_medida,
                        linha.bandeira,
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
            # CONFIRMAR CARGA
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
                f"Registros inseridos: {len(registros):,}"
            )

            print(
                f"Registros no banco: {total_banco:,}"
            )