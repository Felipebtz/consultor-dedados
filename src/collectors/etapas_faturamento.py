"""
Coletor de dados de Etapas de Faturamento (Omie).
Resposta em cadastros; explode etapas (uma linha por etapa).
"""
from typing import Dict, Any, List
from src.collectors.base import BaseCollector
import logging

logger = logging.getLogger(__name__)


def _get(d: dict, key: str, default=None):
    if not isinstance(d, dict):
        return default
    return d.get(key, default)


class EtapasFaturamentoCollector(BaseCollector):
    """Coletor para Etapas de Faturamento (produtos/etapafat/). Uma linha por etapa."""

    def get_endpoint(self) -> str:
        return "produtos/etapafat/"

    def get_method(self) -> str:
        return "ListarEtapasFaturamento"

    def get_table_name(self) -> str:
        return "etapas_faturamento"

    def get_schema(self) -> Dict[str, str]:
        return {
            "id": "BIGINT AUTO_INCREMENT PRIMARY KEY",
            "cod_operacao": "VARCHAR(20)",
            "de_operacao": "VARCHAR(255)",
            "cod_etapa_faturamento": "VARCHAR(50)",
            "de_padrao": "VARCHAR(255)",
            "de_etapa_faturamento": "VARCHAR(255)",
            "fl_inativo": "CHAR(1)",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
        }

    def build_payload(self, pagina: int = 1, registros_por_pagina: int = 200, **kwargs) -> Dict[str, Any]:
        return {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
        }

    def transform_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai cadastros e explode etapas (uma linha por etapa)."""
        rows = raw_data.get("cadastros")
        if not rows:
            return super().transform_data(raw_data)
        if isinstance(rows, dict):
            rows = [rows]
        out = []
        for item in rows:
            etapas = item.get("etapas") or []
            if not etapas:
                continue
            for eta in etapas:
                if not isinstance(eta, dict):
                    continue
                row = {
                    "cod_operacao": str(_get(eta, "cCodOperacao") or ""),
                    "de_operacao": str(_get(eta, "cDescOperacao") or "")[:255],
                    "cod_etapa_faturamento": str(_get(eta, "cCodigo") or ""),
                    "de_padrao": str(_get(eta, "cDescrPadrao") or "")[:255],
                    "de_etapa_faturamento": str(_get(eta, "cDescricao") or "")[:255],
                    "fl_inativo": str(_get(eta, "cInativo") or "N")[:1],
                }
                out.append(row)
        return out
