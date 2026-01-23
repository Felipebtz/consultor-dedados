"""
Classe base para coletores de dados.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.core.interfaces import IDataCollector, IApiClient
import logging

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


class BaseCollector(IDataCollector, ABC):
    """
    Classe base abstrata para todos os coletores de dados.
    Implementa o Template Method Pattern.
    """
    
    def __init__(self, api_client: IApiClient):
        """
        Inicializa o coletor base.
        
        Args:
            api_client: Cliente da API para fazer requisições
        """
        self.api_client = api_client
    
    @abstractmethod
    def get_endpoint(self) -> str:
        """Retorna o endpoint da API."""
        pass
    
    @abstractmethod
    def get_method(self) -> str:
        """Retorna o método da API."""
        pass
    
    @abstractmethod
    def get_table_name(self) -> str:
        """Retorna o nome da tabela no banco de dados."""
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, str]:
        """
        Retorna o schema da tabela.
        
        Returns:
            Dicionário com nome da coluna como chave e tipo SQL como valor
        """
        pass
    
    def build_payload(self, **kwargs) -> Dict[str, Any]:
        """
        Constrói o payload para a requisição.
        Pode ser sobrescrito por classes filhas.
        
        Args:
            **kwargs: Parâmetros específicos do coletor
            
        Returns:
            Payload formatado
        """
        return kwargs
    
    def transform_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transforma os dados brutos da API em formato para o banco.
        Pode ser sobrescrito por classes filhas.
        
        Args:
            raw_data: Dados brutos da API
            
        Returns:
            Lista de dicionários com dados transformados
        """
        # Mapeamento de chaves comuns da API Omie
        possible_keys = [
            "clientes_cadastro",
            "produto_servico_cadastro",
            "servicos_cadastro",
            "categoria_cadastro",
            "conta_receber_cadastro",
            "conta_pagar_cadastro",
            "extrato",
            "movimento",
            "conta_corrente",
            "contrato",
            "ordem_servico",
            "projeto",
            "tipo_faturamento",
            "conta_dre",
            "fornecedor_cadastro",
            "vendedor_cadastro",
            "pedido_venda_produto",
            "osCadastro",  # Formato alternativo
            "lista_os_cadastro",  # Formato alternativo
            "listaServicosCadastro",  # Serviços
            "listaCategoriaCadastro",  # Categorias
        ]
        
        # Procura por chaves conhecidas
        for key in possible_keys:
            if key in raw_data:
                data = raw_data[key]
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and "cadastro" in data:
                    # Algumas APIs retornam {"cadastro": [...]}
                    if isinstance(data["cadastro"], list):
                        return data["cadastro"]
        
        # Tenta encontrar qualquer lista no primeiro nível
        for key, value in raw_data.items():
            if isinstance(value, list) and len(value) > 0:
                # Verifica se é uma lista de dicionários (dados válidos)
                if isinstance(value[0], dict):
                    return value
        
        # Se não encontrou nada, loga detalhes para debug
        logger.warning(f"Nenhum dado encontrado na resposta. Chaves disponíveis: {list(raw_data.keys())}")
        
        # Tenta logar um exemplo da estrutura para debug
        if raw_data:
            sample_key = list(raw_data.keys())[0]
            sample_value = raw_data[sample_key]
            logger.debug(f"Exemplo de chave '{sample_key}': tipo={type(sample_value)}, valor={str(sample_value)[:200] if not isinstance(sample_value, (dict, list)) else 'estrutura complexa'}")
        
        return []
    
    def collect(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Coleta dados da API.
        Template Method que define o fluxo padrão.
        Suporta paginação automática.
        
        Args:
            **kwargs: Parâmetros específicos do coletor
            
        Returns:
            Lista de dicionários com os dados coletados
        """
        all_data = []
        pagina = kwargs.get('pagina', 1)
        # Padrão de 50 registros por página (conforme documentação Omie)
        registros_por_pagina = kwargs.get('registros_por_pagina', 50)
        
        try:
            # Para APIs sem paginação (ex: extrato, ordem_servico), coleta apenas uma vez
            max_iterations = kwargs.get('max_iterations', 1000)  # Limite de segurança
            iteration = 0
            
            while iteration < max_iterations:
                endpoint = self.get_endpoint()
                method = self.get_method()
                
                # Atualiza paginação no payload
                payload = self.build_payload(pagina=pagina, registros_por_pagina=registros_por_pagina, **kwargs)
                
                # Se build_payload retornar None, significa que a coleta deve ser pulada
                if payload is None:
                    logger.info("Coleta pulada: build_payload retornou None (parâmetros inválidos ou coleta não aplicável)")
                    break
                
                # Detecta formato de paginação usado
                usa_paginacao = any(k in payload for k in ['pagina', 'nPagina', 'registros_por_pagina', 'nRegPorPagina'])
                
                # Se não usa paginação, coleta apenas uma vez
                if not usa_paginacao and iteration > 0:
                    break
                
                if not usa_paginacao:
                    logger.info(f"Coletando dados: {endpoint}/{method} (sem paginação)")
                else:
                    logger.info(f"Coletando dados: {endpoint}/{method} - Página {pagina}")
                
                # Adiciona delay entre requisições para evitar rate limiting
                if iteration > 0:
                    import time
                    time.sleep(0.5)  # 500ms entre requisições
                
                response = self.api_client.request(endpoint, method, payload)
                
                # Verifica erros na resposta
                if "faultstring" in response:
                    logger.error(f"Erro na API: {response['faultstring']}")
                    break
                
                # Transforma os dados
                page_data = self.transform_data(response)
                
                # Log de debug se não encontrou dados
                if not page_data:
                    logger.warning(f"Nenhum dado transformado na página {pagina}. Chaves na resposta: {list(response.keys())[:10]}")
                    # Se não usa paginação, para após primeira tentativa
                    if not usa_paginacao:
                        break
                    # Se primeira página não tem dados, para
                    if pagina == 1:
                        break
                    # Se páginas seguintes não têm dados, para
                    break
                
                all_data.extend(page_data)
                logger.info(f"Página {pagina}: {len(page_data)} registros coletados")
                
                # Se não usa paginação, para após primeira coleta
                if not usa_paginacao:
                    break
                
                # Verifica se há mais páginas (formato Omie: clientes_listfull_response)
                total_de_paginas = response.get('total_de_paginas', 0)
                total_de_registros = response.get('total_de_registros', 0)
                
                if total_de_paginas:
                    # Se já coletou todas as páginas, para
                    if pagina >= total_de_paginas:
                        break
                elif total_de_registros:
                    # Fallback: calcula total de páginas
                    # Para serviços, usa nRegPorPagina do payload
                    reg_por_pag = payload.get('nRegPorPagina') or payload.get('registros_por_pagina', registros_por_pagina)
                    total_paginas = (total_de_registros + reg_por_pag - 1) // reg_por_pag
                    if pagina >= total_paginas:
                        break
                
                # Se a página retornou menos registros que o esperado, não há mais páginas
                reg_por_pag = payload.get('nRegPorPagina') or payload.get('registros_por_pagina', registros_por_pagina)
                if len(page_data) < reg_por_pag:
                    break
                
                pagina += 1
                iteration += 1
            
            logger.info(f"Total de dados coletados: {len(all_data)} registros")
            return all_data
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados: {str(e)}")
            return all_data  # Retorna o que foi coletado até o erro
