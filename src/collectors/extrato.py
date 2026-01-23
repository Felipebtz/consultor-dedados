"""
Coletor de dados de Extrato.
NOTA: Este coletor requer uma conta corrente válida (nCodCC ou cCodIntCC).
Forneça o código manualmente ou configure no .env/testar_coletor.py
"""
from typing import Dict, Any, List
from src.collectors.base import BaseCollector
import logging

logger = logging.getLogger(__name__)


class ExtratoCollector(BaseCollector):
    """Coletor para dados de extrato."""
    
    def get_endpoint(self) -> str:
        return "financas/extrato/"
    
    def get_method(self) -> str:
        return "ListarExtrato"
    
    def get_table_name(self) -> str:
        return "extrato"
    
    def get_schema(self) -> Dict[str, str]:
        return {
            "id": "BIGINT PRIMARY KEY AUTO_INCREMENT",
            "codigo_conta_corrente": "BIGINT",
            "data": "DATE",
            "valor": "DECIMAL(15,2)",
            "tipo": "CHAR(1)",
            "descricao": "VARCHAR(255)",
            "numero_documento": "VARCHAR(50)",
            "saldo": "DECIMAL(15,2)",
            "codigo_lancamento": "BIGINT",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
    }
    
    def build_payload(
        self,
        codigo_conta_corrente: int = None,
        codigo_conta_corrente_integracao: str = None,
        data_inicio: str = None,
        data_fim: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Constrói o payload conforme documentação oficial da API Omie.
        https://app.omie.com.br/api/v1/financas/extrato/
        ListarExtrato - REQUER pelo menos nCodCC > 0 ou cCodIntCC não vazio.
        
        IMPORTANTE: Se ambos forem 0/vazios, retorna None para evitar erro 500.
        """
        # Valida se tem pelo menos uma conta corrente válida
        if (not codigo_conta_corrente or codigo_conta_corrente == 0) and not codigo_conta_corrente_integracao:
            logger.error(
                "❌ ERRO: Extrato requer uma conta corrente válida!\n"
                "Forneça pelo menos um dos seguintes:\n"
                "  - codigo_conta_corrente=<número> (ex: 123456)\n"
                "  - codigo_conta_corrente_integracao='<código>' (ex: 'CC001')\n\n"
                "Como obter o código:\n"
                "1. Acesse: https://app.omie.com.br\n"
                "2. Vá em: Financeiro > Contas Correntes\n"
                "3. Copie o código (nCodCC) ou código de integração (cCodIntCC)\n\n"
                "Exemplo de uso:\n"
                "  testar_coletor.py extrato --codigo_conta_corrente=123456\n"
                "  ou no código: kwargs['codigo_conta_corrente'] = 123456"
            )
            return None  # Retorna None para pular a coleta
        
        # Constrói payload com valores válidos
        payload = {}
        
        if codigo_conta_corrente and codigo_conta_corrente > 0:
            payload["nCodCC"] = codigo_conta_corrente
        else:
            payload["nCodCC"] = 0
            
        if codigo_conta_corrente_integracao:
            payload["cCodIntCC"] = codigo_conta_corrente_integracao
        else:
            payload["cCodIntCC"] = ""
            
        payload["dPeriodoInicial"] = data_inicio if data_inicio else ""
        payload["dPeriodoFinal"] = data_fim if data_fim else ""
        
        logger.info(f"✅ Payload Extrato: nCodCC={payload['nCodCC']}, cCodIntCC='{payload['cCodIntCC']}', "
                   f"dPeriodoInicial='{payload['dPeriodoInicial']}', dPeriodoFinal='{payload['dPeriodoFinal']}'")
        
        return payload
    
    
    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Sobrescreve collect para adicionar delays e melhor tratamento de erros.
        A validação de conta corrente é feita no build_payload.
        """
        import time
        
        # Adiciona delay antes de iniciar (Extrato pode ser mais lento)
        logger.info("⏳ Aguardando 2 segundos antes de coletar extrato...")
        time.sleep(2)
        
        try:
            # Chama o método collect do BaseCollector
            # O BaseCollector já verifica se build_payload retorna None
            return super().collect(**kwargs)
        except Exception as e:
            error_msg = str(e)
            
            # Tratamento específico para erros 500
            if "500" in error_msg or "too many 500" in error_msg.lower():
                logger.error(
                    "❌ Erro 500 ao coletar extrato. Possíveis causas:\n"
                    "1. Conta corrente informada não existe ou está inativa\n"
                    "2. Período informado não possui movimentações\n"
                    "3. API Omie temporariamente indisponível\n"
                    "4. Código da conta corrente incorreto\n\n"
                    "Verifique:\n"
                    "- Se o código da conta corrente está correto\n"
                    "- Se a conta está ativa no Omie\n"
                    "- Se há movimentações no período informado"
                )
            else:
                logger.error(f"❌ Erro ao coletar extrato: {error_msg}")
            
            raise
