# Guia de APIs - Como Adicionar Novas APIs

## 📋 APIs Atualmente Implementadas

### 1. **Clientes** ✅
- **Endpoint**: `geral/clientes/`
- **Método**: `ListarClientes`
- **Arquivo**: `src/collectors/clientes.py`
- **Tabela**: `clientes`

### 2. **Produtos** ✅
- **Endpoint**: `geral/produtos/`
- **Método**: `ListarProdutos`
- **Arquivo**: `src/collectors/produtos.py`
- **Tabela**: `produtos`

### 3. **Serviços** ✅
- **Endpoint**: `servicos/servico/`
- **Método**: `ListarCadastroServico`
- **Arquivo**: `src/collectors/servicos.py`
- **Tabela**: `servicos`

### 4. **Categorias** ✅
- **Endpoint**: `geral/categorias/`
- **Método**: `ListarCategorias`
- **Arquivo**: `src/collectors/categorias.py`
- **Tabela**: `categorias`

### 5. **Contas a Receber** ✅
- **Endpoint**: `financas/contareceber/`
- **Método**: `ListarContasReceber`
- **Arquivo**: `src/collectors/contas_receber.py`
- **Tabela**: `contas_receber`

### 6. **Contas a Pagar** ✅
- **Endpoint**: `financas/contapagar/`
- **Método**: `ListarContasPagar`
- **Arquivo**: `src/collectors/contas_pagar.py`
- **Tabela**: `contas_pagar`

### 7. **Extrato** ✅
- **Endpoint**: `financas/extrato/`
- **Método**: `ListarExtrato`
- **Arquivo**: `src/collectors/extrato.py`
- **Tabela**: `extrato`

### 8. **Ordens de Serviço** ✅
- **Endpoint**: `servicos/os/`
- **Método**: `ListarOS`
- **Arquivo**: `src/collectors/ordem_servico.py`
- **Tabela**: `ordem_servico`

### 9. **Contas DRE** ✅
- **Endpoint**: `financas/contadre/`
- **Método**: `ListarCadastroDRE`
- **Arquivo**: `src/collectors/contas_dre.py`
- **Tabela**: `contas_dre`

---

## 🆕 Como Adicionar uma Nova API

### Passo 1: Criar o Arquivo do Coletor

Crie um novo arquivo em `src/collectors/` com o nome da API (ex: `fornecedores.py`):

```python
"""
Coletor de dados de Fornecedores.
"""
from typing import Dict, Any
from src.collectors.base import BaseCollector


class FornecedoresCollector(BaseCollector):
    """Coletor para dados de fornecedores."""
    
    def get_endpoint(self) -> str:
        return "geral/fornecedores/"  # ⬅️ ENDPOINT DA API OMIE
    
    def get_method(self) -> str:
        return "ListarFornecedores"  # ⬅️ MÉTODO DA API OMIE
    
    def get_table_name(self) -> str:
        return "fornecedores"  # ⬅️ NOME DA TABELA NO BANCO
    
    def get_schema(self) -> Dict[str, str]:
        """
        Define a estrutura da tabela no banco de dados.
        Ajuste os campos conforme a resposta da API.
        """
        return {
            "codigo_fornecedor": "VARCHAR(50) PRIMARY KEY",
            "codigo_fornecedor_integracao": "VARCHAR(50)",
            "razao_social": "VARCHAR(255)",
            "nome_fantasia": "VARCHAR(255)",
            "cnpj_cpf": "VARCHAR(20)",
            "email": "VARCHAR(255)",
            "telefone": "VARCHAR(20)",
            "endereco": "VARCHAR(255)",
            "cidade": "VARCHAR(100)",
            "estado": "VARCHAR(2)",
            "cep": "VARCHAR(10)",
            "inativo": "CHAR(1)",
            "data_cadastro": "DATETIME",
            "data_alteracao": "DATETIME",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        }
    
    def build_payload(self, pagina: int = 1, registros_por_pagina: int = 500, **kwargs) -> Dict[str, Any]:
        """
        Constrói o payload para a requisição.
        Ajuste conforme os parâmetros que a API aceita.
        """
        return {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": "N",
            "ordernar_por": "CODIGO_FORNECEDOR"
        }
```

### Passo 2: Registrar no __init__.py

Edite `src/collectors/__init__.py` e adicione:

```python
from src.collectors.fornecedores import FornecedoresCollector

# No __all__:
__all__ = [
    # ... outros coletores ...
    "FornecedoresCollector"
]
```

### Passo 3: Adicionar ao Orquestrador

Edite `src/orchestrator.py`:

1. **Importar o coletor** (no topo do arquivo):
```python
from src.collectors import (
    # ... outros imports ...
    FornecedoresCollector
)
```

2. **Adicionar à lista de coletores** (no método `__init__`):
```python
self.collectors = [
    # ... outros coletores ...
    FornecedoresCollector(self.api_client)
]
```

