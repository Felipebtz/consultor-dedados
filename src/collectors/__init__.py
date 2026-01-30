"""
Módulo de coletores de dados.
"""
from src.collectors.base import BaseCollector
from src.collectors.clientes import ClientesCollector
from src.collectors.produtos import ProdutosCollector
from src.collectors.servicos import ServicosCollector
from src.collectors.categorias import CategoriasCollector
from src.collectors.contas_receber import ContasReceberCollector
from src.collectors.contas_pagar import ContasPagarCollector
from src.collectors.extrato import ExtratoCollector
from src.collectors.ordem_servico import OrdemServicoCollector
from src.collectors.contas_dre import ContasDRECollector
from src.collectors.conta_corrente import ContaCorrenteCollector
from src.collectors.pedido_vendas import PedidoVendasCollector
from src.collectors.crm_oportunidades import CrmOportunidadesCollector
from src.collectors.etapas_faturamento import EtapasFaturamentoCollector
from src.collectors.produto_fornecedor import ProdutoFornecedorCollector

__all__ = [
    "BaseCollector",
    "ClientesCollector",
    "ProdutosCollector",
    "ServicosCollector",
    "CategoriasCollector",
    "ContasReceberCollector",
    "ContasPagarCollector",
    "ExtratoCollector",
    "OrdemServicoCollector",
    "ContasDRECollector",
    "ContaCorrenteCollector",
    "PedidoVendasCollector",
    "CrmOportunidadesCollector",
    "EtapasFaturamentoCollector",
    "ProdutoFornecedorCollector",
]
