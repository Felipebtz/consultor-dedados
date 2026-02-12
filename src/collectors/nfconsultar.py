"""
Coletor de NF-e emitidas (listagem).
API: produtos/nfconsultar/ - ListarNF (listagem paginada; suporta filtro por data).
"""
from typing import Dict, Any, List
from src.collectors.base import BaseCollector
import logging

logger = logging.getLogger(__name__)


def _get(d: dict, key: str, default=None):
    if not isinstance(d, dict):
        return default
    return d.get(key, default)


class NfConsultarCollector(BaseCollector):
    """Coletor para listagem de NF-e (produtos/nfconsultar/)."""

    def get_endpoint(self) -> str:
        return "produtos/nfconsultar/"

    def get_method(self) -> str:
        return "ListarNF"

    def get_table_name(self) -> str:
        return "nf_consultar"

    def get_schema(self) -> Dict[str, str]:
        return {
            "id": "BIGINT AUTO_INCREMENT PRIMARY KEY",
            "numero": "VARCHAR(30)",
            "serie": "VARCHAR(10)",
            "data_emissao": "VARCHAR(20)",
            "cod_cliente": "VARCHAR(30)",
            "valor_total": "DECIMAL(18,2)",
            "situacao": "VARCHAR(30)",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        }

    def supports_incremental(self) -> bool:
        return True

    def build_payload(
        self,
        pagina: int = 1,
        registros_por_pagina: int = 200,
        **kwargs
    ) -> Dict[str, Any]:
        """Payload paginado (Omie usa nPagina/nRegPorPagina); em incremental adiciona filtrar_por_data_de/ate."""
        payload = {
            "nPagina": pagina,
            "nRegPorPagina": registros_por_pagina,
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
        }
        if kwargs.get("incremental") and kwargs.get("data_inicio") and kwargs.get("data_fim"):
            payload["filtrar_por_data_de"] = kwargs["data_inicio"]
            payload["filtrar_por_data_ate"] = kwargs["data_fim"]
            payload["filtrar_apenas_alteracao"] = "S"
        return payload

    def transform_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai lista de NF-e da resposta."""
        if raw_data.get("faultstring"):
            logger.warning(f"NF-e API retornou erro: {raw_data.get('faultstring')}. Chaves: {list(raw_data.keys())}")
            return []
        lista = (
            raw_data.get("listaNF")
            or raw_data.get("lista_nf")
            or raw_data.get("nf")
            or raw_data.get("cadastros")
            or raw_data.get("listaNotasFiscais")
        )
        if not lista:
            logger.info(
                f"NF-e: nenhuma lista encontrada (pode não haver NF-e emitidas). "
                f"Chaves da resposta: {list(raw_data.keys())}"
            )
            return super().transform_data(raw_data)
        if isinstance(lista, dict):
            lista = [lista]
        out = []
        for item in lista:
            if not isinstance(item, dict):
                continue
            out.append({
                "numero": str(_get(item, "nNumero") or _get(item, "numero") or "")[:30],
                "serie": str(_get(item, "cSerie") or _get(item, "serie") or "")[:10],
                "data_emissao": str(_get(item, "dDataEmissao") or _get(item, "data_emissao") or "")[:20],
                "cod_cliente": str(_get(item, "nCodCliente") or _get(item, "cod_cliente") or "")[:30],
                "valor_total": _get(item, "nValorTotal") or _get(item, "valor_total"),
                "situacao": str(_get(item, "cSituacao") or _get(item, "situacao") or "")[:30],
            })
        return out
