"""
Coletor de dados de Pedidos de Venda (Omie).
Uma linha por item do pedido (explode det).
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
    """Coletor para pedidos de venda (produtos/pedido/). Uma linha por item (det)."""

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
            "produto_codigo_produto": "VARCHAR(50)",
            "produto_descricao": "TEXT",
            "produto_quantidade": "DECIMAL(15,4)",
            "produto_valor_unitario": "DECIMAL(15,4)",
            "produto_valor_total": "DECIMAL(15,4)",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
        }

    def build_payload(self, pagina: int = 1, registros_por_pagina: int = 200, **kwargs) -> Dict[str, Any]:
        return {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": "N",
        }

    def transform_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai pedido_venda_produto e gera uma linha por item (det)."""
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
            if not det_list:
                det_list = [{}]
            for item in det_list:
                prod = item.get("produto") or {}
                row = {
                    "cod_pedido": str(_get(cab, "codigo_pedido") or ""),
                    "nr_pedido": str(_get(cab, "numero_pedido") or ""),
                    "nr_sequencial_pedido": str(_get(cab, "sequencial") or ""),
                    "cod_cliente": str(_get(cab, "codigo_cliente") or ""),
                    "cod_etapa_faturamento": str(_get(cab, "etapa") or ""),
                    "fl_faturado": str(_get(info, "faturado") or "N")[:1],
                    "fl_cancelado": str(_get(info, "cancelado") or "N")[:1],
                    "dt_pedido": str(_get(info, "dInc") or ""),
                    "dt_previsao": str(_get(cab, "data_previsao") or ""),
                    "cod_vendedor": str(_get(info_adic, "codVend") or ""),
                    "total_vlr_pedido": _get(total, "valor_total_pedido") or 0,
                    "produto_codigo_produto": str(_get(prod, "codigo_produto") or ""),
                    "produto_descricao": str(_get(prod, "descricao") or "")[:500],
                    "produto_quantidade": _get(prod, "quantidade") or 0,
                    "produto_valor_unitario": _get(prod, "valor_unitario") or 0,
                    "produto_valor_total": _get(prod, "valor_total") or 0,
                }
                out.append(row)
        return out
