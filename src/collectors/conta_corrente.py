"""
Coletor de dados de Contas Correntes.
Necessário para obter códigos válidos para o coletor de Extrato.
"""
from typing import Dict, Any, List
from src.collectors.base import BaseCollector
import logging

logger = logging.getLogger(__name__)


class ContaCorrenteCollector(BaseCollector):
    """Coletor para dados de contas correntes."""
    
    def get_endpoint(self) -> str:
        # Tentando diferentes endpoints possíveis
        # Opção 1: financas/contacorrente/ (sem underscore)
        # Opção 2: geral/conta_corrente/
        # Opção 3: financas/conta_corrente/
        return "financas/contacorrente/"  # Tentando sem underscore primeiro
    
    def get_method(self) -> str:
        # Métodos possíveis: ListarContasCorrentes, ListarContaCorrente, ListarCC
        return "ListarContasCorrentes"
    
    def get_table_name(self) -> str:
        return "contas_correntes"
    
    def get_schema(self) -> Dict[str, str]:
        return {
            "id": "BIGINT PRIMARY KEY AUTO_INCREMENT",
            "codigo_conta_corrente": "BIGINT",
            "codigo_conta_corrente_integracao": "VARCHAR(50)",
            "descricao": "VARCHAR(255)",
            "banco": "VARCHAR(100)",
            "agencia": "VARCHAR(20)",
            "conta": "VARCHAR(50)",
            "saldo_inicial": "DECIMAL(15,2)",
            "saldo_atual": "DECIMAL(15,2)",
            "tipo": "VARCHAR(50)",
            "inativo": "CHAR(1)",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        }
    
    def build_payload(
        self,
        pagina: int = 1,
        registros_por_pagina: int = 200,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Constrói o payload conforme documentação oficial da API Omie.
        https://app.omie.com.br/api/v1/financas/conta_corrente/
        """
        return {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": "N"
        }
    
    def transform_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transforma os dados brutos da API para o formato do banco de dados.
        """
        transformed = []
        
        # Possíveis chaves onde os dados podem estar
        possible_keys = [
            "listaContasCorrentes",
            "contasCorrentes",
            "contas_correntes",
            "lista_contas_correntes",
            "data"
        ]
        
        data_list = None
        for key in possible_keys:
            if key in raw_data and isinstance(raw_data[key], list):
                data_list = raw_data[key]
                break
        
        if not data_list:
            logger.debug(f"Chaves disponíveis na resposta: {list(raw_data.keys())}")
            return transformed
        
        for item in data_list:
            if not isinstance(item, dict):
                continue
                
            transformed_item = {
                "codigo_conta_corrente": item.get("nCodCC") or item.get("codigo_conta_corrente"),
                "codigo_conta_corrente_integracao": item.get("cCodIntCC") or item.get("codigo_conta_corrente_integracao") or "",
                "descricao": item.get("cDescricao") or item.get("descricao") or "",
                "banco": item.get("cBanco") or item.get("banco") or "",
                "agencia": item.get("cAgencia") or item.get("agencia") or "",
                "conta": item.get("cConta") or item.get("conta") or "",
                "saldo_inicial": item.get("nSaldoInicial") or item.get("saldo_inicial") or 0,
                "saldo_atual": item.get("nSaldoAtual") or item.get("saldo_atual") or 0,
                "tipo": item.get("cTipo") or item.get("tipo") or "",
                "inativo": item.get("cInativo") or item.get("inativo") or "N"
            }
            
            transformed.append(transformed_item)
        
        return transformed
