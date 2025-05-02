import logging
from db import get_db_pool
from etl import CryptoETL

def main():
    logging.basicConfig(
        filename="pipeline/logs/pipeline.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("Iniciando pipeline...")

    etl = CryptoETL()
    try:
        raw_data = etl.extract()
        crypto_dim, market_data = etl.transform(raw_data)
        pool = get_db_pool()
        etl.load(pool, crypto_dim, market_data)

        logging.info("Pipeline finalizada com sucesso.")

    except Exception as e:
        logging.error(f"Erro na execução da pipeline: {e}")

if __name__ == "__main__":
    main()


