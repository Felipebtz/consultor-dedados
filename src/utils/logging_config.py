"""
Configuração de logging para o sistema.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    level: int = logging.INFO,
    log_file: str = None,
    console: bool = True
):
    """
    Configura o sistema de logging.
    
    Args:
        level: Nível de logging (logging.INFO, logging.DEBUG, etc.)
        log_file: Caminho do arquivo de log (opcional)
        console: Se True, também exibe logs no console
    """
    # Formato das mensagens
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para console
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)
    
    # Handler para arquivo (se especificado)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)
    
    # Configura nível raiz
    logging.getLogger().setLevel(level)
    
    # Reduz verbosidade de algumas bibliotecas
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("mysql.connector").setLevel(logging.WARNING)
