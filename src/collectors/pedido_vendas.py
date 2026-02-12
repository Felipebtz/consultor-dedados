"""
Coletor de dados de Pedidos de Venda (Omie).
Uma linha por pedido (cabeçalho), alinhado ao total_de_registros da API (~9.354).
"""
from typing import Dict, Any, List
from src.collectors.base import BaseCollector
import logging

logger = logging.getLogger(__name__)


def _get(d: dict, *keys, default=None):
    """Obtém valor de dict aninhado. Ex: _get(p, 'cabecalho', 'codigo_pedido')."""
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k)
    return d if d is not None else default


class PedidoVendasCollector(BaseCollector):
    """Coletor para pedidos de venda (produtos/pedido/). Uma linha por pedido (cabeçalho)."""

    def get_endpoint(self) -> str:
        return "produtos/pedido/"

    def get_method(self) -> str:
        return "ListarPedidos"

    def get_table_name(self) -> str:
        return "pedido_vendas"

    def get_schema(self) -> Dict[str, str]:
        return {
            "id": "BIGINT AUTO_INCREMENT PRIMARY KEY",
            "cod_pedido": "VARCHAR(50)",
            "nr_pedido": "VARCHAR(50)",
            "nr_sequencial_pedido": "VARCHAR(50)",
            "cod_cliente": "VARCHAR(50)",
            "cod_etapa_faturamento": "VARCHAR(20)",
            "fl_faturado": "CHAR(1)",
            "fl_cancelado": "CHAR(1)",
            "dt_pedido": "VARCHAR(30)",
            "dt_previsao": "VARCHAR(30)",
            "cod_vendedor": "VARCHAR(50)",
            "total_vlr_pedido": "DECIMAL(15,2)",
            "quantidade_itens": "INT",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
        }

    def supports_incremental(self) -> bool:
        return True

    def get_unique_key_columns(self) -> List[str]:
        """Chave única por pedido (uma linha por pedido)."""
        return ["cod_pedido"]

    def build_payload(self, pagina: int = 1, registros_por_pagina: int = 200, **kwargs) -> Dict[str, Any]:
        payload = {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": "N",
        }
        if kwargs.get("incremental") and kwargs.get("data_inicio") and kwargs.get("data_fim"):
            payload["filtrar_por_data_de"] = kwargs["data_inicio"]
            payload["filtrar_por_data_ate"] = kwargs["data_fim"]
            payload["filtrar_apenas_alteracao"] = "S"
        return payload

    def transform_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai pedido_venda_produto e gera uma linha por pedido (cabeçalho). Total = total_de_registros da API."""
        rows = raw_data.get("pedido_venda_produto")
        if not rows:
            return super().transform_data(raw_data)
        if isinstance(rows, dict):
            rows = [rows]
        out = []
        for ped in rows:
            cab = ped.get("cabecalho") or {}
            info = ped.get("infoCadastro") or {}
            total = ped.get("total_pedido") or {}
            info_adic = ped.get("informacoes_adicionais") or {}
            det_list = ped.get("det") or []
            quantidade_itens = len(det_list) if det_list else 0
            cod_ped = str(_get(cab, "codigo_pedido") or "")
            nr_seq = str(cab.get("sequencial") or cab.get("numero_pedido") or "")
            row = {
                "cod_pedido": cod_ped,
                "nr_pedido": str(_get(cab, "numero_pedido") or ""),
                "nr_sequencial_pedido": nr_seq,
                "cod_cliente": str(_get(cab, "codigo_cliente") or ""),
                "cod_etapa_faturamento": str(_get(cab, "etapa") or ""),
                "fl_faturado": str(_get(info, "faturado") or "N")[:1],
                "fl_cancelado": str(_get(info, "cancelado") or "N")[:1],
                "dt_pedido": str(_get(info, "dInc") or ""),
                "dt_previsao": str(_get(cab, "data_previsao") or ""),
                "cod_vendedor": str(_get(info_adic, "codVend") or ""),
                "total_vlr_pedido": _get(total, "valor_total_pedido") or 0,
                "quantidade_itens": quantidade_itens,
            }
            if cod_ped:
                out.append(row)
        return out
