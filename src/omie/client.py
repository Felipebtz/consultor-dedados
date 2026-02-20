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
        
        # Não retry em 500: API Omie costuma devolver 500 estável (ex.: módulo desativado); falha na 1ª.
        retry_strategy = Retry(
            total=self.settings.MAX_RETRIES,
            backoff_factor=self.settings.RETRY_DELAY,
            status_forcelist=[429, 502, 503, 504],
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
        # Garante barra final no path (evita 301 redirect na Omie); method vai no body (call).
        path = endpoint.rstrip("/") + "/"
        url = f"{self.settings.BASE_URL}/{path}"
        
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
            
            # Pedidos de compra: API Omie pode demorar (ex.: nbronze usa timeout=120)
            timeout = 120 if "pedidocompra" in endpoint.lower() else self.settings.TIMEOUT
            response = self.session.post(
                url,
                json=full_payload,
                timeout=timeout,
                headers={"Content-Type": "application/json"}
            )
            elapsed_time = time.time() - start_time

            if response.status_code >= 400:
                try:
                    body = response.json()
                    msg = body.get("faultstring") or body.get("message") or str(body)[:500]
                except Exception:
                    msg = response.text[:500] if response.text else "(sem corpo)"
                logger.error(
                    f"Omie API {response.status_code}: endpoint={endpoint} call={method} - {msg}"
                )

            response.raise_for_status()
            result = response.json()
            
            logger.info(
                f"API Request: endpoint={endpoint} call={method} - "
                f"Status: {response.status_code} - Time: {elapsed_time:.2f}s"
            )
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição endpoint={endpoint} call={method}: {str(e)}")
            raise
    
    def close(self):
        """Fecha a sessão HTTP."""
        self.session.close()
