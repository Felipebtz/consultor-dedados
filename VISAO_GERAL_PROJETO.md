# 📊 Visão Geral e Detalhada do Projeto

## 🎯 Objetivo do Projeto

Sistema robusto para **coletar, armazenar e visualizar dados** das APIs do Omie, com foco em:
- ⚡ **Performance**: Tempo de resposta e coleta de dados
- 📊 **Análise**: Dashboard para visualização de dados financeiros
- 🔧 **Manutenibilidade**: Código limpo seguindo SOLID e Clean Code
- 🛡️ **Robustez**: Tratamento de erros e retry automático

---

## 🏗️ Arquitetura do Sistema

### Visão Geral

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE APRESENTAÇÃO                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Dashboard Web (Flask) - Frontend HTML/CSS/JS       │   │
│  │  - Visualização de dados                            │   │
│  │  - Estatísticas financeiras                         │   │
│  │  - Métricas de performance                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE APLICAÇÃO                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Orquestrador (DataOrchestrator)                    │   │
│  │  - Coordena todas as coletas                        │   │
│  │  - Execução paralela/sequencial                     │   │
│  │  - Gerenciamento de métricas                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE SERVIÇOS                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Coletores   │  │  API Client  │  │  Database    │     │
│  │  - Clientes  │  │  - HTTP      │  │  - MySQL     │     │
│  │  - Produtos  │  │  - Retry     │  │  - Pool      │     │
│  │  - Financeiro│  │  - Auth      │  │  - Batch     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    CAMADA DE DADOS                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  MySQL Database                                      │   │
│  │  - 9 tabelas de dados                                │   │
│  │  - Índices otimizados                                │   │
│  │  - Tratamento de duplicatas                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura Detalhada do Projeto

```
consultor-dedados/
│
├── 📂 src/                          # Código-fonte principal
│   │
│   ├── 📂 config/                   # Configurações
│   │   ├── __init__.py
│   │   └── settings.py              # Settings com Pydantic
│   │
│   ├── 📂 core/                     # Interfaces e contratos
│   │   ├── __init__.py
│   │   └── interfaces.py            # Interfaces SOLID
│   │
│   ├── 📂 omie/                     # Integração API Omie
│   │   ├── __init__.py
│   │   ├── auth.py                  # Autenticação
│   │   └── client.py                # Cliente HTTP
│   │
│   ├── 📂 collectors/               # Coletores de dados
│   │   ├── __init__.py
│   │   ├── base.py                  # Classe base abstrata
│   │   ├── clientes.py              # ✅ Clientes
│   │   ├── produtos.py              # ✅ Produtos
│   │   ├── servicos.py              # ✅ Serviços
│   │   ├── categorias.py           # ✅ Categorias
│   │   ├── contas_receber.py       # ✅ Contas a Receber
│   │   ├── contas_pagar.py         # ✅ Contas a Pagar
│   │   ├── extrato.py               # ✅ Extrato
│   │   ├── ordem_servico.py         # ✅ Ordens de Serviço
│   │   └── contas_dre.py            # ✅ Contas DRE
│   │
│   ├── 📂 database/                  # Gerenciamento BD
│   │   ├── __init__.py
│   │   └── manager.py               # DatabaseManager com pool
│   │
│   ├── 📂 metrics/                  # Sistema de métricas
│   │   ├── __init__.py
│   │   └── collector.py             # MetricsCollector
│   │
│   ├── 📂 web/                      # Frontend Web
│   │   ├── __init__.py
│   │   ├── app.py                   # Aplicação Flask
│   │   └── templates/
│   │       └── index.html           # Dashboard HTML
│   │
│   ├── 📂 utils/                    # Utilitários
│   │   ├── __init__.py
│   │   └── logging_config.py       # Configuração de logs
│   │
│   ├── orchestrator.py              # Orquestrador principal
│   └── main.py                      # Script principal
│
├── 📄 .env                          # Variáveis de ambiente (criar)
├── 📄 env.example                   # Exemplo de configuração
├── 📄 requirements.txt              # Dependências Python
│
├── 📚 Documentação/
│   ├── README.md                    # Documentação principal
│   ├── ARCHITECTURE.md              # Arquitetura detalhada
│   ├── GUIA_APIS.md                 # Guia de APIs
│   ├── GUIA_EXECUCAO.md            # Guia de execução
│   ├── VISAO_GERAL_PROJETO.md      # Este arquivo
│   ├── LISTA_APIS_OMIE.md          # Lista de APIs disponíveis
│   └── TEMPLATE_COLETOR.py         # Template para novos coletores
│
└── 🔧 Scripts/
    ├── install_venv.bat            # Instalação automática
    ├── install.bat                 # Instalação simples
    └── example_usage.py             # Exemplos de uso
```

