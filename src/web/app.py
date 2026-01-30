"""
Aplicação Web Flask para Dashboard do Sistema de Coleta Omie.
"""
from flask import Flask, render_template, jsonify
from src.config import Settings
from src.database import DatabaseManager
from src.metrics import MetricsCollector
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Inicializar componentes
settings = Settings()
db_manager = DatabaseManager(settings.database)


@app.route('/')
def index():
    """Página principal do dashboard."""
    return render_template('index.html')


@app.route('/api/stats')
def get_stats():
    """Retorna estatísticas gerais do sistema."""
    try:
        stats = {}
        
        # Lista de tabelas
        tables = [
            'clientes', 'produtos', 'servicos', 'categorias',
            'contas_receber', 'contas_pagar', 'extrato',
            'ordem_servico', 'contas_dre',
            'pedido_vendas', 'crm_oportunidades', 'etapas_faturamento', 'produto_fornecedor'
        ]
        
        # Conta registros em cada tabela
        for table in tables:
            try:
                result = db_manager.execute_query(f"SELECT COUNT(*) as total FROM {table}")
                stats[table] = result[0]['total'] if result else 0
            except Exception as e:
                logger.warning(f"Erro ao contar registros em {table}: {str(e)}")
                stats[table] = 0
        
        # Total geral (soma apenas contagens das tabelas)
        stats['total_geral'] = sum(v for k, v in stats.items() if k != 'total_geral')
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/financial')
def get_financial():
    """Retorna dados financeiros."""
    try:
        financial_data = {}
        
        # Contas a Receber
        try:
            contas_receber = db_manager.execute_query("""
                SELECT 
                    COUNT(*) as total,
                    SUM(valor_documento) as total_valor,
                    SUM(valor_pago) as total_pago,
                    SUM(saldo) as total_saldo
                FROM contas_receber
            """)
            financial_data['contas_receber'] = contas_receber[0] if contas_receber else {}
        except Exception as e:
            logger.warning(f"Erro ao buscar contas a receber: {str(e)}")
            financial_data['contas_receber'] = {}
        
        # Contas a Pagar
        try:
            contas_pagar = db_manager.execute_query("""
                SELECT 
                    COUNT(*) as total,
                    SUM(valor_documento) as total_valor,
                    SUM(valor_pago) as total_pago,
                    SUM(saldo) as total_saldo
                FROM contas_pagar
            """)
            financial_data['contas_pagar'] = contas_pagar[0] if contas_pagar else {}
        except Exception as e:
            logger.warning(f"Erro ao buscar contas a pagar: {str(e)}")
            financial_data['contas_pagar'] = {}
        
        return jsonify({
            'success': True,
            'data': financial_data
        })
    except Exception as e:
        logger.error(f"Erro ao obter dados financeiros: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/tables/<table_name>')
def get_table_data(table_name):
    """Retorna dados de uma tabela específica."""
    try:
        # Validação básica de segurança
        allowed_tables = [
            'clientes', 'produtos', 'servicos', 'categorias',
            'contas_receber', 'contas_pagar', 'extrato',
            'ordem_servico', 'contas_dre',
            'pedido_vendas', 'crm_oportunidades', 'etapas_faturamento', 'produto_fornecedor'
        ]
        
        if table_name not in allowed_tables:
            return jsonify({
                'success': False,
                'error': 'Tabela não permitida'
            }), 400
        
        # Buscar dados (limitado a 100 registros)
        data = db_manager.execute_query(f"SELECT * FROM {table_name} LIMIT 100")
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })
    except Exception as e:
        logger.error(f"Erro ao buscar dados da tabela {table_name}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/metrics')
def get_metrics():
    """Retorna métricas de tempo de coleta das APIs."""
    try:
        # Criar tabela de métricas se não existir
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
        except:
            pass  # Tabela já existe
        
        # Buscar últimas métricas (últimas 50 execuções)
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
        
        # Buscar última execução completa
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
        
        return jsonify({
            'success': True,
            'data': {
                'operations': metrics or [],
                'last_execution': last_execution[0] if last_execution else {}
            }
        })
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("="*80)
    print("DASHBOARD - Sistema de Coleta Omie")
    print("="*80)
    print("Acesse: http://localhost:5000")
    print("="*80)
    app.run(debug=True, host='0.0.0.0', port=5000)
