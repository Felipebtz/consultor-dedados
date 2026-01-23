"""
Sistema de coleta de métricas de performance.
"""
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging
from src.core.interfaces import IMetricsCollector

logger = logging.getLogger(__name__)


@dataclass
class MetricRecord:
    """Registro de uma métrica."""
    operation: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    success: bool = False
    records_count: int = 0
    error_message: Optional[str] = None
    
    def finish(self, success: bool = True, records_count: int = 0, error_message: Optional[str] = None):
        """Finaliza a métrica."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.success = success
        self.records_count = records_count
        self.error_message = error_message


class MetricsCollector(IMetricsCollector):
    """
    Coletor de métricas de performance.
    Implementa padrão Singleton.
    """
    
    _instance = None
    
    def __new__(cls):
        """Implementa padrão Singleton."""
        if cls._instance is None:
            cls._instance = super(MetricsCollector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa o coletor de métricas."""
        if self._initialized:
            return
        
        self._metrics: Dict[str, MetricRecord] = {}
        self._completed_metrics: List[MetricRecord] = []
        self._initialized = True
    
    def start_timer(self, operation: str) -> str:
        """
        Inicia um timer para uma operação.
        
        Args:
            operation: Nome da operação
            
        Returns:
            ID do timer
        """
        timer_id = f"{operation}_{int(time.time() * 1000000)}"
        metric = MetricRecord(operation=operation, start_time=time.time())
        self._metrics[timer_id] = metric
        
        logger.debug(f"Timer iniciado: {operation} (ID: {timer_id})")
        return timer_id
    
    def stop_timer(
        self, 
        timer_id: str, 
        success: bool = True, 
        records_count: int = 0,
        error_message: Optional[str] = None
    ) -> float:
        """
        Para um timer e retorna o tempo decorrido.
        
        Args:
            timer_id: ID do timer
            success: Se a operação foi bem-sucedida
            records_count: Número de registros processados
            error_message: Mensagem de erro (se houver)
            
        Returns:
            Tempo decorrido em segundos
        """
        if timer_id not in self._metrics:
            logger.warning(f"Timer não encontrado: {timer_id}")
            return 0.0
        
        metric = self._metrics[timer_id]
        metric.finish(success, records_count, error_message)
        
        # Move para lista de métricas completadas
        self._completed_metrics.append(metric)
        del self._metrics[timer_id]
        
        logger.info(
            f"Timer finalizado: {metric.operation} - "
            f"Tempo: {metric.duration:.2f}s - "
            f"Registros: {records_count} - "
            f"Sucesso: {success}"
        )
        
        return metric.duration
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Retorna todas as métricas coletadas.
        
        Returns:
            Dicionário com estatísticas das métricas
        """
        if not self._completed_metrics:
            return {
                "total_operations": 0,
                "total_time": 0.0,
                "average_time": 0.0,
                "operations": []
            }
        
        total_time = sum(m.duration for m in self._completed_metrics if m.duration)
        successful_ops = [m for m in self._completed_metrics if m.success]
        failed_ops = [m for m in self._completed_metrics if not m.success]
        
        operations_summary = []
        for metric in self._completed_metrics:
            operations_summary.append({
                "operation": metric.operation,
                "duration": round(metric.duration, 2) if metric.duration else 0.0,
                "success": metric.success,
                "records_count": metric.records_count,
                "error_message": metric.error_message
            })
        
        return {
            "total_operations": len(self._completed_metrics),
            "successful_operations": len(successful_ops),
            "failed_operations": len(failed_ops),
            "total_time": round(total_time, 2),
            "average_time": round(total_time / len(self._completed_metrics), 2) if self._completed_metrics else 0.0,
            "min_time": round(min(m.duration for m in self._completed_metrics if m.duration), 2) if successful_ops else 0.0,
            "max_time": round(max(m.duration for m in self._completed_metrics if m.duration), 2) if successful_ops else 0.0,
            "total_records": sum(m.records_count for m in self._completed_metrics),
            "operations": operations_summary
        }
    
    def get_operation_metrics(self, operation: str) -> List[Dict[str, Any]]:
        """
        Retorna métricas de uma operação específica.
        
        Args:
            operation: Nome da operação
            
        Returns:
            Lista de métricas da operação
        """
        operation_metrics = [m for m in self._completed_metrics if m.operation == operation]
        
        return [
            {
                "duration": round(m.duration, 2) if m.duration else 0.0,
                "success": m.success,
                "records_count": m.records_count,
                "error_message": m.error_message
            }
            for m in operation_metrics
        ]
    
    def reset(self):
        """Reseta todas as métricas."""
        self._metrics.clear()
        self._completed_metrics.clear()
        logger.info("Métricas resetadas")
    
    def print_summary(self):
        """Imprime um resumo das métricas."""
        metrics = self.get_metrics()
        
        print("\n" + "="*80)
        print("RESUMO DE MÉTRICAS DE PERFORMANCE")
        print("="*80)
        print(f"Total de Operações: {metrics['total_operations']}")
        print(f"Operações Bem-sucedidas: {metrics['successful_operations']}")
        print(f"Operações com Erro: {metrics['failed_operations']}")
        print(f"Tempo Total: {metrics['total_time']}s")
        print(f"Tempo Médio: {metrics['average_time']}s")
        print(f"Tempo Mínimo: {metrics['min_time']}s")
        print(f"Tempo Máximo: {metrics['max_time']}s")
        print(f"Total de Registros: {metrics['total_records']}")
        print("\nDetalhes por Operação:")
        print("-"*80)
        
        for op in metrics['operations']:
            status = "✓" if op['success'] else "✗"
            print(f"{status} {op['operation']}: {op['duration']}s ({op['records_count']} registros)")
            if op['error_message']:
                print(f"  Erro: {op['error_message']}")
        
        print("="*80 + "\n")
