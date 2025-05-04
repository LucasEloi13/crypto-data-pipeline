"""
extract.py

Este módulo é responsável por extrair dados da API CoinCap.

Funções:
- extract_data: Realiza uma requisição GET autenticada à API CoinCap e retorna os dados extraídos.

Requisitos:
- Variáveis de ambiente definidas em config.py:
    - COINCAP_API_KEY: Token de autenticação para a API CoinCap
    - COINCAP_API_URL: URL base da API CoinCap
"""

from typing import Dict, List
import requests
from include.config.config import COINCAP_API_KEY, COINCAP_API_URL
from include.config.logging_config import setup_logger

logger = setup_logger("extract", "logs/pipeline.log")

def extract_data() -> List[Dict]:
    logger.info("🔍 Extraindo dados da API CoinCap")
    headers = {"Authorization": f"Bearer {COINCAP_API_KEY}"}
    response = requests.get(COINCAP_API_URL, headers=headers)
    if response.status_code == 200:
        logger.info("✅ Extração concluída com sucesso")
        return response.json().get("data", [])
    else:
        raise Exception(f"❌ Erro na API: {response.status_code}: {response.text}")

