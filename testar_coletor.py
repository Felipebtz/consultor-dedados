"""
Script para testar coletores individualmente.
Uso: python testar_coletor.py <nome_do_coletor>

Coletores disponíveis:
- clientes
- produtos
- servicos
- categorias
- contas_receber
- contas_pagar
- extrato
- ordem_servico
- contas_dre
"""
import sys
import logging
from datetime import datetime, timedelta
from src.config import Settings
from src.omie import OmieApiClient
from src.database import DatabaseManager
from src.metrics import MetricsCollector
from src.collectors import (
    ClientesCollector,
    ProdutosCollector,
    ServicosCollector,
    CategoriasCollector,
    ContasReceberCollector,
    ContasPagarCollector,
    ExtratoCollector,
    OrdemServicoCollector,
    ContasDRECollector,
    ContaCorrenteCollector
)

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Mapeamento de coletores
COLLECTORS = {
    'clientes': ClientesCollector,
    'produtos': ProdutosCollector,
    'servicos': ServicosCollector,
    'categorias': CategoriasCollector,
    'contas_receber': ContasReceberCollector,
    'contas_pagar': ContasPagarCollector,
    'extrato': ExtratoCollector,
    'ordem_servico': OrdemServicoCollector,
    'contas_dre': ContasDRECollector,
    'conta_corrente': ContaCorrenteCollector
}


def test_collector(collector_name: str):
    """Testa um coletor específico."""
    
    if collector_name not in COLLECTORS:
        print(f"\n❌ Coletor '{collector_name}' não encontrado!")
        print(f"\nColetores disponíveis:")
        for name in COLLECTORS.keys():
            print(f"  - {name}")
        return
    
    print("="*80)
    print(f"TESTANDO COLETOR: {collector_name.upper()}")
    print("="*80)
    
    try:
        # Inicializa componentes
        settings = Settings()
        api_client = OmieApiClient(settings.omie)
        db_manager = DatabaseManager(settings.database)
        metrics = MetricsCollector()
        
        # Cria o coletor
        CollectorClass = COLLECTORS[collector_name]
        collector = CollectorClass(api_client)
        
        # Inicializa banco de dados
        logger.info("Inicializando banco de dados...")
        db_manager.create_database_if_not_exists()
        db_manager.create_table(collector.get_table_name(), collector.get_schema())
        
        # Prepara parâmetros
        kwargs = {}
        data_fim = datetime.now().strftime('%Y-%m-%d')
        data_inicio = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        
        # Parâmetros específicos por coletor
        if collector_name in ['contas_receber', 'contas_pagar']:
            kwargs['data_inicio'] = data_inicio
            kwargs['data_fim'] = data_fim
        elif collector_name == 'extrato':
            # Extrato precisa de conta corrente válida
            # Se não houver, o coletor irá pular automaticamente
            # Para usar, você precisaria primeiro listar as contas correntes
            # e passar o código válido aqui: kwargs['codigo_conta_corrente'] = <codigo_valido>
            kwargs['data_inicio'] = data_inicio
            kwargs['data_fim'] = data_fim
            # Não passa codigo_conta_corrente para que o coletor detecte e pule
        
        # Inicia timer
        timer_id = metrics.start_timer(f"{collector_name}_test")
        
        print(f"\n📊 Coletando dados de {collector.get_table_name()}...")
        print(f"Endpoint: {collector.get_endpoint()}")
        print(f"Método: {collector.get_method()}")
        print(f"Payload: {collector.build_payload(**kwargs)}")
        print("-"*80)
        
        # Coleta dados (com delay entre requisições)
        print("⏳ Aguardando 1 segundo antes de iniciar a coleta...")
        import time
        time.sleep(1)
        
        data = collector.collect(**kwargs)
        
        print(f"\n✅ Dados coletados: {len(data)} registros")
        
        if data:
            # Mostra exemplo do primeiro registro
            print(f"\n📋 Exemplo do primeiro registro:")
            print(f"Chaves: {list(data[0].keys())[:10]}")
            print(f"Primeiros campos: {dict(list(data[0].items())[:5])}")
            
            # Insere no banco
            print(f"\n💾 Inserindo dados no banco...")
            records_inserted = db_manager.insert_batch(collector.get_table_name(), data)
            print(f"✅ Registros inseridos: {records_inserted}")
        else:
            print(f"\n⚠️  Nenhum dado foi coletado!")
            print(f"Verifique os logs acima para entender o problema.")
        
        # Finaliza timer
        duration = metrics.stop_timer(timer_id, success=len(data) > 0, records_count=len(data))
        print(f"\n⏱️  Tempo de execução: {duration:.2f}s")
        
        # Fecha conexões
        api_client.close()
        
        print("\n" + "="*80)
        print("✅ TESTE CONCLUÍDO")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Erro ao testar coletor: {str(e)}", exc_info=True)
        print(f"\n❌ ERRO: {str(e)}")
        print("\nVerifique os logs acima para mais detalhes.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n" + "="*80)
        print("TESTE DE COLETORES INDIVIDUAIS")
        print("="*80)
        print("\nUso: python testar_coletor.py <nome_do_coletor>")
        print("\nColetores disponíveis:")
        for name in sorted(COLLECTORS.keys()):
            print(f"  - {name}")
        print("\nExemplo:")
        print("  python testar_coletor.py servicos")
        print("  python testar_coletor.py ordem_servico")
        print("="*80)
    else:
        collector_name = sys.argv[1].lower()
        test_collector(collector_name)
