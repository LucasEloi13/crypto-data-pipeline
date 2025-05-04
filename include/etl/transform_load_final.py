"""
transform_load_final.py

Este módulo realiza a transformação dos dados extraídos e carregados na *staging area*,
preparando-os para inserção nas tabelas finais da camada de *Data Warehouse* (DW).
Ele executa UPSERTs para a dimensão de criptomoedas e INSERTs para a tabela de fatos.

Operações realizadas:
1. Leitura da tabela `crypto_raw` (staging - MySQL)
2. Transformação para:
   - Tabela dimensão: `cryptocurrencies`
   - Tabela de fatos: `crypto_market_data`
3. UPSERT na dimensão e INSERT nas tabelas de fatos
4. Atualização da tabela `crypto_powerbi_summary` via SQL nativo (para uso em dashboards Power BI)
"""
import datetime
from typing import List, Dict
from sqlalchemy import MetaData, select, text
from sqlalchemy.dialects.mysql import insert as mysql_insert
from include.database.db_connection import get_staging_area_engine, get_dw_engine
from include.config.logging_config import setup_logger

logger = setup_logger("transform_load_final", "logs/pipeline.log")

def transform_and_load_data():
    logger.info("🔧 Transformando e carregando dados para a camada final...")
    staging_area_engine = get_staging_area_engine()
    dw_engine = get_dw_engine()

    try:
        # 1. Obter dados do MySQL (staging)
        with staging_area_engine.connect() as mysql_conn:
            metadata = MetaData()
            metadata.reflect(bind=mysql_conn)
            raw_table = metadata.tables["crypto_raw"]
            result = mysql_conn.execute(select(raw_table)).mappings().all()

        if not result:
            logger.warning("⚠️ Nenhum dado encontrado no staging para transformar e carregar")
            return

        # 2. Transformar dados
        crypto_dim = []
        market_facts = []

        for row in result:
            crypto_dim.append({
                "id": row["id"],
                "symbol": row["symbol"],
                "name": row["name"],
                "max_supply": float(row["max_supply"]) if row["max_supply"] else None,
                "explorer": row["explorer"].split(",")[0] if row["explorer"] else None
            })

            market_facts.append({
                "id": row["id"],
                "price_usd": float(row["price_usd"]),
                "market_cap_usd": float(row["market_cap_usd"]),
                "volume_usd_24hr": float(row["volume_usd_24hr"]),
                "change_percent_24hr": float(row["change_percent_24hr"]),
                "vwap_24hr": float(row["vwap_24hr"]) if row["vwap_24hr"] else 0.0,
                "supply": float(row["supply"]),
                "timestamp": datetime.utcnow()
            })

        # 3. Carregar no MySQL (UPSERT para dimensão, INSERT para fatos)
        with dw_engine.begin() as mysql_conn:
            metadata = MetaData()
            metadata.reflect(bind=mysql_conn)

            # Para cryptocurrencies (UPSERT - substitui o on_conflict_do_update)
            crypto_table = metadata.tables["cryptocurrencies"]
            if crypto_dim:
                # Versão MySQL do UPSERT
                stmt = mysql_insert(crypto_table).values(crypto_dim)
                stmt = stmt.on_duplicate_key_update(
                    symbol=stmt.inserted.symbol,
                    name=stmt.inserted.name,
                    max_supply=stmt.inserted.max_supply,
                    explorer=stmt.inserted.explorer
                )
                mysql_conn.execute(stmt)
                logger.info(f"✅ Dimensão 'cryptocurrencies' carregada/atualizada ({len(crypto_dim)} registros)")

            # Para crypto_market_data (INSERT - permanece igual)
            market_table = metadata.tables["crypto_market_data"]
            if market_facts:
                mysql_conn.execute(market_table.insert(), market_facts)
                logger.info(f"✅ Tabela de fatos 'crypto_market_data' carregada ({len(market_facts)} registros)")

            # Atualiza a tabela do Power BI com SQL puro
            try:
                mysql_conn.execute(text("TRUNCATE TABLE crypto_powerbi_summary"))
                mysql_conn.execute(text("""
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
                logger.info("✅ Tabela 'crypto_powerbi_summary' atualizada com sucesso")
            except Exception as e:
                logger.error(f"❌ Erro ao atualizar a tabela 'crypto_powerbi_summary': {str(e)}")
                raise

        logger.info("✅ Transformação e carga final concluídas com sucesso")

    except Exception as e:
        logger.error(f"❌ Erro na transformação e carga final: {str(e)}")
        raise