---

## 🔄 Fluxo de Execução

### 1. Inicialização
```
main.py
  ↓
DataOrchestrator
  ↓
├── Settings (carrega .env)
├── OmieApiClient (cria sessão HTTP)
├── DatabaseManager (cria pool MySQL)
└── MetricsCollector (inicializa métricas)
```

### 2. Preparação do Banco
```
initialize_database()
  ↓
create_database_if_not_exists()
  ↓
Para cada coletor:
  create_table(nome_tabela, schema)
```

### 3. Coleta de Dados
```
run_collections()
  ↓
Para cada coletor (paralelo):
  ├── collect()
  │   ├── request(API Omie)
  │   ├── transform_data()
  │   └── insert_batch(MySQL)
  └── stop_timer(metrics)
```

### 4. Visualização
```
Flask App
  ↓
/api/stats → Estatísticas gerais
/api/financial → Dados financeiros
/api/tables/<nome> → Dados da tabela
```

---

## 📊 Componentes Principais

### 1. Orquestrador (DataOrchestrator)
**Responsabilidade**: Coordenar todas as operações

**Funcionalidades**:
- Inicializar banco de dados
- Executar coletas em paralelo/sequencial
- Gerenciar métricas
- Tratamento de erros

### 2. Coletores (BaseCollector)
**Responsabilidade**: Coletar dados de uma API específica

**Padrão**: Template Method
- `get_endpoint()`: Endpoint da API
- `get_method()`: Método da API
- `get_table_name()`: Nome da tabela
- `get_schema()`: Estrutura da tabela
- `build_payload()`: Parâmetros da requisição
- `collect()`: Fluxo de coleta (herdado)

### 3. Cliente API (OmieApiClient)
**Responsabilidade**: Comunicação HTTP com Omie

**Funcionalidades**:
- Autenticação automática
- Retry automático (3 tentativas)
- Pool de conexões HTTP
- Timeout configurável

### 4. Gerenciador de BD (DatabaseManager)
**Responsabilidade**: Persistência de dados

**Funcionalidades**:
- Pool de conexões MySQL (10 conexões)
- Criação automática de tabelas
- Inserção em lote (executemany)
- Tratamento de duplicatas

### 5. Coletor de Métricas (MetricsCollector)
**Responsabilidade**: Monitoramento de performance

**Métricas coletadas**:
- Tempo por operação
- Total de registros
- Taxa de sucesso/erro
- Estatísticas agregadas

---

## 🗄️ Estrutura do Banco de Dados

### Tabelas Criadas

1. **clientes** - Cadastro de clientes
2. **produtos** - Cadastro de produtos
3. **servicos** - Cadastro de serviços
4. **categorias** - Categorias
5. **contas_receber** - Contas a receber
6. **contas_pagar** - Contas a pagar
7. **extrato** - Extrato financeiro
8. **ordem_servico** - Ordens de serviço
9. **contas_dre** - Contas DRE

### Características
- ✅ Chaves primárias definidas
- ✅ Campos de auditoria (created_at, updated_at)
- ✅ Índices otimizados
- ✅ Tratamento de duplicatas (ON DUPLICATE KEY UPDATE)

