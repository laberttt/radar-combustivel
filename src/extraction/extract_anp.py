from pathlib import Path
from datetime import datetime

import requests


# ============================================================
# CONFIGURAÇÕES
# ============================================================

URL_ANP = (
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/"
    "dados-abertos/arquivos/shpc/qus/"
    "ultimas-4-semanas-gasolina-etanol.csv"
)


# ============================================================
# DIRETÓRIOS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"

RAW_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# EXTRAÇÃO
# ============================================================

def baixar_dados_anp():
    """
    Faz o download dos dados das últimas quatro semanas
    de Gasolina e Etanol disponibilizados pela ANP.

    O arquivo é salvo sem modificações na camada RAW.
    """

    print("=" * 60)
    print("FUELScope - Extração de dados da ANP")
    print("=" * 60)

    print("\nIniciando download...")

    try:

        response = requests.get(
            URL_ANP,
            timeout=30,
            headers={
                "User-Agent": "FuelScope/0.1"
            }
        )

        response.raise_for_status()

    except requests.RequestException as erro:

        print("\nErro ao baixar os dados da ANP:")
        print(erro)

        return

    # Data/hora da extração
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    nome_arquivo = (
        f"anp_gasolina_etanol_{timestamp}.csv"
    )

    caminho_arquivo = RAW_DIR / nome_arquivo

    # Salva exatamente os bytes recebidos da ANP
    caminho_arquivo.write_bytes(
        response.content
    )

    tamanho_mb = (
        caminho_arquivo.stat().st_size
        / 1024
        / 1024
    )

    print("\nDownload concluído!")

    print(
        f"Arquivo: {nome_arquivo}"
    )

    print(
        f"Local: {caminho_arquivo}"
    )

    print(
        f"Tamanho: {tamanho_mb:.2f} MB"
    )

    print("\nDados RAW armazenados com sucesso.")
    
    return caminho_arquivo


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    baixar_dados_anp()
    
    
