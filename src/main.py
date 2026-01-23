"""
Script principal para execução de coletas de dados do Omie.
"""
import sys
from datetime import datetime, timedelta
from src.orchestrator import DataOrchestrator
from src.config import Settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Função principal."""
    try:
        # Inicializa configurações
        settings = Settings()
        
        # Cria o orquestrador
        orchestrator = DataOrchestrator(settings)
        
        # Inicializa o banco de dados
        orchestrator.initialize_database()
        
        # Define período padrão (últimos 6 meses)
        data_fim = datetime.now().strftime("%Y-%m-%d")
        data_inicio = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        
        print("\n" + "="*80)
        print("SISTEMA DE COLETA DE DADOS OMIE")
        print("="*80)
        print(f"Período: {data_inicio} a {data_fim}")
        print("="*80 + "\n")
        
        # Executa coletas gerais (sequencial para evitar rate limiting)
        logger.info("Iniciando coletas gerais...")
        results_general = orchestrator.run_collections(
            parallel=False,  # Modo sequencial para evitar erros 500
            max_workers=5
        )
        
        # Executa coletas financeiras com período específico (sequencial)
        logger.info("Iniciando coletas financeiras...")
        results_financial = orchestrator.run_financial_collections(
            data_inicio=data_inicio,
            data_fim=data_fim,
            parallel=False,  # Modo sequencial para evitar erros 500
            max_workers=3
        )
        
        # Combina resultados
        all_results = results_general + results_financial
        
        # Imprime resultados
        print("\n" + "="*80)
        print("RESULTADOS DAS COLETAS")
        print("="*80)
        for result in all_results:
            status = "[OK]" if result['success'] else "[ERRO]"
            print(f"{status} {result['collector']}: {result['records']} registros")
            if not result['success']:
                print(f"  Erro: {result['message']}")
        print("="*80 + "\n")
        
        # Imprime métricas de performance
        orchestrator.print_metrics_summary()
        
        # Limpa recursos
        orchestrator.cleanup()
        
        print("Coleta de dados concluída com sucesso!")
        
    except KeyboardInterrupt:
        logger.info("Operação cancelada pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
