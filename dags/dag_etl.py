from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from include.etl.extract import extract_data
from include.etl.load_staging import load_data_to_staging
from include.etl.transform_load_final import transform_and_load_data


with DAG(
    dag_id='dag_etl_pipeline',
    schedule='*/5 * * * *',
    start_date=datetime(2025, 5, 3),
    catchup=False,
    tags=['crypto', 'etl', 'modular'],
    doc_md="""
    ### Pipeline de ETL para dados de criptomoedas

    Esta DAG extrai dados da API CoinCap, carrega-os em uma tabela de staging MySQL,
    transforma os dados e os carrega em tabelas dimensionais e de fatos no PostgreSQL.
    """,
) as dag:
    extract_task = PythonOperator(
        task_id='extract_from_api',
        python_callable=extract_data,
    )

    load_staging_task = PythonOperator(
        task_id='load_to_staging',
        python_callable=load_data_to_staging,
        op_args=[extract_task.output],  # Passa o resultado da extração para a carga
    )

    transform_load_final_task = PythonOperator(
        task_id='transform_and_load_final',
        python_callable=transform_and_load_data,
    )

    extract_task >> load_staging_task >> transform_load_final_task