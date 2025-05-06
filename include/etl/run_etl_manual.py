"""
run_etl_manual.py

Este módulo permite a execução manual da pipeline ETL de coleta, carga e transformação
de dados de criptomoedas da API CoinCap.

Utilização:
- Destinado a testes locais ou execuções pontuais da pipeline fora do Airflow.
- Executa as três etapas principais da ETL em sequência:
    1. Extração de dados da API.
    2. Carga na área de staging (tabela `crypto_raw`).
    3. Transformação e carga na área final (tabela `crypto_processed`).

Execução: 
    - PYTHONPATH=. python include/etl/run_etl_manual.py
"""

from extract import extract_data
from load_staging import load_data_to_staging
from transform_load_final import transform_and_load_data
from include.config.logging_config import setup_logger
import logging


def main():
    
    logger = setup_logger("etl_manual", "logs/pipeline.log")

    try:
        logger.info("Iniciando pipeline ETL manual")

        # Extração
        raw_data = extract_data()
       
        # Carga para staging
        load_data_to_staging(raw_data)
        
        # Transformação e carga final
        transform_and_load_data()

        logger.info("Pipeline ETL executada com sucesso \n")

    except Exception as e:
        logger.error(f"Erro durante a execução da pipeline manual: {str(e)}")

if __name__ == "__main__":
    main()
