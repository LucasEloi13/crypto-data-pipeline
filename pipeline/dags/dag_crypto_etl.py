from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys
import subprocess

# Caminho até o script que você quer executar
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), '..', 'src', 'run.py')

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

def executar_script():
    subprocess.run(['python', SCRIPT_PATH], check=True)

with DAG(
    dag_id='executar_script_run',
    default_args=default_args,
    description='Executa run.py a cada 5 minutos',
    schedule_interval='*/5 * * * *',
    start_date=datetime(2025, 4, 30),
    catchup=False,
    tags=['etl', 'script'],
) as dag:

    rodar_script = PythonOperator(
        task_id='executar_run_py',
        python_callable=executar_script
    )

    rodar_script
