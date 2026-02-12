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
from src.collectors.servico_resumo import ServicoResumoCollector
from src.collectors.vendas_resumo import VendasResumoCollector
from src.collectors.nfse import NfseCollector
from src.collectors.nfconsultar import NfConsultarCollector
from src.collectors.pedidos_compra import PedidosCompraCollector

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
    "ServicoResumoCollector",
    "VendasResumoCollector",
    "NfseCollector",
    "NfConsultarCollector",
    "PedidosCompraCollector",
]
