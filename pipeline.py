from datetime import datetime
import time

from src.extraction.extract_anp import baixar_dados_anp
from src.transformation.transform_anp import transformar_dados_anp
from src.load.load_postgres import carregar_postgres


def executar_pipeline():

    inicio = time.time()

    print("\n" + "=" * 70)
    print("RADAR COMBUSTÍVEL")
    print("PIPELINE ETL")
    print("=" * 70)

    print(
        "\nInício:",
        datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    )

    try:

        # =====================================================
        # 1. EXTRACT
        # =====================================================

        print("\n" + "=" * 70)
        print("[1/3] EXTRAÇÃO")
        print("=" * 70)

        arquivo_raw = baixar_dados_anp()

        if arquivo_raw is None:
            raise RuntimeError(
                "A etapa de extração não retornou um arquivo."
            )

        print(
            f"\nArquivo RAW recebido pelo pipeline:\n"
            f"{arquivo_raw}"
        )


        # =====================================================
        # 2. TRANSFORM
        # =====================================================

        print("\n" + "=" * 70)
        print("[2/3] TRANSFORMAÇÃO")
        print("=" * 70)

        arquivo_processado = transformar_dados_anp(
            arquivo_raw
        )

        if arquivo_processado is None:
            raise RuntimeError(
                "A etapa de transformação não retornou "
                "um arquivo."
            )

        print(
            f"\nArquivo processado recebido pelo pipeline:\n"
            f"{arquivo_processado}"
        )


        # =====================================================
        # 3. LOAD
        # =====================================================

        print("\n" + "=" * 70)
        print("[3/3] CARGA")
        print("=" * 70)

        total_registros = carregar_postgres(
            arquivo_processado
        )


        # =====================================================
        # FINALIZAÇÃO
        # =====================================================

        duracao = time.time() - inicio

        print("\n" + "=" * 70)
        print("PIPELINE CONCLUÍDO COM SUCESSO")
        print("=" * 70)

        print(
            f"\nRegistros no PostgreSQL: "
            f"{total_registros:,}"
        )

        print(
            f"Tempo total: {duracao:.2f} segundos"
        )

        print(
            "Finalizado em:",
            datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        )


    except Exception as erro:

        duracao = time.time() - inicio

        print("\n" + "=" * 70)
        print("ERRO DURANTE A EXECUÇÃO DO PIPELINE")
        print("=" * 70)

        print(f"\nTipo: {type(erro).__name__}")
        print(f"Erro: {erro}")

        print(
            f"\nPipeline interrompido após "
            f"{duracao:.2f} segundos."
        )

        raise


if __name__ == "__main__":
    executar_pipeline()