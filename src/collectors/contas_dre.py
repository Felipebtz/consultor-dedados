"""
Coletor de dados de Contas DRE.
"""
from typing import Dict, Any, List
from src.collectors.base import BaseCollector
import logging

logger = logging.getLogger(__name__)


class ContasDRECollector(BaseCollector):
    """Coletor para dados de contas DRE."""
    
    def get_endpoint(self) -> str:
        return "geral/dre/"
    
    def get_method(self) -> str:
        return "ListarCadastroDRE"
    
    def get_table_name(self) -> str:
        return "contas_dre"
    
    def get_schema(self) -> Dict[str, str]:
        return {
            "codigo_conta_dre": "VARCHAR(50) PRIMARY KEY",
            "codigo_conta_dre_integracao": "VARCHAR(50)",
            "descricao": "VARCHAR(255)",
            "tipo": "VARCHAR(50)",
            "nivel": "INT",
            "conta_pai": "VARCHAR(50)",
            "natureza": "VARCHAR(50)",
            "inativo": "CHAR(1)",
            "data_cadastro": "DATETIME",
            "data_alteracao": "DATETIME",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        }
    
    def build_payload(self, **kwargs) -> Dict[str, Any]:
        """
        Constrói o payload conforme documentação oficial da API Omie.
        https://app.omie.com.br/api/v1/geral/dre/
        """
        return {
            "apenasContasAtivas": "N"
        }
    
    def transform_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transforma os dados de contas DRE conforme documentação oficial.
        Retorno: dreCadastroListResponse com dreLista (array)
        """
        # Log para debug
        logger.debug(f"Chaves disponíveis na resposta: {list(raw_data.keys())}")
        
        # Conforme documentação: dreCadastroListResponse contém dreLista
        data_list = []
        
        # Tenta a chave oficial primeiro
        if "dreCadastroListResponse" in raw_data:
            response = raw_data["dreCadastroListResponse"]
            if isinstance(response, dict) and "dreLista" in response:
                data_list = response["dreLista"]
                logger.info(f"Encontrados {len(data_list)} registros em 'dreCadastroListResponse.dreLista'")
            elif isinstance(response, list):
                data_list = response
                logger.info(f"Encontrados {len(data_list)} registros em 'dreCadastroListResponse'")
        
        # Tenta chave direta
        if not data_list and "dreLista" in raw_data:
            data_list = raw_data["dreLista"]
            if isinstance(data_list, list):
                logger.info(f"Encontrados {len(data_list)} registros em 'dreLista'")
        
        # Fallback: busca qualquer lista
        if not data_list:
            for key, value in raw_data.items():
                if isinstance(value, list) and len(value) > 0:
                    if isinstance(value[0], dict):
                        data_list = value
                        logger.info(f"Encontrados {len(data_list)} registros em '{key}' (busca genérica)")
                        break
                elif isinstance(value, dict):
                    # Procura dentro do dict
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, list) and len(sub_value) > 0:
                            if isinstance(sub_value[0], dict):
                                data_list = sub_value
                                logger.info(f"Encontrados {len(data_list)} registros em '{key}.{sub_key}'")
                                break
                    if data_list:
                        break
        
        # Se ainda não encontrou, usa fallback do BaseCollector
        if not data_list:
            logger.warning(f"Nenhum dado encontrado. Chaves disponíveis: {list(raw_data.keys())}")
            data_list = super().transform_data(raw_data)
        
        # Mapeia campos conforme documentação oficial:
        # codigoDRE, descricaoDRE, nivelDRE, sinalDRE, totalizaDRE, naoExibirDRE
        mapped_data = []
        for item in data_list:
            mapped_item = {
                "codigo_conta_dre": str(
                    item.get("codigoDRE") or 
                    item.get("codigo_conta_dre") or
                    ""
                ),
                "codigo_conta_dre_integracao": str(
                    item.get("codigoDRE") or  # Pode usar o mesmo código
                    item.get("codigo_conta_dre_integracao") or
                    ""
                ),
                "descricao": str(
                    item.get("descricaoDRE") or 
                    item.get("descricao") or
                    ""
                ),
                "tipo": str(
                    item.get("sinalDRE") or  # Sinal pode ser usado como tipo
                    item.get("tipo") or
                    ""
                ),
                "nivel": int(
                    item.get("nivelDRE") or 
                    item.get("nivel") or
                    0
                ) if (item.get("nivelDRE") or item.get("nivel")) else 0,
                "conta_pai": "",  # Não disponível na API
                "natureza": str(
                    item.get("totalizaDRE") or  # Totalizadora pode indicar natureza
                    item.get("natureza") or
                    ""
                ),
                "inativo": str(
                    "S" if item.get("naoExibirDRE") == "S" else "N" or
                    item.get("inativo") or
                    "N"
                ),
                "data_cadastro": None,  # Não disponível na API
                "data_alteracao": None  # Não disponível na API
            }
            
            # Remove campos vazios mas mantém codigo_conta_dre
            mapped_item = {k: v for k, v in mapped_item.items() if v or k in ["codigo_conta_dre"]}
            
            # Aceita se tiver código OU descrição
            if mapped_item.get("codigo_conta_dre") or mapped_item.get("descricao"):
                mapped_data.append(mapped_item)
            else:
                logger.debug(f"Registro ignorado (sem código nem descrição): {list(item.keys())[:5]}")
        
        logger.info(f"Total de {len(mapped_data)} registros mapeados para inserção")
        return mapped_data

# 10:26:51,218 - src.collectors.base - ERROR - Erro ao coletar dados: HTTPSConnectionPool(host='app.omie.com.br', port=443): Max retries exceeded with url: /api/v1/financas/extrato/ (Caused by ResponseError('too many 500 error responses'))
#