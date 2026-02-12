"""
Coletor de resumo de vendas (NF-e, CT-e, cupom fiscal).
API: produtos/vendas-resumo/ - ResumoVendas (período; sem paginação).
"""
from typing import Dict, Any, List
from src.collectors.base import BaseCollector
from src.collectors.servico_resumo import _date_omie
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class VendasResumoCollector(BaseCollector):
    """Coletor para resumo de vendas (produtos/vendas-resumo/)."""

    def get_endpoint(self) -> str:
        return "produtos/vendas-resumo/"

    def get_method(self) -> str:
        return "ResumoVendas"

    def get_table_name(self) -> str:
        return "vendas_resumo"

    def get_schema(self) -> Dict[str, str]:
        return {
            "id": "BIGINT AUTO_INCREMENT PRIMARY KEY",
            "data_inicio": "VARCHAR(20)",
            "data_fim": "VARCHAR(20)",
            "total_nf": "INT",
            "valor_total": "DECIMAL(18,2)",
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
        """Payload: dDataInicio, dDataFim (formato DD/MM/YYYY). Sem paginação."""
        data_inicio = kwargs.get("data_inicio")
        data_fim = kwargs.get("data_fim")
        if data_inicio and data_fim:
            payload = {
                "dDataInicio": _date_omie(data_inicio),
                "dDataFim": _date_omie(data_fim),
            }
        else:
            fim = datetime.now()
            ini = fim - timedelta(days=30)
            payload = {
                "dDataInicio": ini.strftime("%d/%m/%Y"),
                "dDataFim": fim.strftime("%d/%m/%Y"),
            }
        return payload

    def transform_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai resumo da resposta (lista ou objeto único)."""
        if raw_data.get("faultstring"):
            logger.warning(
                f"Resumo Vendas API retornou erro: {raw_data.get('faultstring')}. Chaves: {list(raw_data.keys())}"
            )
            return []
        out = []
        data_inicio = raw_data.get("dDataInicio", "")
        data_fim = raw_data.get("dDataFim", "")
        # Chaves possíveis na resposta Omie
        lista = (
            raw_data.get("listaResumo")
            or raw_data.get("resumoVendas")
            or raw_data.get("cadastros")
            or raw_data.get("resumo_vendas")
        )
        if isinstance(lista, list) and lista:
            for item in lista:
                if not isinstance(item, dict):
                    continue
                row = {
                    "data_inicio": str(data_inicio)[:20],
                    "data_fim": str(data_fim)[:20],
                    "total_nf": item.get("nTotal") or item.get("total_nf") or item.get("quantidade"),
                    "valor_total": item.get("vTotal") or item.get("valor_total") or item.get("valor"),
                }
                out.append(row)
        if not out:
            logger.info(
                f"Resumo Vendas: nenhuma lista encontrada (formato da API pode diferir). "
                f"Chaves: {list(raw_data.keys())}"
            )
            out.append({
                "data_inicio": str(data_inicio)[:20],
                "data_fim": str(data_fim)[:20],
                "total_nf": raw_data.get("total_de_registros"),
                "valor_total": raw_data.get("valor_total"),
            })
        return out
