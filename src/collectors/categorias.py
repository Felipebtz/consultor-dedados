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
    
    def build_payload(self, pagina: int = 1, registros_por_pagina: int = 200, **kwargs) -> Dict[str, Any]:
        """
        Constrói o payload conforme documentação oficial da API Omie.
        https://app.omie.com.br/api/v1/geral/categorias/
        """
        return {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina
        }
