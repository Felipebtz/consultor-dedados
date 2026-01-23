"""
Coletor de dados de Contas a Pagar.
"""
from typing import Dict, Any
from src.collectors.base import BaseCollector


class ContasPagarCollector(BaseCollector):
    """Coletor para dados de contas a pagar."""
    
    def get_endpoint(self) -> str:
        return "financas/contapagar/"
    
    def get_method(self) -> str:
        return "ListarContasPagar"
    
    def get_table_name(self) -> str:
        return "contas_pagar"
    
    def get_schema(self) -> Dict[str, str]:
        return {
            "id": "BIGINT PRIMARY KEY AUTO_INCREMENT",
            "codigo_lancamento": "VARCHAR(50) UNIQUE",
            "codigo_lancamento_integracao": "VARCHAR(50)",
            "codigo_cliente_fornecedor": "VARCHAR(50)",
            "data_vencimento": "DATE",
            "data_emissao": "DATE",
            "valor_documento": "DECIMAL(15,2)",
            "valor_pago": "DECIMAL(15,2)",
            "saldo": "DECIMAL(15,2)",
            "status": "VARCHAR(50)",
            "numero_documento": "VARCHAR(50)",
            "numero_pedido": "VARCHAR(50)",
            "numero_parcela": "VARCHAR(10)",
            "observacao": "TEXT",
            "codigo_categoria": "VARCHAR(50)",
            "codigo_conta_corrente": "VARCHAR(50)",
            "codigo_projeto": "VARCHAR(50)",
            "data_previsao": "DATE",
            "data_baixa": "DATE",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        }
    
    def build_payload(
        self,
        data_inicio: str = None,
        data_fim: str = None,
        pagina: int = 1,
        registros_por_pagina: int = 20,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Constrói o payload conforme documentação oficial da API Omie.
        https://app.omie.com.br/api/v1/financas/contapagar/
        """
        payload = {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": "N"
        }
        
        if data_inicio:
            payload["data_vencimento_inicial"] = data_inicio
        if data_fim:
            payload["data_vencimento_final"] = data_fim
            
        return payload
