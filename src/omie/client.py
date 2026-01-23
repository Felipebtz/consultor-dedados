"""
Cliente HTTP para comunicação com a API Omie.
"""
import requests
import time
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.core.interfaces import IApiClient
from src.config import OmieSettings
from src.omie.auth import OmieAuthenticator
import logging

logger = logging.getLogger(__name__)


class OmieApiClient(IApiClient):
    """
    Cliente HTTP para comunicação com a API Omie.
    Implementa retry automático e tratamento de erros.
    """
    
    def __init__(self, settings: OmieSettings):
        """
        Inicializa o cliente da API.
        
        Args:
            settings: Configurações da API Omie
        """
        self.settings = settings
        self.authenticator = OmieAuthenticator(settings)
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Cria uma sessão HTTP com configurações de retry.
        
        Returns:
            Sessão HTTP configurada
        """
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.settings.MAX_RETRIES,
            backoff_factor=self.settings.RETRY_DELAY,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    def request(
        self, 
        endpoint: str, 
        method: str, 
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executa uma requisição à API Omie.
        
        Args:
            endpoint: Endpoint da API (ex: 'geral/clientes/')
            method: Método da API (ex: 'ListarClientes')
            payload: Payload da requisição
            
        Returns:
            Resposta da API como dicionário
            
        Raises:
            requests.RequestException: Em caso de erro na requisição
        """
        url = f"{self.settings.BASE_URL}/{endpoint}"
        
        # Constrói o payload completo
        full_payload = self.authenticator.build_payload(method, payload)
        
        try:
            start_time = time.time()
            
            # Adiciona delay antes da requisição para evitar rate limiting
            # Delay maior para extrato (pode ser mais lento)
            if "extrato" in endpoint.lower():
                time.sleep(1.0)  # 1 segundo para extrato
            else:
                time.sleep(0.3)  # 300ms para outras APIs
            
            response = self.session.post(
                url,
                json=full_payload,
                timeout=self.settings.TIMEOUT,
                headers={"Content-Type": "application/json"}
            )
            elapsed_time = time.time() - start_time
            
            # Se recebeu erro 500, aguarda mais tempo antes de retry
            if response.status_code == 500:
                wait_time = 5 if "extrato" in endpoint.lower() else 2
                logger.warning(f"Erro 500 recebido, aguardando {wait_time}s antes de retry...")
                time.sleep(wait_time)
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(
                f"API Request: {endpoint}/{method} - "
                f"Status: {response.status_code} - "
                f"Time: {elapsed_time:.2f}s"
            )
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição {endpoint}/{method}: {str(e)}")
            # Se for erro 500, aguarda mais tempo antes de retry
            if "500" in str(e) or "too many 500" in str(e).lower():
                logger.warning("Muitos erros 500 detectados. Aguardando 5s antes de continuar...")
                time.sleep(5)
            raise
    
    def close(self):
        """Fecha a sessão HTTP."""
        self.session.close()
