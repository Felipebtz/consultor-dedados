"""
Coletor de dados de Categorias.
"""
from typing import Dict, Any
from src.collectors.base import BaseCollector


class CategoriasCollector(BaseCollector):
    """Coletor para dados de categorias."""
    
    def get_endpoint(self) -> str:
        return "geral/categorias/"
    
    def get_method(self) -> str:
        return "ListarCategorias"
    
    def get_table_name(self) -> str:
        return "categorias"
    
    def get_schema(self) -> Dict[str, str]:
        return {
            "codigo_categoria": "VARCHAR(50) PRIMARY KEY",
            "nome_categoria": "VARCHAR(255)",
            "descricao": "TEXT",
            "categoria_pai": "VARCHAR(50)",
            "inativo": "CHAR(1)",
            "data_cadastro": "DATETIME",
            "data_alteracao": "DATETIME",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        }
    
    def supports_incremental(self) -> bool:
        return True

    def build_payload(self, pagina: int = 1, registros_por_pagina: int = 200, **kwargs) -> Dict[str, Any]:
        """
        Constrói o payload conforme documentação oficial da API Omie.
        Em modo incremental: filtrar_por_data_de, filtrar_por_data_ate, filtrar_apenas_alteracao.
        """
        payload = {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina
        }
        if kwargs.get("incremental") and kwargs.get("data_inicio") and kwargs.get("data_fim"):
            payload["filtrar_por_data_de"] = kwargs["data_inicio"]
            payload["filtrar_por_data_ate"] = kwargs["data_fim"]
            payload["filtrar_apenas_alteracao"] = "S"
        return payload
