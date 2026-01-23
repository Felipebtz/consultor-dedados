# Consultor de Dados - Sistema de Coleta Omie

Sistema robusto para coleta de dados das APIs do Omie, com foco em performance, tempo de resposta e arquitetura escalável.

## 🏗️ Arquitetura

O sistema foi desenvolvido seguindo os princípios **SOLID** e **Clean Code**, utilizando **Programação Orientada a Objetos (POO)**:

- **Single Responsibility**: Cada classe tem uma responsabilidade única
- **Open/Closed**: Extensível através de herança e interfaces
- **Liskov Substitution**: Classes filhas podem substituir classes base
- **Interface Segregation**: Interfaces específicas e focadas
- **Dependency Inversion**: Dependências através de abstrações

## 📁 Estrutura do Projeto

```
consultor-dedados/
├── src/
│   ├── config/          # Configurações do sistema
│   ├── core/            # Interfaces e classes base
│   ├── omie/            # Integração com API Omie
│   ├── collectors/      # Coletores específicos por endpoint
│   ├── database/        # Gerenciamento de banco de dados
│   ├── metrics/         # Sistema de métricas de performance
│   ├── orchestrator.py  # Orquestrador principal
│   └── main.py         # Script principal
├── .env.example         # Exemplo de variáveis de ambiente
├── requirements.txt     # Dependências Python
└── README.md           # Este arquivo
```

## 🚀 Instalação

### ⚠️ IMPORTANTE: Problema com pip no Windows/Python 3.13

Se você encontrar erros de encoding (`UnicodeDecodeError`) ao instalar dependências, **use um ambiente virtual** (recomendado):

**Opção 1: Script Automático (Mais Fácil)**
```bash
install_venv.bat
```

**Opção 2: Manual**
```bash
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

Para mais detalhes e outras soluções, consulte `SOLUCAO_PIP.md`.

### Instalação Normal

1. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

2. **Configure as variáveis de ambiente**:
   - Copie `env.example` para `.env`
   - Preencha com suas credenciais da API Omie e configurações do MySQL

```env
APP_KEY=2085162581502
APP_SECRET=d9331dd6c75f062db4441e72cff8f00d
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=coleta_dados
```

3. **Configure o banco de dados MySQL**:
   - Certifique-se de que o MySQL está rodando
   - O sistema criará automaticamente o banco de dados e as tabelas

## 📊 Endpoints Suportados

### Cadastros Gerais
- ✅ Clientes (`ListarClientes`)
- ✅ Produtos (`ListarProdutos`)
- ✅ Serviços (`ListarCadastroServico`)
- ✅ Categorias (`ListarCategorias`)
- ✅ Contas DRE (`ListarCadastroDRE`)

### Financeiro
- ✅ Contas a Receber (`ListarContasReceber`)
- ✅ Contas a Pagar (`ListarContasPagar`)
- ✅ Extrato (`ListarExtrato`)

### Movimentos
- ✅ Ordens de Serviço (`ListarOS`)

## 🎯 Uso

### ⚡ Início Rápido

1. **Instalar dependências** (primeira vez):
   ```bash
   install_venv.bat
   ```

2. **Configurar credenciais** no arquivo `.env`

3. **Executar coleta de dados**:
   ```bash
   executar.bat
   ```

4. **Iniciar dashboard web**:
   ```bash
   iniciar_dashboard.bat
   ```

5. **Acessar dashboard**: http://localhost:5000

### Execução Básica

Execute o script principal:

```bash
python -m src.main
```

O sistema irá:
1. Inicializar o banco de dados e criar todas as tabelas
2. Coletar dados de todos os endpoints
3. Armazenar os dados no MySQL
4. Exibir métricas de performance

### Dashboard Web

Para visualizar os dados coletados:

```bash
python -m src.web.app
```

Acesse no navegador: **http://localhost:5000**

**Funcionalidades do Dashboard:**
- 📊 Estatísticas gerais por tabela
- 💰 Dados financeiros (Contas a Receber/Pagar)
- 🔄 Atualização automática a cada 30 segundos
- 📈 Visualização de totais e saldos

### Execução Programática

```python
from src.orchestrator import DataOrchestrator
from src.config import Settings

# Inicializa
settings = Settings()
orchestrator = DataOrchestrator(settings)

# Inicializa banco de dados
orchestrator.initialize_database()

# Executa coletas gerais
results = orchestrator.run_collections(parallel=True, max_workers=5)

# Executa coletas financeiras com período específico
results_financial = orchestrator.run_financial_collections(
    data_inicio="2025-01-01",
    data_fim="2025-12-31",
    parallel=True
)

# Obtém métricas
metrics = orchestrator.get_metrics_summary()
orchestrator.print_metrics_summary()

# Limpa recursos
orchestrator.cleanup()
```

## ⚡ Performance

O sistema foi otimizado para performance:

- **Pool de Conexões**: Reutilização de conexões MySQL
- **Execução Paralela**: Coletas simultâneas usando ThreadPoolExecutor
- **Inserção em Lote**: `executemany` para inserções eficientes
- **Retry Automático**: Tratamento de erros temporários
- **Métricas Detalhadas**: Monitoramento de tempo de cada operação

### Métricas Coletadas

- Tempo total de execução
- Tempo por operação
- Número de registros coletados
- Taxa de sucesso/erro
- Tempo mínimo/máximo/médio

## 🗄️ Banco de Dados

O sistema cria automaticamente as seguintes tabelas:

- `clientes`
- `produtos`
- `servicos`
- `categorias`
- `contas_receber`
- `contas_pagar`
- `extrato`
- `ordem_servico`
- `contas_dre`

Cada tabela possui:
- Campos específicos do endpoint
- `created_at` e `updated_at` para auditoria
- Índices apropriados
- Tratamento de duplicatas (ON DUPLICATE KEY UPDATE)

## 🔧 Configuração Avançada

### Ajustar Pool de Conexões

No arquivo `.env`:
```env
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

### Ajustar Workers Paralelos

No código:
```python
orchestrator.run_collections(parallel=True, max_workers=10)
```

### Timeout e Retries

No arquivo `.env`:
```env
TIMEOUT=60
MAX_RETRIES=5
RETRY_DELAY=2
```

## 📝 Logs

O sistema gera logs detalhados de:
- Início/fim de cada coleta
- Erros e exceções
- Tempo de execução
- Número de registros processados

## 🛠️ Desenvolvimento

### Adicionar Novo Coletor

1. Crie uma nova classe em `src/collectors/` herdando de `BaseCollector`
2. Implemente os métodos abstratos:
   - `get_endpoint()`
   - `get_method()`
   - `get_table_name()`
   - `get_schema()`
   - `build_payload()` (opcional)
3. Registre no `__init__.py` do módulo collectors
4. Adicione ao orquestrador em `orchestrator.py`

### Exemplo de Novo Coletor

```python
from src.collectors.base import BaseCollector

class NovoColetor(BaseCollector):
    def get_endpoint(self) -> str:
        return "novo/endpoint/"
    
    def get_method(self) -> str:
        return "ListarNovo"
    
    def get_table_name(self) -> str:
        return "nova_tabela"
    
    def get_schema(self) -> Dict[str, str]:
        return {
            "id": "INT PRIMARY KEY AUTO_INCREMENT",
            "campo1": "VARCHAR(255)",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }
```

## 📄 Licença

Este projeto é privado e de uso interno.

## 👥 Suporte

Para questões ou problemas, consulte a documentação da API Omie:
https://developer.omie.com.br/service-list/
