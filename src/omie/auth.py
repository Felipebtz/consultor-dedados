"""
Módulo de autenticação da API Omie.
"""
import hashlib
import time
from typing import Dict, Any
from src.config import OmieSettings


class OmieAuthenticator:
    """
    Gerencia a autenticação da API Omie.
    Implementa o padrão de autenticação requerido pela Omie.
    """
    
    def __init__(self, settings: OmieSettings):
        """
        Inicializa o autenticador.
        
        Args:
            settings: Configurações da API Omie
        """
        self.settings = settings
    
    def generate_auth_data(self) -> Dict[str, Any]:
        """
        Gera os dados de autenticação necessários para a API Omie.
        
        Returns:
            Dicionário com app_key, app_secret e timestamp
        """
        return {
            "app_key": self.settings.APP_KEY,
            "app_secret": self.settings.APP_SECRET
        }
    
    def build_payload(self, call: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constrói o payload completo para a requisição.
        
        Args:
            call: Nome do método da API
            params: Parâmetros específicos do método
            
        Returns:
            Payload completo formatado
        """
        return {
            "call": call,
            "app_key": self.settings.APP_KEY,
            "app_secret": self.settings.APP_SECRET,
            "param": [params]
        }
