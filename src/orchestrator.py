"""
Orquestrador principal para execução de coletas de dados.
Suporta coleta full e incremental (janela de datas).
"""
import concurrent.futures
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from src.config import Settings
from src.omie import OmieApiClient
from src.database import DatabaseManager
from src.bigquery import BigQueryManager
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
    ContaCorrenteCollector,
    PedidoVendasCollector,
    PedidosCompraCollector,
    CrmOportunidadesCollector,
    EtapasFaturamentoCollector,
    ProdutoFornecedorCollector,
    ServicoResumoCollector,
    VendasResumoCollector,
    NfseCollector,
    NfConsultarCollector,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Tamanho do lote para inserção no MySQL (evita "Lost connection" em tabelas grandes)
INSERT_BATCH_SIZE = 500


class DataOrchestrator:
    """
    Orquestrador principal para coletas de dados.
    Gerencia execução paralela e sequencial de coletas.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Inicializa o orquestrador.
        
        Args:
            settings: Configurações do sistema (opcional)
        """
        self.settings = settings or Settings()
        self.api_client = OmieApiClient(self.settings.omie)
        # BigQuery quando GCP configurado (.env: GOOGLE_APPLICATION_CREDENTIALS + GCP_PROJECT_ID + BIGQUERY_DATASET)
        gcp = self.settings.gcp
        if gcp.GOOGLE_APPLICATION_CREDENTIALS and gcp.project_id and gcp.dataset_id:
            logger.info("Usando BigQuery como destino (fluxo MySQL desativado)")
            self.db_manager = BigQueryManager(gcp)
        else:
            self.db_manager = DatabaseManager(self.settings.database)
        self.metrics = MetricsCollector()
        
        # Registra todos os coletores disponíveis
        self.collectors = [
            ClientesCollector(self.api_client),
            ProdutosCollector(self.api_client),
            ServicosCollector(self.api_client),
            CategoriasCollector(self.api_client),
            ContasReceberCollector(self.api_client),
            ContasPagarCollector(self.api_client),
            ContaCorrenteCollector(self.api_client),  # Importante: antes do Extrato
            ExtratoCollector(self.api_client),
            OrdemServicoCollector(self.api_client),
            ContasDRECollector(self.api_client),
            PedidoVendasCollector(self.api_client),
            PedidosCompraCollector(self.api_client),
            CrmOportunidadesCollector(self.api_client),
            EtapasFaturamentoCollector(self.api_client),
            ProdutoFornecedorCollector(self.api_client),
            ServicoResumoCollector(self.api_client),
            VendasResumoCollector(self.api_client),
            NfseCollector(self.api_client),
            NfConsultarCollector(self.api_client),
        ]
    
    def _save_metric_to_db(self, operation: str, duration: float, success: bool, records_count: int, error_message: str = None):
        """Salva métrica no banco de dados."""
        try:
            # Cria tabela se não existir
            self.db_manager.create_table('api_metrics', {
                'id': 'BIGINT PRIMARY KEY AUTO_INCREMENT',
                'operation': 'VARCHAR(100)',
                'duration': 'DECIMAL(10,2)',
                'success': 'TINYINT(1)',
                'records_count': 'INT',
                'error_message': 'TEXT',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            })
            
            # Insere métrica usando insert_batch (BigQuery NUMERIC(10,2) exige 2 decimais; enviar created_at)
            from datetime import datetime
            metric_data = [{
                'operation': operation,
                'duration': round(float(duration), 2),
                'success': 1 if success else 0,
                'records_count': int(records_count),
                'error_message': str(error_message) if error_message else None,
                'created_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }]
            
            # Usa insert_batch que já trata a criação da tabela
            self.db_manager.insert_batch('api_metrics', metric_data)
        except Exception as e:
            logger.warning(f"Erro ao salvar métrica no banco: {str(e)}")
    
    def initialize_database(self):
        """Inicializa o banco de dados e cria todas as tabelas."""
        logger.info("Inicializando banco de dados...")
        
        try:
            # Cria o banco de dados se não existir
            self.db_manager.create_database_if_not_exists()
            
            # Cria todas as tabelas
            for collector in self.collectors:
                table_name = collector.get_table_name()
                schema = collector.get_schema()
                self.db_manager.create_table(table_name, schema)
            
            logger.info("Banco de dados inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
            raise
    
    def collect_data(
        self, 
        collector, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Coleta dados de um coletor específico.
        
        Args:
            collector: Instância do coletor
            **kwargs: Parâmetros específicos do coletor
            
        Returns:
            Dicionário com resultado da coleta
        """
        operation_name = f"{collector.get_table_name()}_collect"
        timer_id = self.metrics.start_timer(operation_name)
        
        try:
            # Coleta os dados
            data = collector.collect(**kwargs)
            
            if not data:
                duration = self.metrics.stop_timer(timer_id, success=True, records_count=0)
                self._save_metric_to_db(operation_name, duration, True, 0)
                return {
                    "collector": collector.get_table_name(),
                    "success": True,
                    "records": 0,
                    "message": "Nenhum dado encontrado"
                }
            
            table_name = collector.get_table_name()
            key_columns = getattr(collector, 'get_unique_key_columns', lambda: [])()

            if key_columns and hasattr(self.db_manager, 'get_existing_keys') and hasattr(self.db_manager, 'get_key_from_record'):
                # Carga incremental: insere só registros cuja chave ainda não existe
                total_coletado = len(data)
                existing = self.db_manager.get_existing_keys(table_name, key_columns)
                new_data = []
                for r in data:
                    k = self.db_manager.get_key_from_record(r, key_columns)
                    if k is not None and k not in existing:
                        new_data.append(r)
                        existing.add(k)
                data = new_data
                logger.info(f"Incremental '{table_name}': {len(new_data)} novos de {total_coletado} coletados ({total_coletado - len(new_data)} já existentes)")
            else:
                # Full refresh: esvazia a tabela e insere tudo
                if hasattr(self.db_manager, 'truncate_table'):
                    self.db_manager.truncate_table(table_name)

            records_inserted = 0
            for i in range(0, len(data), INSERT_BATCH_SIZE):
                chunk = data[i : i + INSERT_BATCH_SIZE]
                records_inserted += self.db_manager.insert_batch(table_name, chunk)
            
            duration = self.metrics.stop_timer(timer_id, success=True, records_count=records_inserted)
            self._save_metric_to_db(operation_name, duration, True, records_inserted)
            
            return {
                "collector": table_name,
                "success": True,
                "records": records_inserted,
                "message": f"{records_inserted} registros inseridos"
            }
            
        except Exception as e:
            error_msg = str(e)
            duration = self.metrics.stop_timer(timer_id, success=False, records_count=0, error_message=error_msg)
            self._save_metric_to_db(operation_name, duration, False, 0, error_msg)
            logger.error(f"Erro ao coletar dados de {collector.get_table_name()}: {error_msg}")
            
            return {
                "collector": collector.get_table_name(),
                "success": False,
                "records": 0,
                "message": error_msg
            }
    
    def run_collections(
        self, 
        parallel: bool = True,
        max_workers: int = 5,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Executa todas as coletas.
        
        Args:
            parallel: Se True, executa coletas em paralelo
            max_workers: Número máximo de workers para execução paralela
            **kwargs: Parâmetros para os coletores (ex: data_inicio, data_fim)
            
        Returns:
            Lista com resultados de cada coleta
        """
        logger.info(f"Iniciando coletas (paralelo: {parallel}, workers: {max_workers})")
        
        if parallel:
            return self._run_parallel(max_workers, **kwargs)
        else:
            return self._run_sequential(**kwargs)
    
    def _run_parallel(self, max_workers: int, **kwargs) -> List[Dict[str, Any]]:
        """Executa coletas em paralelo."""
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submete todas as tarefas
            future_to_collector = {
                executor.submit(self.collect_data, collector, **kwargs): collector
                for collector in self.collectors
            }
            
            # Coleta os resultados conforme completam
            for future in concurrent.futures.as_completed(future_to_collector):
                collector = future_to_collector[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Erro na coleta de {collector.get_table_name()}: {str(e)}")
                    results.append({
                        "collector": collector.get_table_name(),
                        "success": False,
                        "records": 0,
                        "message": str(e)
                    })
        
        return results
    
    def _run_sequential(self, **kwargs) -> List[Dict[str, Any]]:
        """Executa coletas sequencialmente com delays para evitar rate limiting."""
        results = []
        import time
        
        logger.info(f"Iniciando coletas sequenciais (total: {len(self.collectors)})")
        
        for i, collector in enumerate(self.collectors, 1):
            try:
                logger.info(f"[{i}/{len(self.collectors)}] Coletando {collector.get_table_name()}...")
                # Extrato: injeta conta corrente do .env se configurada (evita extrato zerado)
                collect_kwargs = dict(kwargs)
                if collector.get_table_name() == "extrato":
                    if self.settings.omie.EXTRATO_CONTA_CORRENTE is not None:
                        collect_kwargs["codigo_conta_corrente"] = self.settings.omie.EXTRATO_CONTA_CORRENTE
                    if self.settings.omie.EXTRATO_CONTA_CORRENTE_INTEGRACAO:
                        collect_kwargs["codigo_conta_corrente_integracao"] = self.settings.omie.EXTRATO_CONTA_CORRENTE_INTEGRACAO
                result = self.collect_data(collector, **collect_kwargs)
                results.append(result)
                
                # Delay entre coletores para evitar rate limiting
                if i < len(self.collectors):
                    time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro ao coletar {collector.get_table_name()}: {str(e)}")
                results.append({
                    "collector": collector.get_table_name(),
                    "success": False,
                    "records": 0,
                    "message": str(e)
                })
                # Delay mesmo em caso de erro
                if i < len(self.collectors):
                    time.sleep(1)
        
        return results
    
    def run_financial_collections(
        self,
        data_inicio: str,
        data_fim: str,
        parallel: bool = True,
        max_workers: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Executa coletas específicas de dados financeiros.
        
        Args:
            data_inicio: Data inicial (formato: YYYY-MM-DD)
            data_fim: Data final (formato: YYYY-MM-DD)
            parallel: Se True, executa em paralelo
            max_workers: Número máximo de workers
            
        Returns:
            Lista com resultados das coletas financeiras
        """
        financial_collectors = [
            self.collectors[4],  # ContasReceberCollector
            self.collectors[5],  # ContasPagarCollector
            self.collectors[6],  # ExtratoCollector
        ]
        
        logger.info(f"Coletando dados financeiros de {data_inicio} a {data_fim}")
        
        if parallel:
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_collector = {}
                for collector in financial_collectors:
                    fc_kwargs = {"data_inicio": data_inicio, "data_fim": data_fim}
                    if collector.get_table_name() == "extrato":
                        if self.settings.omie.EXTRATO_CONTA_CORRENTE is not None:
                            fc_kwargs["codigo_conta_corrente"] = self.settings.omie.EXTRATO_CONTA_CORRENTE
                        if self.settings.omie.EXTRATO_CONTA_CORRENTE_INTEGRACAO:
                            fc_kwargs["codigo_conta_corrente_integracao"] = self.settings.omie.EXTRATO_CONTA_CORRENTE_INTEGRACAO
                    future_to_collector[
                        executor.submit(self.collect_data, collector, **fc_kwargs)
                    ] = collector
                
                for future in concurrent.futures.as_completed(future_to_collector):
                    collector = future_to_collector[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Erro na coleta financeira: {str(e)}")
                        results.append({
                            "collector": collector.get_table_name(),
                            "success": False,
                            "records": 0,
                            "message": str(e)
                        })
            return results
        else:
            results = []
            for collector in financial_collectors:
                fc_kwargs = {"data_inicio": data_inicio, "data_fim": data_fim}
                if collector.get_table_name() == "extrato":
                    if self.settings.omie.EXTRATO_CONTA_CORRENTE is not None:
                        fc_kwargs["codigo_conta_corrente"] = self.settings.omie.EXTRATO_CONTA_CORRENTE
                    if self.settings.omie.EXTRATO_CONTA_CORRENTE_INTEGRACAO:
                        fc_kwargs["codigo_conta_corrente_integracao"] = self.settings.omie.EXTRATO_CONTA_CORRENTE_INTEGRACAO
                result = self.collect_data(collector, **fc_kwargs)
                results.append(result)
            return results
    
    def run_incremental_collections(
        self,
        days: int = 5,
        parallel: bool = False,
        max_workers: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Executa coleta incremental: apenas registros alterados/incluídos na janela de datas.
        Janela padrão: últimos 5 dias (ex.: 29/01/2026 → 02/02/2026).
        Usa filtrar_por_data_de, filtrar_por_data_ate e filtrar_apenas_alteracao quando
        o coletor suporta (supports_incremental() == True).
        
        Args:
            days: Número de dias para trás (janela)
            parallel: Se True, executa coletores incrementais em paralelo
            max_workers: Número máximo de workers
            
        Returns:
            Lista com resultados das coletas incrementais
        """
        data_fim = datetime.now().strftime("%Y-%m-%d")
        data_inicio = (datetime.now() - timedelta(days=int(days))).strftime("%Y-%m-%d")
        incremental_collectors = [c for c in self.collectors if c.supports_incremental()]
        
        logger.info(f"Coleta incremental: {data_inicio} a {data_fim} ({days} dias) - {len(incremental_collectors)} coletores")
        
        kwargs = {
            "incremental": True,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "incremental_days": days,
        }
        
        if parallel:
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_collector = {
                    executor.submit(self.collect_data, collector, **kwargs): collector
                    for collector in incremental_collectors
                }
                for future in concurrent.futures.as_completed(future_to_collector):
                    collector = future_to_collector[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Erro na coleta incremental de {collector.get_table_name()}: {str(e)}")
                        results.append({
                            "collector": collector.get_table_name(),
                            "success": False,
                            "records": 0,
                            "message": str(e)
                        })
            return results
        else:
            results = []
            for i, collector in enumerate(incremental_collectors, 1):
                try:
                    logger.info(f"[{i}/{len(incremental_collectors)}] Incremental: {collector.get_table_name()}...")
                    result = self.collect_data(collector, **kwargs)
                    results.append(result)
                    if i < len(incremental_collectors):
                        import time
                        time.sleep(1)
                except Exception as e:
                    logger.error(f"Erro ao coletar incremental {collector.get_table_name()}: {str(e)}")
                    results.append({
                        "collector": collector.get_table_name(),
                        "success": False,
                        "records": 0,
                        "message": str(e)
                    })
            return results
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Retorna resumo das métricas."""
        return self.metrics.get_metrics()
    
    def print_metrics_summary(self):
        """Imprime resumo das métricas."""
        self.metrics.print_summary()
    
    def cleanup(self):
        """Limpa recursos."""
        self.api_client.close()
        self.db_manager.close_pool()
        logger.info("Recursos limpos")