---

## 🚀 Tecnologias Utilizadas

### Backend
- **Python 3.8+**: Linguagem principal
- **Pydantic**: Validação de configurações
- **Requests**: Cliente HTTP
- **MySQL Connector**: Conexão com MySQL
- **Flask**: Framework web

### Frontend
- **HTML5/CSS3**: Estrutura e estilo
- **JavaScript (Vanilla)**: Interatividade
- **Fetch API**: Comunicação com backend

### Arquitetura
- **SOLID Principles**: Design patterns
- **POO**: Programação Orientada a Objetos
- **Template Method**: Padrão de design
- **Singleton**: Pool de conexões

---

## 📈 Métricas e Performance

### Métricas Coletadas
- ⏱️ Tempo total de execução
- ⏱️ Tempo por operação
- 📊 Número de registros coletados
- ✅ Taxa de sucesso/erro
- 📈 Tempo mínimo/máximo/médio

### Otimizações
- 🔄 Execução paralela (ThreadPoolExecutor)
- 🔌 Pool de conexões MySQL
- 📦 Inserção em lote (executemany)
- 🔁 Retry automático
- 📄 Paginação automática

---

## 🎯 Funcionalidades do Dashboard

### Visão Geral
- Total de registros por tabela
- Cards visuais com estatísticas
- Atualização automática (30s)

### Dados Financeiros
- Contas a Receber (total, pago, pendente)
- Contas a Pagar (total, pago, pendente)
- Valores formatados em R$

### Navegação
- Interface responsiva
- Design moderno
- Fácil navegação

---

## 🔐 Segurança

- ✅ Validação de entrada (Pydantic)
- ✅ Sanitização de queries SQL
- ✅ Whitelist de tabelas permitidas
- ✅ Tratamento de erros
- ✅ Logs detalhados

---

## 📝 Próximas Melhorias

### Curto Prazo
- [ ] Gráficos interativos (Chart.js)
- [ ] Filtros por data
- [ ] Exportação de dados (CSV/Excel)
- [ ] Histórico de coletas

### Médio Prazo
- [ ] Autenticação de usuários
- [ ] Múltiplas empresas
- [ ] Agendamento de coletas
- [ ] Notificações

### Longo Prazo
- [ ] Machine Learning para previsões
- [ ] API REST completa
- [ ] Mobile app
- [ ] Integração com outros sistemas

---

## 📞 Suporte e Documentação

- **README.md**: Documentação principal
- **ARCHITECTURE.md**: Arquitetura detalhada
- **GUIA_EXECUCAO.md**: Passo a passo de execução
- **GUIA_APIS.md**: Como adicionar novas APIs
- **SOLUCAO_PIP.md**: Solução de problemas

---

## 🎓 Conceitos Aplicados

### SOLID
- **S**ingle Responsibility: Cada classe uma responsabilidade
- **O**pen/Closed: Aberto para extensão, fechado para modificação
- **L**iskov Substitution: Classes filhas substituem classes base
- **I**nterface Segregation: Interfaces específicas
- **D**ependency Inversion: Dependências via abstrações

### Design Patterns
- **Template Method**: BaseCollector
- **Singleton**: DatabaseManager, MetricsCollector
- **Factory**: Criação de coletores
- **Strategy**: Diferentes estratégias de coleta

### Clean Code
- Nomes descritivos
- Funções pequenas e focadas
- Comentários quando necessário
- DRY (Don't Repeat Yourself)
- Type hints em todas as funções

---

## ✅ Status do Projeto

- ✅ Backend completo e funcional
- ✅ 9 APIs implementadas
- ✅ Sistema de métricas
- ✅ Dashboard web básico
- ✅ Documentação completa
- 🔄 Melhorias contínuas

---

**Desenvolvido com foco em performance, manutenibilidade e escalabilidade.**
