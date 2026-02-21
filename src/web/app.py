"""
Aplicação Web Flask para Dashboard do Sistema de Coleta Omie.
Lê do BigQuery quando GCP está configurado; senão lê do MySQL (apenas em ambiente local).
Na Vercel NÃO existe MySQL: usa só BigQuery ou stub (dados vazios) para evitar erro de conexão.
Otimizado: cache curto (45s), contagens em paralelo, respostas leves.
"""
import os
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, render_template, jsonify, request
from src.config import Settings
from src.database import DatabaseManager
from src.bigquery import BigQueryManager
from src.metrics import MetricsCollector
from src.orchestrator import DataOrchestrator

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Cache em memória (TTL 45s) para dashboard rápido
_CACHE_TTL = 45
_cache = {}  # key -> (timestamp, value)

def _cached(key):
    if key in _cache:
        ts, val = _cache[key]
        if time.time() - ts < _CACHE_TTL:
            return val
    return None

def _set_cache(key, value):
    _cache[key] = (time.time(), value)

# Headers para o browser cachear respostas (dashboard rápido)
def _cache_headers():
    return {"Cache-Control": "public, max-age=45"}


class _StubDbManager:
    """
    Stub quando na Vercel sem BigQuery disponível.
    Na Vercel não existe MySQL (localhost:3306); este stub evita tentativa de conexão
    e retorna dados vazios para o dashboard carregar sem erro.
    """
    def get_table_count(self, table_name: str) -> int:
        return 0
    def execute_query(self, query: str, params=None):
        return []
    def table_ref(self, table_name: str) -> str:
        return table_name
    def create_table(self, table_name: str, schema: dict) -> bool:
        return True


# Inicializar: na Vercel NUNCA usar MySQL; localmente BigQuery primeiro, senão MySQL
settings = Settings()
gcp = settings.gcp
_vercel = os.environ.get("VERCEL") == "1"

if _vercel:
    # Vercel é serverless: não há MySQL. Usar só BigQuery ou stub.
    if gcp.GOOGLE_APPLICATION_CREDENTIALS and gcp.project_id and gcp.dataset_id:
        try:
            db_manager = BigQueryManager(gcp)
            _use_bigquery = True
        except Exception as e:
            logger.warning(
                "BigQuery indisponível na Vercel (%s). Configure GOOGLE_APPLICATION_CREDENTIALS_JSON e Build step.",
                e,
            )
            db_manager = _StubDbManager()
            _use_bigquery = False
    else:
        logger.warning(
            "Na Vercel só BigQuery é suportado (MySQL não existe). "
            "Configure GCP_PROJECT_ID, BIGQUERY_DATASET e GOOGLE_APPLICATION_CREDENTIALS_JSON."
        )
        db_manager = _StubDbManager()
        _use_bigquery = False
elif gcp.GOOGLE_APPLICATION_CREDENTIALS and gcp.project_id and gcp.dataset_id:
    try:
        db_manager = BigQueryManager(gcp)
        _use_bigquery = True
    except Exception as e:
        logger.warning(f"BigQuery indisponível ({e}), usando MySQL")
        db_manager = DatabaseManager(settings.database)
        _use_bigquery = False
else:
    db_manager = DatabaseManager(settings.database)
    _use_bigquery = False

_executor = ThreadPoolExecutor(max_workers=20)
TABLES_STATS = [
    'clientes', 'produtos', 'servicos', 'categorias',
    'contas_receber', 'contas_pagar', 'extrato',
    'ordem_servico', 'contas_dre',
    'pedido_vendas', 'pedidos_compra', 'crm_oportunidades', 'etapas_faturamento', 'produto_fornecedor',
    'servico_resumo', 'vendas_resumo', 'nfse', 'nf_consultar'
]


@app.route('/')
def index():
    """Página principal do dashboard."""
    return render_template('index.html')
