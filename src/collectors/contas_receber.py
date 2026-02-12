"""
Coletor de dados de Contas a Receber.
API: financas/contareceber/ - ListarContasReceber (lcrListarRequest).
Payload: pagina, registros_por_pagina, apenas_importado_api; incremental: filtrar_por_data_de, filtrar_por_data_ate, filtrar_apenas_alteracao (datas em DD/MM/YYYY).
"""
from typing import Dict, Any
from src.collectors.base import BaseCollector


def _date_omie(d: str) -> str:
    """Converte YYYY-MM-DD para DD/MM/YYYY (formato Omie)."""
    if not d or len(d) < 10:
        return d
    try:
        parts = d[:10].split("-")
        if len(parts) == 3:
            return f"{parts[2]}/{parts[1]}/{parts[0]}"
    except Exception:
        pass
    return d


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
        pagina: int = 1,
        registros_por_pagina: int = 200,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Payload conforme lcrListarRequest (ListarContasReceber).
        Não usar data_vencimento_inicial/final (não existem na API).
        Incremental: filtrar_por_data_de, filtrar_por_data_ate (DD/MM/YYYY), filtrar_apenas_alteracao.
        """
        payload = {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": "N",
        }
        if kwargs.get("incremental") and kwargs.get("data_inicio") and kwargs.get("data_fim"):
            payload["filtrar_por_data_de"] = _date_omie(kwargs["data_inicio"])
            payload["filtrar_por_data_ate"] = _date_omie(kwargs["data_fim"])
            payload["filtrar_apenas_alteracao"] = "S"
        return payload
