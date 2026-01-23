"""
Módulo core com interfaces e classes base.
"""
from src.core.interfaces import (
    IApiClient,
    IDataCollector,
    IDatabaseManager,
    IMetricsCollector
)

__all__ = [
    "IApiClient",
    "IDataCollector",
    "IDatabaseManager",
    "IMetricsCollector"
]
