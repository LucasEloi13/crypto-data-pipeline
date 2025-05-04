"""
logging_config.py

Este módulo define uma função utilitária para configurar loggers personalizados,
permitindo rastreamento e depuração de diferentes partes do pipeline de dados.

Funções:
- setup_logger: Cria e retorna um logger configurado para escrever logs em um arquivo específico.

Exemplo de uso:
    from logging_config import setup_logger
    logger = setup_logger("extract", "logs/pipeline.log")
    logger.info("Mensagem de log")
"""
import logging
import os

def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger