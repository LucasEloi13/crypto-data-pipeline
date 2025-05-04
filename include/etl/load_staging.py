"""
load_staging.py

Este módulo é responsável por carregar os dados extraídos da API CoinCap
para a tabela `crypto_raw` da área de staging no banco de dados MySQL.

Funções:
- load_data_to_staging: Insere ou atualiza os registros de criptomoedas na tabela staging.

Requisitos:
- A tabela `crypto_raw` deve existir no banco de dados MySQL.
- O módulo `db_connection` deve fornecer a engine com `get_staging_area_engine`.

Estratégia de inserção:
- Utiliza `ON DUPLICATE KEY UPDATE` para atualizar registros existentes
  com base na chave primária (geralmente o campo `id`).
"""

from datetime import datetime
from typing import Dict, List
from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.mysql import insert as mysql_insert
from include.database.db_connection import get_staging_area_engine
from include.config.logging_config import setup_logger

logger = setup_logger("load_staging", "logs/pipeline.log")

def load_data_to_staging(raw_data: List[Dict]):
    try:
        engine = get_staging_area_engine()
        metadata = MetaData()
        metadata.reflect(bind=engine, only=["crypto_raw"])
        raw_table = metadata.tables["crypto_raw"]

        with engine.begin() as conn:
            for asset in raw_data:
                data = {
                    "id": asset["id"],
                    "symbol": asset["symbol"],
                    "name": asset["name"],
                    "max_supply": float(asset["maxSupply"]) if asset["maxSupply"] else None,
                    "explorer": asset.get("explorer"),
                    "price_usd": float(asset["priceUsd"]),
                    "market_cap_usd": float(asset["marketCapUsd"]),
                    "volume_usd_24hr": float(asset["volumeUsd24Hr"]),
                    "change_percent_24hr": float(asset["changePercent24Hr"]),
                    "vwap_24hr": float(asset["vwap24Hr"]) if asset.get("vwap24Hr") else None,
                    "supply": float(asset["supply"]),
                    "timestamp": datetime.utcnow()
                }

                stmt = mysql_insert(raw_table).values(data)
                stmt = stmt.on_duplicate_key_update(
                    symbol=stmt.inserted.symbol,
                    name=stmt.inserted.name,
                    max_supply=stmt.inserted.max_supply,
                    explorer=stmt.inserted.explorer,
                    price_usd=stmt.inserted.price_usd,
                    market_cap_usd=stmt.inserted.market_cap_usd,
                    volume_usd_24hr=stmt.inserted.volume_usd_24hr,
                    change_percent_24hr=stmt.inserted.change_percent_24hr,
                    vwap_24hr=stmt.inserted.vwap_24hr,
                    supply=stmt.inserted.supply,
                    timestamp=stmt.inserted.timestamp
                )
                conn.execute(stmt)

            logger.info(f"✅ Dados carregados/atualizados ({len(raw_data)} registros) na staging")

    except Exception as e:
        logger.error(f"❌ Erro no carregamento para staging: {str(e)}")
        raise