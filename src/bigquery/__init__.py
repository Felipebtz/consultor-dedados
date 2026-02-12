"""
Módulo BigQuery: cargas e consultas diretas (substitui MySQL quando GCP configurado).
"""
from src.bigquery.manager import BigQueryManager

__all__ = ["BigQueryManager"]
