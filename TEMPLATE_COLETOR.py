"""
Template para criar um novo coletor de dados.
Copie este arquivo e renomeie para o nome da sua API.
"""
from typing import Dict, Any
from src.collectors.base import BaseCollector


class SeuColetorCollector(BaseCollector):
    """
    Coletor para dados de [NOME DA API].
    
    INSTRUÇÕES:
    1. Renomeie a classe (ex: FornecedoresCollector)
    2. Preencha os métodos abaixo com as informações da API Omie
    3. Ajuste o schema conforme os campos retornados pela API
    4. Registre no __init__.py e orchestrator.py
    """
    
    def get_endpoint(self) -> str:
        """
        Retorna o endpoint da API Omie.
        Exemplo: "geral/clientes/", "financas/contareceber/"
        """
        return "geral/seu_endpoint/"  # ⬅️ ALTERE AQUI
    
    def get_method(self) -> str:
        """
        Retorna o método da API Omie.
        Exemplo: "ListarClientes", "ListarContasReceber"
        """
        return "ListarSeuMetodo"  # ⬅️ ALTERE AQUI
    
    def get_table_name(self) -> str:
        """
        Retorna o nome da tabela no banco de dados.
        Use minúsculas e underscore (ex: "contas_receber")
        """
        return "sua_tabela"  # ⬅️ ALTERE AQUI
    
    def get_schema(self) -> Dict[str, str]:
        """
        Define a estrutura da tabela no banco de dados.
        
        IMPORTANTE:
        - Sempre defina uma chave primária
        - Use tipos SQL apropriados (VARCHAR, INT, DECIMAL, DATE, DATETIME, TEXT)
        - Os campos created_at e updated_at são adicionados automaticamente
        - Ajuste os campos conforme a resposta da API Omie
        """
        return {
            # Chave primária (obrigatório)
            "codigo_principal": "VARCHAR(50) PRIMARY KEY",  # ⬅️ ALTERE AQUI
            
            # Campos específicos da API (adicione conforme necessário)
            "campo1": "VARCHAR(255)",
            "campo2": "VARCHAR(100)",
            "campo3": "INT",
            "campo4": "DECIMAL(15,2)",
            "campo5": "DATE",
            "campo6": "DATETIME",
            "campo7": "TEXT",
            "inativo": "CHAR(1)",
            
            # Campos de auditoria (já incluídos automaticamente, mas você pode adicionar)
            "data_cadastro": "DATETIME",
            "data_alteracao": "DATETIME",
            
            # Estes são adicionados automaticamente, não precisa incluir:
            # "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            # "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        }
    
    def build_payload(self, pagina: int = 1, registros_por_pagina: int = 500, **kwargs) -> Dict[str, Any]:
        """
        Constrói o payload para a requisição à API.
        
        Parâmetros comuns da Omie:
        - pagina: Número da página (padrão: 1)
        - registros_por_pagina: Quantidade de registros por página (padrão: 500)
        - apenas_importado_api: "N" ou "S"
        - ordernar_por: Campo para ordenação
        
        Para APIs com filtros específicos (datas, etc), adicione parâmetros:
        """
        return {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": "N",
            "ordernar_por": "CODIGO_PRINCIPAL"  # ⬅️ ALTERE AQUI
        }
        
        # EXEMPLO: Se precisar de filtros de data:
        # payload = {
        #     "pagina": pagina,
        #     "registros_por_pagina": registros_por_pagina,
        #     "apenas_importado_api": "N",
        #     "ordernar_por": "DATA"
        # }
        # 
        # if kwargs.get("data_inicio"):
        #     payload["data_inicial"] = kwargs["data_inicio"]
        # if kwargs.get("data_fim"):
        #     payload["data_final"] = kwargs["data_fim"]
        # 
        # return payload