### Passo 4: Testar

Execute o sistema:
```bash
python -m src.main
```

---

## 📝 Exemplo Completo: Adicionando "Vendedores"

### 1. Criar `src/collectors/vendedores.py`:

```python
"""
Coletor de dados de Vendedores.
"""
from typing import Dict, Any
from src.collectors.base import BaseCollector


class VendedoresCollector(BaseCollector):
    """Coletor para dados de vendedores."""
    
    def get_endpoint(self) -> str:
        return "geral/vendedores/"
    
    def get_method(self) -> str:
        return "ListarVendedores"
    
    def get_table_name(self) -> str:
        return "vendedores"
    
    def get_schema(self) -> Dict[str, str]:
        return {
            "codigo_vendedor": "VARCHAR(50) PRIMARY KEY",
            "codigo_vendedor_integracao": "VARCHAR(50)",
            "nome": "VARCHAR(255)",
            "email": "VARCHAR(255)",
            "telefone": "VARCHAR(20)",
            "comissao": "DECIMAL(5,2)",
            "inativo": "CHAR(1)",
            "data_cadastro": "DATETIME",
            "data_alteracao": "DATETIME",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        }
    
    def build_payload(self, pagina: int = 1, registros_por_pagina: int = 500, **kwargs) -> Dict[str, Any]:
        return {
            "pagina": pagina,
            "registros_por_pagina": registros_por_pagina,
            "apenas_importado_api": "N",
            "ordernar_por": "CODIGO_VENDEDOR"
        }
```

### 2. Editar `src/collectors/__init__.py`:

```python
from src.collectors.vendedores import VendedoresCollector

__all__ = [
    # ... outros ...
    "VendedoresCollector"
]
```

### 3. Editar `src/orchestrator.py`:

```python
from src.collectors import (
    # ... outros ...
    VendedoresCollector
)

# No __init__:
self.collectors = [
    # ... outros ...
    VendedoresCollector(self.api_client)
]
```

---

## 🔍 Como Descobrir os Campos da API

1. **Consulte a documentação da Omie**: https://developer.omie.com.br/service-list/
2. **Teste a API manualmente** usando Postman ou curl
3. **Veja a resposta JSON** e mapeie os campos para o schema
4. **Ajuste o método `transform_data()`** em `base.py` se necessário

---

## ⚠️ Dicas Importantes

1. **Nome da Tabela**: Use sempre minúsculas e underscore (ex: `contas_receber`)
2. **Chave Primária**: Sempre defina uma chave primária no schema
3. **Campos Obrigatórios**: `created_at` e `updated_at` são adicionados automaticamente
4. **Tipos SQL**: Use tipos apropriados (VARCHAR, INT, DECIMAL, DATE, DATETIME, TEXT)
5. **Paginação**: A maioria das APIs Omie suporta paginação (já implementada)

---

## 📚 APIs Comuns que Podem Ser Adicionadas

Baseado na documentação da Omie, aqui estão algumas APIs que você pode querer adicionar:

- **Fornecedores**: `geral/fornecedores/` → `ListarFornecedores`
- **Vendedores**: `geral/vendedores/` → `ListarVendedores`
- **Pedidos**: `produtos/pedido/` → `ListarPedidos`
- **Contratos**: `geral/contratos/` → `ListarContratos`
- **Projetos**: `geral/projetos/` → `ListarProjetos`
- **Movimentos**: `financas/movimentos/` → `ListarMovimentos`
- **Conta Corrente**: `financas/conta_corrente/` → `ListarContasCorrentes`

---

## 🎯 Checklist para Nova API

- [ ] Criar arquivo do coletor em `src/collectors/`
- [ ] Definir `get_endpoint()` com o endpoint correto
- [ ] Definir `get_method()` com o método correto
- [ ] Definir `get_table_name()` com nome da tabela
- [ ] Definir `get_schema()` com estrutura da tabela
- [ ] Definir `build_payload()` com parâmetros necessários
- [ ] Registrar no `__init__.py` do módulo collectors
- [ ] Adicionar ao orquestrador em `orchestrator.py`
- [ ] Testar a execução
- [ ] Verificar se os dados estão sendo salvos no banco

---

## 💡 Exemplo de API com Parâmetros Especiais

Se a API precisa de parâmetros específicos (como datas), veja o exemplo de `ContasReceberCollector`:

```python
def build_payload(
    self, 
    data_inicio: str = None,
    data_fim: str = None,
    pagina: int = 1,
    registros_por_pagina: int = 500,
    **kwargs
) -> Dict[str, Any]:
    payload = {
        "pagina": pagina,
        "registros_por_pagina": registros_por_pagina,
        "apenas_importado_api": "N",
        "ordernar_por": "DATA_VENCIMENTO"
    }
    
    if data_inicio:
        payload["data_vencimento_inicial"] = data_inicio
    if data_fim:
        payload["data_vencimento_final"] = data_fim
        
    return payload
```
