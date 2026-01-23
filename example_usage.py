"""
Exemplo de uso do sistema de coleta de dados Omie.
"""
from src.orchestrator import DataOrchestrator
from src.config import Settings
from datetime import datetime, timedelta

def exemplo_coleta_completa():
    """Exemplo de coleta completa de todos os dados."""
    print("="*80)
    print("EXEMPLO: Coleta Completa de Dados")
    print("="*80)
    
    # Inicializa
    settings = Settings()
    orchestrator = DataOrchestrator(settings)
    
    try:
        # Inicializa banco de dados
        orchestrator.initialize_database()
        
        # Executa todas as coletas em paralelo
        results = orchestrator.run_collections(
            parallel=True,
            max_workers=5
        )
        
        # Imprime resultados
        print("\nResultados:")
        for result in results:
            print(f"  {result['collector']}: {result['records']} registros")
        
        # Imprime métricas
        orchestrator.print_metrics_summary()
        
    finally:
        orchestrator.cleanup()


def exemplo_coleta_financeira():
    """Exemplo de coleta apenas de dados financeiros."""
    print("="*80)
    print("EXEMPLO: Coleta de Dados Financeiros")
    print("="*80)
    
    settings = Settings()
    orchestrator = DataOrchestrator(settings)
    
    try:
        orchestrator.initialize_database()
        
        # Define período
        data_fim = datetime.now().strftime("%Y-%m-%d")
        data_inicio = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
        
        # Coleta dados financeiros
        results = orchestrator.run_financial_collections(
            data_inicio=data_inicio,
            data_fim=data_fim,
            parallel=True,
            max_workers=3
        )
        
        print(f"\nPeríodo: {data_inicio} a {data_fim}")
        print("\nResultados Financeiros:")
        for result in results:
            print(f"  {result['collector']}: {result['records']} registros")
        
        orchestrator.print_metrics_summary()
        
    finally:
        orchestrator.cleanup()


def exemplo_coleta_individual():
    """Exemplo de coleta de um endpoint específico."""
    print("="*80)
    print("EXEMPLO: Coleta Individual")
    print("="*80)
    
    from src.collectors import ClientesCollector
    
    settings = Settings()
    orchestrator = DataOrchestrator(settings)
    
    try:
        orchestrator.initialize_database()
        
        # Cria coletor específico
        clientes_collector = ClientesCollector(orchestrator.api_client)
        
        # Coleta dados
        result = orchestrator.collect_data(clientes_collector, pagina=1, registros_por_pagina=100)
        
        print(f"\nResultado: {result['collector']}")
        print(f"Registros: {result['records']}")
        print(f"Sucesso: {result['success']}")
        
        orchestrator.print_metrics_summary()
        
    finally:
        orchestrator.cleanup()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        exemplo = sys.argv[1]
        if exemplo == "completa":
            exemplo_coleta_completa()
        elif exemplo == "financeira":
            exemplo_coleta_financeira()
        elif exemplo == "individual":
            exemplo_coleta_individual()
        else:
            print("Uso: python example_usage.py [completa|financeira|individual]")
    else:
        # Executa exemplo completo por padrão
        exemplo_coleta_completa()
