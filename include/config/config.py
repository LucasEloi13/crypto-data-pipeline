import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# ======================
# CoinCap API Configuration
# ======================
COINCAP_API_KEY = os.getenv("COINCAP_API_KEY")
COINCAP_API_URL = os.getenv("COINCAP_API_URL")

# ======================
# MySQL Configuration (Staging)
# ======================
MYSQL_HOST = os.getenv("MYSQL_HOST", "mysql")
MYSQL_USER = os.getenv("MYSQL_USER", "user")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_DB = os.getenv("MYSQL_DB", "staging")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))

# ======================
# GCP Cloud SQL Configuration
# ======================
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_REGION = os.getenv("GCP_REGION")
GCP_INSTANCE_NAME = os.getenv("GCP_INSTANCE_NAME")
GCP_DB_NAME = os.getenv("GCP_DB_NAME")
GCP_DB_USER = os.getenv("GCP_DB_USER")
GCP_DB_PASSWORD = os.getenv("GCP_DB_PASSWORD")