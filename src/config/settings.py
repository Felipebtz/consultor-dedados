"""
Configurações do sistema usando Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class DatabaseSettings(BaseSettings):
    """Configurações do banco de dados MySQL."""
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "coleta_dados"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class OmieSettings(BaseSettings):
    """Configurações da API Omie."""
    APP_KEY: str
    APP_SECRET: str
    BASE_URL: str = "https://app.omie.com.br/api/v1"
    TIMEOUT: int = 30
    MAX_RETRIES: int = 5
    RETRY_DELAY: int = 5 # Aumentado para 5 segundos entre retries

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class Settings:
    """Classe principal de configurações."""
    
    def __init__(self):
        self.database = DatabaseSettings()
        self.omie = OmieSettings()
