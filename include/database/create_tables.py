"""
Script de Criação de Tabelas - Staging Area (MySQL) e Data Warehouse (PostgreSQL)

Este script define e cria as seguintes tabelas:
-------------------------------------------------
Staging Area (MySQL):
- crypto_raw: armazena os dados brutos extraídos da API CoinCap.

Data Warehouse (PostgreSQL):
- cryptocurrencies: dimensão de criptomoedas com metadados.
- crypto_market_data: fatos com dados de mercado vinculados às moedas.
- crypto_powerbi_summary: visão agregada dos dados para consumo via Power BI.

Características:
- Usa SQLAlchemy para abstração da criação das tabelas.
- Criação automática de campos com timestamp.
- Relacionamento entre dimensão e fato no DW via chave estrangeira.
"""

from sqlalchemy import MetaData, Table, Column, String, Text, DECIMAL, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.mysql import DATETIME as MYSQL_DATETIME
from sqlalchemy.sql import text
from db_connection import get_staging_area_engine, get_dw_engine
from config.logging_config import setup_logger

logger = setup_logger("create_tables", "logs/pipeline.log")

def create_staging_tables():
    logger.info("🔧 Criando tabelas da Staging Area...")
    engine = get_staging_area_engine()
    metadata = MetaData()

    crypto_raw = Table(
        "crypto_raw", metadata,
        Column("id", String(100), primary_key=True),
        Column("symbol", String(10)),
        Column("name", String(100)),
        Column("max_supply", DECIMAL(30, 10)),
        Column("explorer", Text),
        Column("price_usd", DECIMAL(30, 10)),
        Column("market_cap_usd", DECIMAL(30, 10)),
        Column("volume_usd_24hr", DECIMAL(30, 10)),
        Column("change_percent_24hr", DECIMAL(30, 10)),
        Column("vwap_24hr", DECIMAL(30, 10)),
        Column("supply", DECIMAL(30, 10)),
        Column("timestamp", MYSQL_DATETIME(fsp=6))
    )

    metadata.create_all(engine)
    logger.info("✅ Tabelas da Staging Area criadas com sucesso")


def create_dw_tables():
    logger.info("🔧 Criando tabelas do Data Warehouse...")
    engine = get_dw_engine()
    metadata = MetaData()

    cryptocurrencies = Table(
        "cryptocurrencies", metadata,
        Column("id", String(100), primary_key=True),
        Column("symbol", String(10)),
        Column("name", String(100)),
        Column("max_supply", DECIMAL(30, 10)),
        Column("explorer", Text),
        Column("created_at", MYSQL_DATETIME(fsp=6), server_default=text("CURRENT_TIMESTAMP"))
    )

    crypto_market_data = Table(
        "crypto_market_data", metadata,
        Column("id", String(100), ForeignKey("cryptocurrencies.id")),
        Column("price_usd", DECIMAL(30, 10)),
        Column("market_cap_usd", DECIMAL(30, 10)),
        Column("volume_usd_24hr", DECIMAL(30, 10)),
        Column("change_percent_24hr", DECIMAL(30, 10)),
        Column("vwap_24hr", DECIMAL(30, 10)),
        Column("supply", DECIMAL(30, 10)),
        Column("timestamp", MYSQL_DATETIME(fsp=6))
    )

    crypto_powerbi_summary = Table(
        "crypto_powerbi_summary", metadata,
        Column("id", String(100)),
        Column("rank", Integer),
        Column("symbol", String(10)),
        Column("supply", DECIMAL(30, 10)),
        Column("price_usd", DECIMAL(30, 10)),
        Column("updated_at", MYSQL_DATETIME(fsp=6))
    )

    metadata.create_all(engine)
    logger.info("✅ Tabelas do DW criadas com sucesso")


if __name__ == "__main__":
    try:
        create_staging_tables()
        create_dw_tables()
        logger.info("🚀 Todas as tabelas foram criadas com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {str(e)}")
        raise
