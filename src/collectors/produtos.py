"""
Coletor de dados de Produtos.
"""
from typing import Dict, Any
from src.collectors.base import BaseCollector


class ProdutosCollector(BaseCollector):
    """Coletor para dados de produtos."""
    
    def get_endpoint(self) -> str:
        return "geral/produtos/"
    
    def get_method(self) -> str:
        return "ListarProdutos"
    
    def get_table_name(self) -> str:
        return "produtos"
    
    def get_schema(self) -> Dict[str, str]:
        return {
            "codigo_produto": "VARCHAR(50) PRIMARY KEY",
            "codigo_produto_integracao": "VARCHAR(50)",
            "descricao": "VARCHAR(255)",
            "ncm": "VARCHAR(10)",
            "valor_unitario": "DECIMAL(15,2)",
            "unidade": "VARCHAR(10)",
            "tipo_item": "VARCHAR(20)",
            "categoria": "VARCHAR(100)",
            "peso_liq": "DECIMAL(10,3)",
            "peso_bruto": "DECIMAL(10,3)",
            "altura": "DECIMAL(10,3)",
            "largura": "DECIMAL(10,3)",
            "profundidade": "DECIMAL(10,3)",
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
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": "N",
            "filtrar_apenas_omiepdv": "N"
        }
        if kwargs.get("incremental") and kwargs.get("data_inicio") and kwargs.get("data_fim"):
            payload["filtrar_por_data_de"] = kwargs["data_inicio"]
            payload["filtrar_por_data_ate"] = kwargs["data_fim"]
            payload["filtrar_apenas_alteracao"] = "S"
        return payload
