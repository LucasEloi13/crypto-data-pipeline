import requests
from datetime import datetime
from typing import Tuple, List, Dict
from config import COINCAP_API_KEY, COINCAP_API_URL
from sqlalchemy import text
import logging
from sqlalchemy.dialects.mysql import insert as mysql_insert  # Import correto para MySQL


class CryptoETL:

    def extract(self) -> Dict:
        headers = {"Authorization": f"Bearer {COINCAP_API_KEY}"}
        response = requests.get(COINCAP_API_URL, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro na API: {response.status_code}: {response.text}")

    def transform(self, api_data: Dict) -> Tuple[List[Dict], List[Dict]]:
        crypto_dimension = []
        market_facts = []

        for asset in api_data.get("data", []):
            crypto_dim = {
                "id": asset.get("id"),
                "symbol": asset.get("symbol"),
                "name": asset.get("name"),
                "max_supply": float(asset["maxSupply"]) if asset.get("maxSupply") else None,
                "explorer": asset.get("explorer", "").split(",")[0] if asset.get("explorer") else None
            }
            crypto_dimension.append(crypto_dim)

            market_data = {
                "id": asset.get("id"),
                "price_usd": float(asset["priceUsd"]),
                "market_cap_usd": float(asset["marketCapUsd"]),
                "volume_usd_24hr": float(asset["volumeUsd24Hr"]),
                "change_percent_24hr": float(asset["changePercent24Hr"]),
                "vwap_24hr": float(asset["vwap24Hr"]) if asset["vwap24Hr"] else 0.0,
                "supply": float(asset["supply"]),
                "timestamp": datetime.utcnow()
            }
            market_facts.append(market_data)

        return crypto_dimension, market_facts

    def load(self, pool, crypto_dim, market_data):
        from sqlalchemy import MetaData, Table

        with pool.connect() as conn:
            metadata = MetaData()
            metadata.reflect(bind=conn)

            cryptocurrencies = Table("cryptocurrencies", metadata, autoload_with=conn)
            crypto_market_data = Table("crypto_market_data", metadata, autoload_with=conn)

            # 1. Upsert para cryptocurrencies (atualiza apenas se houver mudanças)
            if crypto_dim:
                stmt = mysql_insert(cryptocurrencies).values(crypto_dim)
                stmt = stmt.on_duplicate_key_update(
                    symbol=stmt.inserted.symbol,
                    name=stmt.inserted.name,
                    max_supply=stmt.inserted.max_supply,
                    explorer=stmt.inserted.explorer
                )
                conn.execute(stmt)

            # 2. Mantém inserções completas para market_data
            if market_data:
                conn.execute(crypto_market_data.insert(), market_data)

                

            # 3. Atualiza a tabela do Power BI com SQL puro
            conn.execute(text("TRUNCATE TABLE crypto_powerbi_summary"))
            conn.execute(text("""
                INSERT INTO crypto_powerbi_summary (id, `rank`, symbol, supply, price_usd, updated_at)
                SELECT
                    cmd.id,
                    RANK() OVER (ORDER BY cmd.price_usd DESC) AS `rank`,
                    c.symbol,
                    cmd.supply,
                    cmd.price_usd,
                    cmd.timestamp AS updated_at
                FROM crypto_market_data cmd
                JOIN cryptocurrencies c ON cmd.id = c.id
                WHERE cmd.timestamp = (
                    SELECT MAX(timestamp) FROM crypto_market_data
                )
            """))
            
            conn.commit()

        logging.info("Dados carregados com sucesso.")
