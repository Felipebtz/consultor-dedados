"""
Configurações do sistema usando Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class GcpSettings(BaseSettings):
    """Configurações Google Cloud (BigQuery e GCS)."""
    # Caminho absoluto do JSON da service account (BigQuery + GCS)
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    # Bucket GCS (ex.: gscbronze)
    GCS_BUCKET: str = "gscbronze"
    # BigQuery: projeto e dataset (.env: GCP_PROJECT_ID, BIGQUERY_DATASET)
    GCP_PROJECT_ID: Optional[str] = None
    BIGQUERY_DATASET: Optional[str] = None
    BQ_PROJECT: Optional[str] = None  # alias
    BQ_DATASET: Optional[str] = None  # alias

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

    @property
    def project_id(self) -> Optional[str]:
        return self.GCP_PROJECT_ID or self.BQ_PROJECT

    @property
    def dataset_id(self) -> Optional[str]:
        return self.BIGQUERY_DATASET or self.BQ_DATASET


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
    RETRY_DELAY: int = 5  # Aumentado para 5 segundos entre retries
    # Extrato: obrigatório informar um dos dois para a coleta de extrato funcionar (evita zerado)
    EXTRATO_CONTA_CORRENTE: Optional[int] = None  # nCodCC - código da conta no Omie (Financeiro > Contas Correntes)
    EXTRATO_CONTA_CORRENTE_INTEGRACAO: Optional[str] = None  # cCodIntCC - código de integração da conta

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class Settings:
    """Classe principal de configurações."""
    
    def __init__(self):
        self.database = DatabaseSettings()
        self.omie = OmieSettings()
        self.gcp = GcpSettings()
