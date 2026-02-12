"""
Coletor de dados de Pedidos de Compra (Omie).
API: produtos/pedidocompra/ - PesquisarPedCompra (com_pedido_pesquisar_request).
Retorno: pedidos_pesquisa (lista com cabecalho_consulta, produtos_consulta, etc).
Uma linha por pedido (cabeçalho).
"""
from typing import Dict, Any, List
from src.collectors.base import BaseCollector
import logging

logger = logging.getLogger(__name__)


def _get(d: dict, *keys, default=None):
    """Obtém valor de dict aninhado. Ex: _get(p, 'cabecalho_consulta', 'nCodPed')."""
    for k in keys:
        if not isinstance(d, dict):
            return default
        d = d.get(k)
    return d if d is not None else default


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


class PedidosCompraCollector(BaseCollector):
    """Coletor para pedidos de compra (produtos/pedidocompra/). Uma linha por pedido (cabeçalho)."""

    def get_endpoint(self) -> str:
        return "produtos/pedidocompra/"

    def get_method(self) -> str:
        return "PesquisarPedCompra"

    def get_table_name(self) -> str:
        return "pedidos_compra"

    def get_schema(self) -> Dict[str, str]:
        return {
            "id": "BIGINT AUTO_INCREMENT PRIMARY KEY",
            "cod_pedido": "VARCHAR(50)",
            "cod_pedido_integracao": "VARCHAR(50)",
            "numero": "VARCHAR(30)",
            "cod_fornecedor": "VARCHAR(50)",
            "data_previsao": "VARCHAR(20)",
            "cod_conta_corrente": "VARCHAR(50)",
            "cod_projeto": "VARCHAR(50)",
            "observacao": "TEXT",
            "quantidade_itens": "INT",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
        }

    def supports_incremental(self) -> bool:
        return True

    def get_unique_key_columns(self) -> List[str]:
        return ["cod_pedido"]

    def build_payload(
        self,
        pagina: int = 1,
        registros_por_pagina: int = 50,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Payload conforme com_pedido_pesquisar_request (PesquisarPedCompra).
        Exemplo oficial: nPagina, nRegsPorPagina, lApenasImportadoApi, lExibirPedidos* (T/F), dDataInicial, dDataFinal (DD/MM/YYYY), lApenasAlterados (F).
        Usar janela de datas menor (ex.: último ano) para evitar 500.
        """
        # Janela padrão: último ano (API pode retornar 500 com intervalo muito grande)
        from datetime import datetime, timedelta
        hoje = datetime.now()
        um_ano_atras = hoje - timedelta(days=365)
        data_inicio_default = um_ano_atras.strftime("%d/%m/%Y")
        data_fim_default = hoje.strftime("%d/%m/%Y")

        payload = {
            "nPagina": pagina,
            "nRegsPorPagina": registros_por_pagina,
            "lApenasImportadoApi": "F",
            "lExibirPedidosPendentes": "T",
            "lExibirPedidosFaturados": "F",
            "lExibirPedidosRecebidos": "F",
            "lExibirPedidosCancelados": "F",
            "lExibirPedidosEncerrados": "F",
            "lExibirPedidosRecParciais": "F",
            "lExibirPedidosFatParciais": "F",
            "dDataInicial": data_inicio_default,
            "dDataFinal": data_fim_default,
            "lApenasAlterados": "F",
        }
        if kwargs.get("incremental") and kwargs.get("data_inicio") and kwargs.get("data_fim"):
            payload["dDataInicial"] = _date_omie(kwargs["data_inicio"])
            payload["dDataFinal"] = _date_omie(kwargs["data_fim"])
            payload["lApenasAlterados"] = "T"
        return payload

    def transform_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai pedidos_pesquisa e gera uma linha por pedido (cabeçalho)."""
        if raw_data.get("faultstring"):
            logger.warning(
                f"Pedidos de Compra API retornou erro: {raw_data.get('faultstring')}. "
                f"Chaves: {list(raw_data.keys())}"
            )
            return []

        lista = raw_data.get("pedidos_pesquisa")
        if not lista:
            logger.info(
                "Pedidos de Compra: nenhuma lista encontrada. "
                f"Chaves da resposta: {list(raw_data.keys())}"
            )
            return []

        if isinstance(lista, dict):
            lista = [lista]

        out = []
        for item in lista:
            if not isinstance(item, dict):
                continue
            cab = _get(item, "cabecalho_consulta") or {}
            produtos = item.get("produtos_consulta") or []
            if isinstance(produtos, dict):
                produtos = [produtos]
            cod_ped = str(_get(cab, "nCodPed") or "")
            if not cod_ped:
                continue
            row = {
                "cod_pedido": cod_ped[:50],
                "cod_pedido_integracao": str(cab.get("cCodIntPed") or "")[:50],
                "numero": str(cab.get("cNumero") or "")[:30],
                "cod_fornecedor": str(cab.get("nCodFor") or "")[:50],
                "data_previsao": str(cab.get("dDtPrevisao") or "")[:20],
                "cod_conta_corrente": str(cab.get("nCodCC") or "")[:50],
                "cod_projeto": str(cab.get("nCodProj") or "")[:50],
                "observacao": str(cab.get("cObs") or "")[:65535] if cab.get("cObs") else None,
                "quantidade_itens": len(produtos),
            }
            out.append(row)
        return out
