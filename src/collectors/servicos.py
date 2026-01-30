"""
Coletor de dados de Serviços.
"""
from typing import Dict, Any, List
from src.collectors.base import BaseCollector
import logging

logger = logging.getLogger(__name__)


class ServicosCollector(BaseCollector):
    """Coletor para dados de serviços."""
    
    def get_endpoint(self) -> str:
        return "servicos/servico/"
    
    def get_method(self) -> str:
        return "ListarCadastroServico"
    
    def get_table_name(self) -> str:
        return "servicos"
    
    def get_schema(self) -> Dict[str, str]:
        return {
            "codigo_servico": "VARCHAR(50) PRIMARY KEY",
            "codigo_servico_integracao": "VARCHAR(50)",
            "descricao": "VARCHAR(255)",
            "valor_unitario": "DECIMAL(15,2)",
            "categoria": "VARCHAR(100)",
            "inativo": "CHAR(1)",
            "data_cadastro": "DATETIME",
            "data_alteracao": "DATETIME",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        }
    
    def build_payload(self, pagina: int = 1, registros_por_pagina: int = 200, **kwargs) -> Dict[str, Any]:
        """
        Constrói o payload conforme documentação oficial da API Omie.
        https://app.omie.com.br/api/v1/servicos/servico/
        Usa nPagina e nRegPorPagina conforme documentação.
        """
        return {
            "nPagina": pagina,
            "nRegPorPagina": registros_por_pagina
        }
    
    def transform_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transforma os dados de serviços.
        A API pode retornar em diferentes formatos.
        """
        # Log para debug
        logger.debug(f"Chaves disponíveis na resposta: {list(raw_data.keys())}")
        
        # Tenta diferentes chaves possíveis
        possible_keys = [
            "listaServicosCadastro",
            "servicos_cadastro",
            "servico_cadastro",
            "cadastro",
            "srvListarResponse",  # Formato da API
            "listaServicoCadastro"  # Formato alternativo
        ]
        
        data_list = []
        for key in possible_keys:
            if key in raw_data:
                data = raw_data[key]
                logger.debug(f"Encontrada chave '{key}': tipo={type(data)}")
                if isinstance(data, list):
                    data_list = data
                    logger.info(f"Encontrados {len(data_list)} registros em '{key}'")
                    break
                elif isinstance(data, dict):
                    # Se é um dict, pode ter uma lista dentro
                    for sub_key, sub_value in data.items():
                        if isinstance(sub_value, list):
                            data_list = sub_value
                            logger.info(f"Encontrados {len(data_list)} registros em '{key}.{sub_key}'")
                            break
                    if data_list:
                        break
        
        # Se não encontrou, tenta buscar qualquer lista no primeiro nível
        if not data_list:
            for key, value in raw_data.items():
                if isinstance(value, list) and len(value) > 0:
                    if isinstance(value[0], dict):
                        data_list = value
                        logger.info(f"Encontrados {len(data_list)} registros em '{key}' (busca genérica)")
                        break
        
        # Se ainda não encontrou, usa fallback
        if not data_list:
            logger.warning(f"Nenhum dado encontrado. Chaves disponíveis: {list(raw_data.keys())}")
            data_list = super().transform_data(raw_data)
        
        # Mapeia campos da API para campos do schema
        mapped_data = []
        for item in data_list:
            # Tenta diferentes formatos de campos
            codigo = (
                item.get("nCodServico") or 
                item.get("codigo_servico") or 
                item.get("codigo") or 
                item.get("nCodigo") or
                ""
            )
            
            mapped_item = {
                "codigo_servico": str(codigo) if codigo else "",
                "codigo_servico_integracao": str(
                    item.get("cCodIntServico") or 
                    item.get("codigo_servico_integracao") or 
                    item.get("codigo_integracao") or 
                    item.get("cCodInt") or
                    ""
                ),
                "descricao": str(
                    item.get("cDescricao") or 
                    item.get("descricao") or 
                    item.get("cNome") or
                    ""
                ),
                "valor_unitario": float(
                    item.get("nValorUnitario") or 
                    item.get("valor_unitario") or 
                    item.get("nValor") or
                    0
                ),
                "categoria": str(
                    item.get("cCategoria") or 
                    item.get("categoria") or
                    ""
                ),
                "inativo": str(
                    item.get("cInativo") or 
                    item.get("inativo") or 
                    item.get("cAtivo") or
                    "N"
                ),
                "data_cadastro": (
                    item.get("dDtInc") or 
                    item.get("data_cadastro") or 
                    item.get("dDataInc") or
                    None
                ),
                "data_alteracao": (
                    item.get("dDtAlt") or 
                    item.get("data_alteracao") or 
                    item.get("dDataAlt") or
                    None
                )
            }
            
            # Remove campos vazios mas mantém codigo_servico
            mapped_item = {k: v for k, v in mapped_item.items() if v or k in ["codigo_servico"]}
            
            # Aceita se tiver código OU descrição
            if mapped_item.get("codigo_servico") or mapped_item.get("descricao"):
                mapped_data.append(mapped_item)
            else:
                logger.debug(f"Registro ignorado (sem código nem descrição): {list(item.keys())[:5]}")
        
        logger.info(f"Total de {len(mapped_data)} registros mapeados para inserção")
        return mapped_data
