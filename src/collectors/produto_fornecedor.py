"""
Coletor de dados de Produto x Fornecedor (Omie).
Resposta em cadastros (fornecedores com lista produtos); uma linha por (fornecedor, produto).
"""
from typing import Dict, Any, List
from src.collectors.base import BaseCollector
import logging

logger = logging.getLogger(__name__)


def _get(d: dict, key: str, default=None):
    if not isinstance(d, dict):
        return default
    return d.get(key, default)


class ProdutoFornecedorCollector(BaseCollector):
    """Coletor para Produto Fornecedor (estoque/produtofornecedor/). Uma linha por produto do fornecedor."""

    def get_endpoint(self) -> str:
        return "estoque/produtofornecedor/"

    def get_method(self) -> str:
        return "ListarProdutoFornecedor"

    def get_table_name(self) -> str:
        return "produto_fornecedor"

    def get_schema(self) -> Dict[str, str]:
        return {
            "id": "BIGINT AUTO_INCREMENT PRIMARY KEY",
            "cod_fornecedor": "VARCHAR(50)",
            "nome_fantasia": "VARCHAR(255)",
            "razao_social": "VARCHAR(255)",
            "cpf_cnpj": "VARCHAR(20)",
            "id_produto": "VARCHAR(50)",
            "cod_produto_fornecedor": "VARCHAR(100)",
            "de_produto": "TEXT",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
        }

    def build_payload(self, pagina: int = 1, registros_por_pagina: int = 200, **kwargs) -> Dict[str, Any]:
        return {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
        }

    def transform_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai cadastros e achata: uma linha por (fornecedor, produto)."""
        rows = raw_data.get("cadastros")
        if not rows:
            return super().transform_data(raw_data)
        if isinstance(rows, dict):
            rows = [rows]
        out = []
        for forn in rows:
            produtos = forn.get("produtos") or []
            for prod in produtos:
                cod_forn = _get(forn, "nCodForn")
                cod_prod_forn = _get(prod, "cCodigo")
                if cod_prod_forn is not None and str(cod_prod_forn).strip():
                    cod_prod_forn = str(cod_prod_forn).lstrip("0") or cod_prod_forn
                row = {
                    "cod_fornecedor": str(cod_forn or ""),
                    "nome_fantasia": str(_get(forn, "cNomeFantasia") or "")[:255],
                    "razao_social": str(_get(forn, "cRazaoSocial") or "")[:255],
                    "cpf_cnpj": str(_get(forn, "cCpfCnpj") or "")[:20],
                    "id_produto": str(_get(prod, "nCodProd") or ""),
                    "cod_produto_fornecedor": str(cod_prod_forn or "")[:100],
                    "de_produto": str(_get(prod, "cDescricao") or "")[:2000],
                }
                out.append(row)
        return out
