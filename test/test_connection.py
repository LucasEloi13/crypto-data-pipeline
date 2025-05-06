"""
test_connection.py

Este script tem como objetivo testar as conexões com os bancos de dados configurados
no projeto, tanto o banco local (Staging Area) quanto o banco em nuvem (Data Warehouse - GCP).

Uso:
    Este teste é útil para validar se as credenciais, variáveis de ambiente e 
    acesso de rede estão corretos antes de executar a ETL completa.

Importante:
    O script deve ser executado a partir da raiz do projeto ou com o PYTHONPATH ajustado.
"""

import os
import sys
import logging
from sqlalchemy import text
from include.database.db_connection import get_staging_area_engine, get_dw_engine
from include.config.logging_config import setup_logger
# Configuração do logger

logger = setup_logger("db_connection", "logs/connection.log")

def test_staging_connection():
    logger.info("🔄 Testando conexão com banco STAGING...")
    try:
        engine = get_staging_area_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            logger.info("✅ Conexão STAGING bem-sucedida.")
    except Exception as e:
        logger.error(f"❌ Erro ao conectar com STAGING: {e}")

def test_dw_connection():
    logger.info("🔄 Testando conexão com banco DW (Cloud SQL)...")
    try:
        engine = get_dw_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            logger.info("✅ Conexão DW bem-sucedida.")
    except Exception as e:
        logger.error(f"❌ Erro ao conectar com DW: {e}")

if __name__ == "__main__":
    logger.info("Iniciando testes de conexão com os bancos de dados...")
    test_staging_connection()
    test_dw_connection()
    logger.info("Testes de conexão finalizados. \n")
