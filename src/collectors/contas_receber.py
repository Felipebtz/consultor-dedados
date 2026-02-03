"""
Coletor de dados de Contas a Receber.
"""
from typing import Dict, Any
from src.collectors.base import BaseCollector


class ContasReceberCollector(BaseCollector):
    """Coletor para dados de contas a receber."""

    def supports_incremental(self) -> bool:
        return True
    
    def get_endpoint(self) -> str:
        return "financas/contareceber/"
    
    def get_method(self) -> str:
        return "ListarContasReceber"
    
    def get_table_name(self) -> str:
        return "contas_receber"
    
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
        registros_por_pagina: int = 200,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Constrói o payload conforme documentação oficial da API Omie.
        https://app.omie.com.br/api/v1/financas/contareceber/
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
        if kwargs.get("incremental") and (data_inicio and data_fim):
            payload["filtrar_por_data_de"] = data_inicio
            payload["filtrar_por_data_ate"] = data_fim
            payload["filtrar_apenas_alteracao"] = "S"
        return payload