@app.route('/api/run-coleta', methods=['POST'])
def run_coleta():
    """Dispara a coleta Omie -> BigQuery. Síncrono; invalida cache ao terminar."""
    try:
        orch = DataOrchestrator(settings)
        results = orch.run_collections(parallel=False)
        orch.cleanup()
        _cache.clear()
        total = sum(r.get("records", 0) for r in results)
        return jsonify({
            "success": True,
            "message": f"Coleta concluída. Total: {total} registros.",
            "results": results
        }), 200
    except Exception as e:
        logger.error(f"Erro ao rodar coleta: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/stats')
def get_stats():
    """Estatísticas gerais (cache 45s, contagens em paralelo). Use ?refresh=1 para ignorar cache."""
    if not request.args.get("refresh"):
        cached = _cached("stats")
        if cached is not None:
            return jsonify(cached), 200, _cache_headers()

    try:
        stats = {}

        def _count_one(table):
            try:
                if _use_bigquery:
                    return table, db_manager.get_table_count(table)
                r = db_manager.execute_query(f"SELECT COUNT(*) as total FROM {table}")
                return table, (r[0]['total'] if r else 0)
            except Exception as e:
                logger.warning(f"Erro ao contar {table}: {str(e)}")
                return table, 0

        futures = {_executor.submit(_count_one, t): t for t in TABLES_STATS}
        for fut in as_completed(futures):
            table, count = fut.result()
            stats[table] = count

        stats['total_geral'] = sum(v for k, v in stats.items() if k != 'total_geral')
        out = {'success': True, 'data': stats}
        _set_cache("stats", out)
        return jsonify(out), 200, _cache_headers()
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/financial')
def get_financial():
    """Dados financeiros (cache 45s, duas queries em paralelo)."""
    cached = _cached("financial")
    if cached is not None:
        return jsonify(cached), 200, _cache_headers()

    try:
        financial_data = {}
        tbl_cr = db_manager.table_ref("contas_receber") if _use_bigquery else "contas_receber"
        tbl_cp = db_manager.table_ref("contas_pagar") if _use_bigquery else "contas_pagar"

        def _query_cr():
            try:
                r = db_manager.execute_query(f"""
                    SELECT COUNT(*) as total, SUM(valor_documento) as total_valor,
                           SUM(valor_pago) as total_pago, SUM(saldo) as total_saldo
                    FROM {tbl_cr}
                """)
                return 'contas_receber', (r[0] if r else {})
            except Exception as e:
                logger.warning(f"Erro contas a receber: {str(e)}")
                return 'contas_receber', {}

        def _query_cp():
            try:
                r = db_manager.execute_query(f"""
                    SELECT COUNT(*) as total, SUM(valor_documento) as total_valor,
                           SUM(valor_pago) as total_pago, SUM(saldo) as total_saldo
                    FROM {tbl_cp}
                """)
                return 'contas_pagar', (r[0] if r else {})
            except Exception as e:
                logger.warning(f"Erro contas a pagar: {str(e)}")
                return 'contas_pagar', {}

        f1, f2 = _executor.submit(_query_cr), _executor.submit(_query_cp)
        for k, v in [f1.result(), f2.result()]:
            financial_data[k] = v

        out = {'success': True, 'data': financial_data}
        _set_cache("financial", out)
        return jsonify(out), 200, _cache_headers()
    except Exception as e:
        logger.error(f"Erro ao obter dados financeiros: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tables/<table_name>')
def get_table_data(table_name):
    """Retorna dados de uma tabela específica."""
    try:
        # Validação básica de segurança (inclui faturamento e pedidos_compra)
        allowed_tables = [
            'clientes', 'produtos', 'servicos', 'categorias',
            'contas_receber', 'contas_pagar', 'extrato',
            'ordem_servico', 'contas_dre',
            'pedido_vendas', 'pedidos_compra', 'crm_oportunidades', 'etapas_faturamento', 'produto_fornecedor',
            'servico_resumo', 'vendas_resumo', 'nfse', 'nf_consultar'
        ]
        
        if table_name not in allowed_tables:
            return jsonify({
                'success': False,
                'error': 'Tabela não permitida'
            }), 400
        
        # Buscar dados (limitado a 50 para resposta rápida)
        tbl = db_manager.table_ref(table_name) if _use_bigquery else table_name
        data = db_manager.execute_query(f"SELECT * FROM {tbl} LIMIT 50")

        resp = jsonify({'success': True, 'data': data, 'count': len(data)})
        resp.headers["Cache-Control"] = "public, max-age=30"
        return resp
    except Exception as e:
        logger.error(f"Erro ao buscar dados da tabela {table_name}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/metrics')
def get_metrics():
    """Métricas de coleta (cache 45s)."""
    cached = _cached("metrics")
    if cached is not None:
        return jsonify(cached), 200, _cache_headers()

    try:
        tbl = db_manager.table_ref("api_metrics") if _use_bigquery else "api_metrics"
        try:
            db_manager.create_table('api_metrics', {
                'id': 'BIGINT PRIMARY KEY AUTO_INCREMENT',
                'operation': 'VARCHAR(100)',
                'duration': 'DECIMAL(10,2)',
                'success': 'TINYINT(1)',
                'records_count': 'INT',
                'error_message': 'TEXT',
                'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            })
        except Exception:
            pass

        if _use_bigquery:
            metrics = db_manager.execute_query(f"""
                SELECT 
                    operation,
                    AVG(duration) as avg_duration,
                    MIN(duration) as min_duration,
                    MAX(duration) as max_duration,
                    SUM(records_count) as total_records,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as error_count,
                    MAX(created_at) as last_execution
                FROM {tbl}
                WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
                GROUP BY operation
                ORDER BY last_execution DESC
            """)
            last_execution = db_manager.execute_query(f"""
                SELECT 
                    SUM(duration) as total_time,
                    COUNT(*) as total_operations,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_operations,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_operations,
                    SUM(records_count) as total_records,
                    MAX(created_at) as last_run
                FROM {tbl}
                WHERE created_at = (SELECT MAX(created_at) FROM {tbl})
            """)
        else:
            metrics = db_manager.execute_query("""
                SELECT 
                    operation,
                    AVG(duration) as avg_duration,
                    MIN(duration) as min_duration,
                    MAX(duration) as max_duration,
                    SUM(records_count) as total_records,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as error_count,
                    MAX(created_at) as last_execution
                FROM api_metrics
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
                GROUP BY operation
                ORDER BY last_execution DESC
            """)
            last_execution = db_manager.execute_query("""
                SELECT 
                    SUM(duration) as total_time,
                    COUNT(*) as total_operations,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_operations,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_operations,
                    SUM(records_count) as total_records,
                    MAX(created_at) as last_run
                FROM api_metrics
                WHERE created_at = (
                    SELECT MAX(created_at) FROM api_metrics
                )
            """)
        
        out = {
            'success': True,
            'data': {
                'operations': metrics or [],
                'last_execution': last_execution[0] if last_execution else {}
            }
        }
        _set_cache("metrics", out)
        return jsonify(out), 200, _cache_headers()
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("="*80)
    print("DASHBOARD - Sistema de Coleta Omie")
    print("="*80)
    print("Acesse: http://localhost:5000")
    print("="*80)
    app.run(debug=True, host='0.0.0.0', port=5000)
