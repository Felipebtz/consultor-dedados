"""
Script principal para execução de coletas de dados do Omie.
Suporta coleta full e incremental (--incremental: últimos 5 dias).
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

INCREMENTAL_DAYS_DEFAULT = 5


def main():
    """Função principal."""
    incremental = "--incremental" in sys.argv or "-i" in sys.argv
    try:
        settings = Settings()
        orchestrator = DataOrchestrator(settings)
        orchestrator.initialize_database()
        
        if incremental:
            days = INCREMENTAL_DAYS_DEFAULT
            for i, arg in enumerate(sys.argv):
                if arg in ("--incremental", "-i") and i + 1 < len(sys.argv) and sys.argv[i + 1].isdigit():
                    days = int(sys.argv[i + 1])
                    break
            data_fim = datetime.now().strftime("%Y-%m-%d")
            data_inicio = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            print("\n" + "="*80)
            print("COLETA INCREMENTAL OMIE (apenas alterações/inclusões recentes)")
            print("="*80)
            print(f"Janela: {data_inicio} → {data_fim} ({days} dias)")
            print("="*80 + "\n")
            all_results = orchestrator.run_incremental_collections(days=days, parallel=False, max_workers=3)
        else:
            data_fim = datetime.now().strftime("%Y-%m-%d")
            data_inicio = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
            print("\n" + "="*80)
            print("SISTEMA DE COLETA DE DADOS OMIE (full)")
            print("="*80)
            print(f"Período: {data_inicio} a {data_fim}")
            print("="*80 + "\n")
            logger.info("Iniciando coletas gerais...")
            results_general = orchestrator.run_collections(parallel=False, max_workers=5)
            logger.info("Iniciando coletas financeiras...")
            results_financial = orchestrator.run_financial_collections(
                data_inicio=data_inicio,
                data_fim=data_fim,
                parallel=False,
                max_workers=3
            )
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
        
        # --- BIGQUERY / GCS: metadado da coleta (comentário para rastreabilidade) ---
        # Aqui você pode montar o metadado (execucao_id, data_inicio, data_fim, modo,
        # tabelas_coletadas, registros_por_tabela, etc.) e:
        # 1) Gravar em JSON (ex.: metadata_coleta_YYYYMMDD_HHMMSS.json) para enviar ao GCS
        # 2) Gravar em tabela MySQL execucao_coleta (opcional)
        # Ver docs/BIGQUERY_GCS_PASSO_A_PASSO.md para o passo a passo completo (GCS → BigQuery).
        
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
