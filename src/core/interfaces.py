"""
Interfaces (Protocols) seguindo o princípio de Interface Segregation (SOLID).
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime


class IApiClient(ABC):
    """Interface para cliente de API."""
    
    @abstractmethod
    def request(self, endpoint: str, method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executa uma requisição à API."""
        pass


class IDataCollector(ABC):
    """Interface para coletores de dados."""
    
    @abstractmethod
    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """Coleta dados da API."""
        pass
    
    @abstractmethod
    def get_endpoint(self) -> str:
        """Retorna o endpoint da API."""
        pass
    
    @abstractmethod
    def get_method(self) -> str:
        """Retorna o método da API."""
        pass


class IDatabaseManager(ABC):
    """Interface para gerenciador de banco de dados."""
    
    @abstractmethod
    def create_table(self, table_name: str, schema: Dict[str, str]) -> bool:
        """Cria uma tabela no banco de dados."""
        pass
    
    @abstractmethod
    def insert_batch(self, table_name: str, data: List[Dict[str, Any]]) -> int:
        """Insere dados em lote."""
        pass
    
    @abstractmethod
    def execute_query(self, query: str, params: Optional[Dict] = None) -> Any:
        """Executa uma query SQL."""
        pass


class IMetricsCollector(ABC):
    """Interface para coletor de métricas."""
    
    @abstractmethod
    def start_timer(self, operation: str) -> str:
        """Inicia um timer para uma operação."""
        pass
    
    @abstractmethod
    def stop_timer(self, timer_id: str) -> float:
        """Para um timer e retorna o tempo decorrido."""
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna todas as métricas coletadas."""
        pass
