"""
Coletor de dados de Ordens de Serviço.
"""
from typing import Dict, Any, List
from src.collectors.base import BaseCollector
import logging

logger = logging.getLogger(__name__)


class OrdemServicoCollector(BaseCollector):
    """Coletor para dados de ordens de serviço."""
    
    def get_endpoint(self) -> str:
        return "servicos/os/"
    
    def get_method(self) -> str:
        return "ListarOS"
    
    def get_table_name(self) -> str:
        return "ordem_servico"
    
    def get_schema(self) -> Dict[str, str]:
        return {
            #CONFIRA AQUI POIS PODE DÁ DUPLICACAO POR NÃO TER ID AUTOINCREMENT
            "codigo_os": "VARCHAR(50) PRIMARY KEY",
            "codigo_os_integracao": "VARCHAR(50)",
            "codigo_cliente": "VARCHAR(50)",
            "data_previsao": "DATE",
            "data_emissao": "DATE",
            "data_fechamento": "DATE",
            "valor_total": "DECIMAL(15,2)",
            "valor_desconto": "DECIMAL(15,2)",
            "valor_liquido": "DECIMAL(15,2)",
            "status": "VARCHAR(50)",
            "numero_pedido": "VARCHAR(50)",
            "observacao": "TEXT",
            "codigo_projeto": "VARCHAR(50)",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        }
    
    def supports_incremental(self) -> bool:
        return True

    def build_payload(
        self,
        pagina: int = 1,
        registros_por_pagina: int = 200,
        apenas_importado_api: str = "N",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Constrói o payload conforme documentação oficial da API Omie.
        Em modo incremental: filtrar_por_data_de, filtrar_por_data_ate, filtrar_apenas_alteracao.
        """
        payload = {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": apenas_importado_api
        }
        if kwargs.get("incremental") and kwargs.get("data_inicio") and kwargs.get("data_fim"):
            payload["filtrar_por_data_de"] = kwargs["data_inicio"]
            payload["filtrar_por_data_ate"] = kwargs["data_fim"]
            payload["filtrar_apenas_alteracao"] = "S"
        return payload
    
    def transform_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transforma os dados de ordens de serviço conforme documentação oficial.
        API Omie retorna: pagina, total_de_paginas, registros, total_de_registros, osCadastro (na raiz).
        """
        data_list = []
        # Formato exato da API (Postman): osCadastro na raiz
        if "osCadastro" in raw_data and isinstance(raw_data["osCadastro"], list):
            data_list = raw_data["osCadastro"]
            logger.info(f"Encontrados {len(data_list)} registros em 'osCadastro' (raiz)")
        # Resposta às vezes vem dentro do nome do método
        if not data_list and "ListarOS" in raw_data:
            inner = raw_data["ListarOS"]
            if isinstance(inner, dict) and "osCadastro" in inner and isinstance(inner["osCadastro"], list):
                data_list = inner["osCadastro"]
                logger.info(f"Encontrados {len(data_list)} registros em 'ListarOS.osCadastro'")
        
        # Conforme documentação: osListarResponse (wrapper alternativo)
        if not data_list and "osListarResponse" in raw_data:
            response = raw_data["osListarResponse"]
            if isinstance(response, dict):
                # Procura por chaves comuns que podem conter a lista
                for key in ["listaOS", "osCadastro", "cadastro", "lista"]:
                    if key in response and isinstance(response[key], list):
                        data_list = response[key]
                        logger.info(f"Encontrados {len(data_list)} registros em 'osListarResponse.{key}'")
                        break
                # Se não encontrou, pode ser que a resposta seja a lista diretamente
                if not data_list and isinstance(response, list):
                    data_list = response
                    logger.info(f"Encontrados {len(data_list)} registros em 'osListarResponse' (lista direta)")
            elif isinstance(response, list):
                data_list = response
                logger.info(f"Encontrados {len(data_list)} registros em 'osListarResponse'")
        
        # Tenta chaves alternativas
        possible_keys = [
            "listaOS",
            "osCadastro",
            "ordem_servico",
            "os_cadastro",
            "cadastro"
        ]
        
        if not data_list:
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
        # Conforme documentação: osCadastro contém Cabecalho, Departamentos, Email, etc.
        mapped_data = []
        for item in data_list:
            # A estrutura da API tem os dados principais em "Cabecalho"
            cabecalho = item.get("Cabecalho", {})
            info_cadastro = item.get("InfoCadastro", {})
            
            # Tenta diferentes formatos de campos (primeiro em Cabecalho, depois no item direto)
            codigo = (
                cabecalho.get("nCodOS") or
                cabecalho.get("nIdPed") or 
                item.get("nCodOS") or
                item.get("nIdPed") or 
                item.get("codigo_os") or 
                item.get("codigo") or 
                ""
            )
            
            # Número da OS
            numero_os = (
                cabecalho.get("cNumOS") or
                cabecalho.get("cNumPedido") or
                item.get("cNumOS") or
                item.get("cNumPedido") or
                ""
            )
            
            mapped_item = {
                "codigo_os": str(codigo) if codigo else "",
                "codigo_os_integracao": str(
                    cabecalho.get("cCodIntOS") or
                    item.get("cCodIntOS") or 
                    item.get("codigo_os_integracao") or 
                    item.get("codigo_integracao") or 
                    ""
                ),
                "codigo_cliente": str(
                    cabecalho.get("nCodCli") or
                    cabecalho.get("nCodCliente") or 
                    item.get("nCodCli") or
                    item.get("nCodCliente") or 
                    item.get("codigo_cliente") or
                    ""
                ),
                "data_previsao": (
                    cabecalho.get("dDtPrevisao") or 
                    item.get("dDtPrevisao") or 
                    item.get("data_previsao") or 
                    None
                ),
                "data_emissao": (
                    info_cadastro.get("dDtInc") or
                    cabecalho.get("dDtEmissao") or 
                    item.get("dDtEmissao") or 
                    item.get("data_emissao") or 
                    None
                ),
                "data_fechamento": (
                    info_cadastro.get("dDtFat") or
                    cabecalho.get("dDtFechamento") or 
                    item.get("dDtFechamento") or 
                    item.get("data_fechamento") or 
                    None
                ),
                "valor_total": float(
                    cabecalho.get("nValorTot") or
                    cabecalho.get("nValorTotal") or 
                    item.get("nValorTotal") or 
                    item.get("valor_total") or 
                    0
                ),
                "valor_desconto": float(
                    cabecalho.get("nValorDesconto") or
                    item.get("nValorDesconto") or 
                    item.get("valor_desconto") or
                    0
                ),
                "valor_liquido": float(
                    cabecalho.get("nValorLiquido") or
                    item.get("nValorLiquido") or 
                    item.get("valor_liquido") or
                    0
                ),
                "status": str(
                    cabecalho.get("cEtapa") or
                    cabecalho.get("cStatus") or 
                    item.get("cStatus") or 
                    item.get("status") or
                    ""
                ),
                "numero_pedido": str(
                    numero_os or
                    cabecalho.get("cNumPedido") or 
                    item.get("cNumPedido") or 
                    item.get("numero_pedido") or
                    ""
                ),
                "observacao": str(
                    item.get("InformacoesAdicionais", {}).get("cDadosAdicNF") or
                    item.get("cObservacao") or 
                    item.get("observacao") or
                    ""
                ),
                "codigo_projeto": str(
                    item.get("InformacoesAdicionais", {}).get("nCodProj") or
                    item.get("nCodProjeto") or 
                    item.get("codigo_projeto") or
                    ""
                )
            }
            
            # Remove campos vazios mas mantém codigo_os
            mapped_item = {k: v for k, v in mapped_item.items() if v or k in ["codigo_os"]}
            
            # Aceita se tiver código OU número do pedido OU número da OS
            if mapped_item.get("codigo_os") or mapped_item.get("numero_pedido"):
                mapped_data.append(mapped_item)
            else:
                logger.debug(f"Registro ignorado (sem código nem número). Chaves disponíveis: {list(item.keys())[:5]}")
        
        logger.info(f"Total de {len(mapped_data)} registros mapeados para inserção")
        return mapped_data
