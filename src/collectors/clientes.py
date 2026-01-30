"""
Coletor de dados de Clientes.
"""
from typing import Dict, Any, List
from src.collectors.base import BaseCollector
import logging

logger = logging.getLogger(__name__)


class ClientesCollector(BaseCollector):
    """Coletor para dados de clientes."""
    
    def get_endpoint(self) -> str:
        return "geral/clientes/"
    
    def get_method(self) -> str:
        return "ListarClientes"
    
    def get_table_name(self) -> str:
        return "clientes"
    
    def get_schema(self) -> Dict[str, str]:
        return {
            "codigo_cliente_omie": "VARCHAR(50) PRIMARY KEY",
            "codigo_cliente_integracao": "VARCHAR(50)",
            "razao_social": "VARCHAR(255)",
            "nome_fantasia": "VARCHAR(255)",
            "cnpj_cpf": "VARCHAR(20)",
            "email": "VARCHAR(255)",
            "telefone1_ddd": "VARCHAR(5)",
            "telefone1_numero": "VARCHAR(20)",
            "endereco": "VARCHAR(255)",
            "endereco_numero": "VARCHAR(20)",
            "bairro": "VARCHAR(100)",
            "cidade": "VARCHAR(100)",
            "estado": "VARCHAR(2)",
            "cep": "VARCHAR(10)",
            "inscricao_estadual": "VARCHAR(50)",
            "inscricao_municipal": "VARCHAR(50)",
            "pessoa_fisica": "CHAR(1)",
            "inativo": "CHAR(1)",
            "data_cadastro": "DATETIME",
            "data_alteracao": "DATETIME",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        }
    
    def build_payload(self, pagina: int = 1, registros_por_pagina: int = 200, **kwargs) -> Dict[str, Any]:
        """
        Constrói o payload conforme documentação da API Omie.
        Parâmetros do clientes_list_request:
        - pagina: Número da página
        - registros_por_pagina: Quantidade de registros por página (padrão: 50)
        - apenas_importado_api: "N" ou "S"
        """
        return {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": "N"
        }
    
    def transform_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transforma os dados de clientes.
        A API retorna em clientes_cadastro.
        """
        data_list = []
        if "clientes_cadastro" in raw_data:
            data_list = raw_data["clientes_cadastro"]
        else:
            # Fallback para busca genérica
            data_list = super().transform_data(raw_data)
        
        # Mapeia campos da API para campos do schema
        mapped_data = []
        for item in data_list:
            # Extrai dados do endereço se estiver aninhado
            endereco_data = item.get("endereco", {}) if isinstance(item.get("endereco"), dict) else {}
            telefone_data = item.get("telefone1", {}) if isinstance(item.get("telefone1"), dict) else {}
            
            mapped_item = {
                "codigo_cliente_omie": str(item.get("codigo_cliente_omie") or item.get("nCodCliente") or item.get("codigo") or ""),
                "codigo_cliente_integracao": str(item.get("codigo_cliente_integracao") or item.get("cCodIntCliente") or item.get("codigo_integracao") or ""),
                "razao_social": str(item.get("razao_social") or item.get("cNome") or endereco_data.get("cNome") or ""),
                "nome_fantasia": str(item.get("nome_fantasia") or item.get("cNomeFantasia") or ""),
                "cnpj_cpf": str(item.get("cnpj_cpf") or item.get("cCnpjCpf") or ""),
                "email": str(item.get("email") or item.get("cEmail") or ""),
                "telefone1_ddd": str(telefone_data.get("ddd") or item.get("telefone1_ddd") or item.get("cDDD") or ""),
                "telefone1_numero": str(telefone_data.get("numero") or item.get("telefone1_numero") or item.get("cTelefone") or ""),
                "endereco": str(endereco_data.get("endereco") or item.get("endereco") or item.get("cEndereco") or ""),
                "endereco_numero": str(endereco_data.get("numero") or item.get("endereco_numero") or item.get("cNumero") or ""),
                "bairro": str(endereco_data.get("bairro") or item.get("bairro") or item.get("cBairro") or ""),
                "cidade": str(endereco_data.get("cidade") or item.get("cidade") or item.get("cCidade") or ""),
                "estado": str(endereco_data.get("estado") or item.get("estado") or item.get("cEstado") or ""),
                "cep": str(endereco_data.get("cep") or item.get("cep") or item.get("cCEP") or ""),
                "inscricao_estadual": str(item.get("inscricao_estadual") or item.get("cInscEstadual") or ""),
                "inscricao_municipal": str(item.get("inscricao_municipal") or item.get("cInscMunicipal") or ""),
                "pessoa_fisica": str(item.get("pessoa_fisica") or item.get("cPessoaFisica") or "N"),
                "inativo": str(item.get("inativo") or item.get("cInativo") or "N"),
                "data_cadastro": item.get("data_cadastro") or item.get("dDtInc") or None,
                "data_alteracao": item.get("data_alteracao") or item.get("dDtAlt") or None
            }
            # Remove campos vazios mas mantém codigo_cliente_omie
            mapped_item = {k: v for k, v in mapped_item.items() if v or k in ["codigo_cliente_omie"]}
            if mapped_item.get("codigo_cliente_omie"):
                mapped_data.append(mapped_item)
        
        return mapped_data
