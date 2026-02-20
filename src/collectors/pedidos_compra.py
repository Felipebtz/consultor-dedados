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
            "cod_fornecedor_integracao": "VARCHAR(50)",
            "cnpj_cpf_fornecedor": "VARCHAR(20)",
            "data_previsao": "VARCHAR(20)",
            "cod_parc": "VARCHAR(10)",
            "qtde_parc": "INT",
            "cod_categoria": "VARCHAR(30)",
            "cod_comprador": "VARCHAR(20)",
            "contato": "VARCHAR(120)",
            "numero_contrato": "VARCHAR(30)",
            "numero_pedido_fornecedor": "VARCHAR(30)",
            "cod_conta_corrente": "VARCHAR(50)",
            "cod_conta_corrente_integracao": "VARCHAR(50)",
            "cod_projeto": "VARCHAR(50)",
            "observacao": "TEXT",
            "observacao_interna": "TEXT",
            "quantidade_itens": "INT",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
        }

    def supports_incremental(self) -> bool:
        return False  # Desativado por enquanto (API Omie 500); coleta só em full.

    def get_unique_key_columns(self) -> List[str]:
        return []  # Full refresh: truncar e inserir tudo (sem incremental).

    def build_payload(
        self,
        pagina: int = 1,
        registros_por_pagina: int = 100,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Payload alinhado à API Omie. Máximo 100 registros por página (limite da Omie).
        Janela: 01/01/2024 até hoje. Flags iguais ao script que funciona.
        """
        from datetime import datetime
        hoje = datetime.now()
        data_inicio_default = "01/01/2024"
        data_fim_default = hoje.strftime("%d/%m/%Y")

        # Omie: máximo 100 registros por página neste endpoint
        n_regs = min(int(registros_por_pagina), 100)
        payload = {
            "nPagina": int(pagina),
            "nRegsPorPagina": n_regs,
            "lApenasImportadoApi": "F",
            "lExibirPedidosPendentes": "T",
            "lExibirPedidosFaturados": "T",
            "lExibirPedidosRecebidos": "T",
            "lExibirPedidosCancelados": "F",
            "lExibirPedidosEncerrados": "F",
            "lExibirPedidosRecParciais": "T",
            "lExibirPedidosFatParciais": "T",
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

        def _str_val(v, n):
            return str(v or "")[:n] if v is not None else None

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
                "cod_pedido_integracao": _str_val(cab.get("cCodIntPed"), 50),
                "numero": _str_val(cab.get("cNumero"), 30),
                "cod_fornecedor": _str_val(cab.get("nCodFor"), 50),
                "cod_fornecedor_integracao": _str_val(cab.get("cCodIntFor"), 50),
                "cnpj_cpf_fornecedor": _str_val(cab.get("cCnpjCpfFor"), 20),
                "data_previsao": _str_val(cab.get("dDtPrevisao"), 20),
                "cod_parc": _str_val(cab.get("cCodParc"), 10),
                "qtde_parc": cab.get("nQtdeParc"),
                "cod_categoria": _str_val(cab.get("cCodCateg"), 30),
                "cod_comprador": _str_val(cab.get("nCodCompr"), 20),
                "contato": _str_val(cab.get("cContato"), 120),
                "numero_contrato": _str_val(cab.get("cContrato"), 30),
                "numero_pedido_fornecedor": _str_val(cab.get("cNumPedido") or cab.get("cNumero"), 30),
                "cod_conta_corrente": _str_val(cab.get("nCodCC"), 50),
                "cod_conta_corrente_integracao": _str_val(cab.get("nCodIntCC"), 50),
                "cod_projeto": _str_val(cab.get("nCodProj"), 50),
                "observacao": (str(cab.get("cObs") or "")[:65535]) if cab.get("cObs") else None,
                "observacao_interna": (str(cab.get("cObsInt") or "")[:65535]) if cab.get("cObsInt") else None,
                "quantidade_itens": len(produtos),
            }
            out.append(row)
        return out