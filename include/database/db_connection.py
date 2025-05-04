"""
db_connection.py

Este módulo contém funções para criar conexões com bancos de dados MySQL,
tanto locais quanto em nuvem (GCP Cloud SQL), utilizando SQLAlchemy e Cloud SQL Connector.

Funções:
- get_staging_area_engine: Cria engine para banco de dados MySQL local (staging area).
- get_dw_engine: Cria engine para banco de dados MySQL hospedado no GCP via Cloud SQL Connector.
"""

from google.cloud.sql.connector import Connector
from sqlalchemy import create_engine, text
from include.config.config import (
    MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT,
    GCP_PROJECT_ID, GCP_REGION, GCP_INSTANCE_NAME, GCP_DB_NAME, GCP_DB_USER, GCP_DB_PASSWORD
)
import logging

def get_staging_area_engine():
    """
    Retorna uma engine SQLAlchemy para conexão com o MySQL (staging area).
    Usa variáveis importadas do config.py
    """
    try:
        connection_string = (
            f"mysql+mysqlconnector://"
            f"{MYSQL_USER}:{MYSQL_PASSWORD}@"
            f"{MYSQL_HOST}:{MYSQL_PORT}/"
            f"{MYSQL_DB}"
        )
        engine = create_engine(connection_string, pool_pre_ping=True)
        logging.info("Conexão com MySQL estabelecida com sucesso.")
        return engine
    except Exception as e:
        logging.error(f"Erro ao conectar no MySQL: {e}")
        raise

def get_dw_engine():
    """
    Retorna uma Engine SQLAlchemy para Cloud SQL MySQL, usando Cloud SQL Connector.
    """
    try:
        # Configuração do Cloud SQL Connector (exatamente como no seu exemplo)
        connector = Connector()
        
        engine = create_engine(
            "mysql+pymysql://",
            creator=lambda: connector.connect(
               f"{GCP_PROJECT_ID}:{GCP_REGION}:{GCP_INSTANCE_NAME}", 
                "pymysql",
                user=GCP_DB_USER,
                password=GCP_DB_PASSWORD,
                db=GCP_DB_NAME
            ),
        )
        
        # Teste rápido da conexão
        with engine.connect() as conn:
            conn.execute(text("SELECT 1")) 
        
        logging.info("✅ Engine criada com sucesso (usando Cloud SQL Connector).")
        return engine

    except Exception as e:
        logging.error(f"❌ Falha ao criar a Engine: {e}")
        raise
