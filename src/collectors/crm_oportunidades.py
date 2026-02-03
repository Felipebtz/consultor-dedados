"""
Coletor de dados de CRM Oportunidades (Omie).
Resposta em cadastros; flatten de identificacao e outrasInf.
"""
from typing import Dict, Any, List
from src.collectors.base import BaseCollector
import logging

logger = logging.getLogger(__name__)


def _get(d: dict, key: str, default=None):
    if not isinstance(d, dict):
        return default
    return d.get(key, default)


class CrmOportunidadesCollector(BaseCollector):
    """Coletor para CRM Oportunidades (crm/oportunidades/)."""

    def get_endpoint(self) -> str:
        return "crm/oportunidades/"

    def get_method(self) -> str:
        return "ListarOportunidades"

    def get_table_name(self) -> str:
        return "crm_oportunidades"

    def get_schema(self) -> Dict[str, str]:
        return {
            "id": "BIGINT AUTO_INCREMENT PRIMARY KEY",
            "codigo_oportunidade": "VARCHAR(50)",
            "codigo_interno": "VARCHAR(50)",
            "descricao_oportunidade": "VARCHAR(500)",
            "codigo_conta": "VARCHAR(50)",
            "codigo_vendedor": "VARCHAR(50)",
            "codigo_fase": "VARCHAR(20)",
            "data_inclusao": "VARCHAR(30)",
            "data_alteracao": "VARCHAR(30)",
            "ano_previsao": "INT",
            "mes_previsao": "INT",
            "valor_ticket": "DECIMAL(15,4)",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
        }

    def supports_incremental(self) -> bool:
        return True

    def build_payload(self, pagina: int = 1, registros_por_pagina: int = 200, **kwargs) -> Dict[str, Any]:
        payload = {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
        }
        if kwargs.get("incremental") and kwargs.get("data_inicio") and kwargs.get("data_fim"):
            payload["filtrar_por_data_de"] = kwargs["data_inicio"]
            payload["filtrar_por_data_ate"] = kwargs["data_fim"]
            payload["filtrar_apenas_alteracao"] = "S"
        return payload

    def transform_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai cadastros e achata identificacao, fasesStatus, previsaoTemp, ticket, outrasInf."""
        rows = raw_data.get("cadastros")
        if not rows:
            return super().transform_data(raw_data)
        if isinstance(rows, dict):
            rows = [rows]
        out = []
        for opp in rows:
            ident = _get(opp, "identificacao") or {}
            outras = _get(opp, "outrasInf") or {}
            fases = _get(opp, "fasesStatus") or {}
            previsao = _get(opp, "previsaoTemp") or {}
            ticket = _get(opp, "ticket") or {}
            row = {
                "codigo_oportunidade": str(_get(ident, "nCodOp") or ""),
                "codigo_interno": str(_get(ident, "cCodIntOp") or ""),
                "descricao_oportunidade": str(_get(ident, "cDesOp") or "")[:500],
                "codigo_conta": str(_get(ident, "nCodConta") or ""),
                "codigo_vendedor": str(_get(ident, "nCodVendedor") or ""),
                "codigo_fase": str(_get(fases, "nCodFase") or ""),
                "data_inclusao": str(_get(outras, "dInclusao") or ""),
                "data_alteracao": str(_get(outras, "dAlteracao") or ""),
                "ano_previsao": int(_get(previsao, "nAnoPrev") or 0) or None,
                "mes_previsao": int(_get(previsao, "nMesPrev") or 0) or None,
                "valor_ticket": _get(ticket, "nTicket") or None,
            }
            out.append(row)
        return out
