"""
Coletor de NFS-e emitidas.
API: servicos/nfse/ - ListarNFSEs (parâmetros: nPagina, nRegPorPagina, dEmiInicial, dEmiFinal).
"""
from typing import Dict, Any, List
from src.collectors.base import BaseCollector
import logging

logger = logging.getLogger(__name__)


def _get(d: dict, key: str, default=None):
    if not isinstance(d, dict):
        return default
    return d.get(key, default)


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


class NfseCollector(BaseCollector):
    """Coletor para listagem de NFS-e (servicos/nfse/)."""

    def get_endpoint(self) -> str:
        return "servicos/nfse/"

    def get_method(self) -> str:
        return "ListarNFSEs"

    def get_table_name(self) -> str:
        return "nfse"

    def get_schema(self) -> Dict[str, str]:
        return {
            "id": "BIGINT AUTO_INCREMENT PRIMARY KEY",
            "numero": "VARCHAR(30)",
            "codigo_nfse": "VARCHAR(50)",
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
        registros_por_pagina: int = 50,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Payload conforme documentação Omie: nPagina, nRegPorPagina, dEmiInicial, dEmiFinal (string DD/MM/YYYY).
        """
        data_inicio = kwargs.get("data_inicio", "01/01/2020")
        data_fim = kwargs.get("data_fim", "31/12/2030")
        # Converte YYYY-MM-DD (incremental) para DD/MM/YYYY
        if data_inicio and len(data_inicio) == 10 and "-" in data_inicio:
            data_inicio = _date_omie(data_inicio)
        if data_fim and len(data_fim) == 10 and "-" in data_fim:
            data_fim = _date_omie(data_fim)

        return {
            "nPagina": pagina,
            "nRegPorPagina": registros_por_pagina,
            "dEmiInicial": data_inicio,
            "dEmiFinal": data_fim,
        }

    def transform_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai lista de NFS-e da resposta."""

        if raw_data.get("faultstring"):
            logger.warning(
                f"NFS-e API retornou erro: {raw_data.get('faultstring')}. "
                f"Chaves: {list(raw_data.keys())}"
            )
            return []

        lista = raw_data.get("nfseEncontradas")

        if not lista:
            logger.info(
                "NFS-e: nenhuma lista encontrada. "
                f"Chaves da resposta: {list(raw_data.keys())}"
            )
            return []

        if isinstance(lista, dict):
            lista = [lista]

        out = []

        for item in lista:
            if not isinstance(item, dict):
                continue

            cab = _get(item, "Cabecalho", {})
            emissao = _get(item, "Emissao", {})

            out.append({
                "numero": str(_get(cab, "nNumeroNFSe") or "")[:30],
                "codigo_nfse": str(_get(cab, "cCodigoVerifNFSe") or "")[:50],
                "data_emissao": str(_get(emissao, "cDataEmissao") or "")[:20],
                "cod_cliente": str(_get(cab, "nCodigoCliente") or "")[:30],
                "valor_total": _get(cab, "nValorNFSe"),
                "situacao": str(_get(cab, "cStatusNFSe") or "")[:30],
            })

        return out
