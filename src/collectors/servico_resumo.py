"""
Coletor de resumo de faturamento de serviços (NFS-e, recibo etc.).
API: servicos/resumo/ - ObterResumoServicos (sem paginação; período dDataInicio/dDataFim).
"""
from typing import Dict, Any, List
from src.collectors.base import BaseCollector
import logging

logger = logging.getLogger(__name__)


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


class ServicoResumoCollector(BaseCollector):
    """Coletor para resumo do faturamento de serviços (servicos/resumo/)."""

    def get_endpoint(self) -> str:
        return "servicos/resumo/"

    def get_method(self) -> str:
        return "ObterResumoServicos"

    def get_table_name(self) -> str:
        return "servico_resumo"

    def get_schema(self) -> Dict[str, str]:
        return {
            "id": "BIGINT AUTO_INCREMENT PRIMARY KEY",
            "data_inicio": "VARCHAR(20)",
            "data_fim": "VARCHAR(20)",
            "n_faturadas": "INT",
            "v_faturadas": "DECIMAL(18,2)",
            "n_pendentes": "INT",
            "v_pendentes": "DECIMAL(18,2)",
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
        """
        Payload conforme API Omie: dDataInicio, dDataFim, lApenasResumo.
        Sem paginação. Em incremental usa data_inicio/data_fim de kwargs.
        """
        data_inicio = kwargs.get("data_inicio")
        data_fim = kwargs.get("data_fim")
        if data_inicio and data_fim:
            payload = {
                "dDataInicio": _date_omie(data_inicio),
                "dDataFim": _date_omie(data_fim),
                "lApenasResumo": True,
            }
        else:
            # Fallback: último mês
            from datetime import datetime, timedelta
            fim = datetime.now()
            ini = fim - timedelta(days=30)
            payload = {
                "dDataInicio": ini.strftime("%d/%m/%Y"),
                "dDataFim": fim.strftime("%d/%m/%Y"),
                "lApenasResumo": True,
            }
        return payload

    def transform_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Resposta é um objeto único (painel, ordemServico, etc.).
        Extrai painel.faturamentoResumo e retorna uma linha por período.
        """
        if raw_data.get("faultstring"):
            logger.warning(
                f"Resumo Serviços API retornou erro: {raw_data.get('faultstring')}. Chaves: {list(raw_data.keys())}"
            )
            return []
        out = []
        data_inicio = raw_data.get("dDataInicio", "")
        data_fim = raw_data.get("dDataFim", "")
        painel = raw_data.get("painel") or raw_data.get("painelResumo")
        if isinstance(painel, dict):
            fat = painel.get("faturamentoResumo") or painel
            n_fat = fat.get("nFaturadas") if isinstance(fat.get("nFaturadas"), (int, type(None))) else None
            v_fat = fat.get("vFaturadas")
            n_pend = fat.get("nPendentes") if isinstance(fat.get("nPendentes"), (int, type(None))) else None
            v_pend = fat.get("vPendentes")
            out.append({
                "data_inicio": str(data_inicio)[:20],
                "data_fim": str(data_fim)[:20],
                "n_faturadas": n_fat,
                "v_faturadas": v_fat,
                "n_pendentes": n_pend,
                "v_pendentes": v_pend,
            })
        if not out:
            logger.info(
                f"Resumo Serviços: painel não encontrado na resposta (pode ser formato diferente). "
                f"Chaves: {list(raw_data.keys())}"
            )
            out.append({
                "data_inicio": str(data_inicio)[:20],
                "data_fim": str(data_fim)[:20],
                "n_faturadas": None,
                "v_faturadas": None,
                "n_pendentes": None,
                "v_pendentes": None,
            })
        return out
