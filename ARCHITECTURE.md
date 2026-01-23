# Arquitetura do Sistema - Consultor de Dados Omie

## 📐 Visão Geral

Sistema desenvolvido seguindo os princípios **SOLID** e **Clean Code**, com foco em:
- ⚡ **Performance**: Coletas paralelas, pool de conexões, inserção em lote
- 📊 **Métricas**: Monitoramento detalhado de tempo de resposta
- 🔧 **Manutenibilidade**: Código limpo, modular e extensível
- 🛡️ **Robustez**: Tratamento de erros, retry automático, validação de dados

## 🏗️ Estrutura de Camadas

### 1. Camada de Configuração (`src/config/`)
- **Settings**: Classe principal de configurações
- **DatabaseSettings**: Configurações do MySQL
- **OmieSettings**: Configurações da API Omie
- Usa `pydantic-settings` para validação e carregamento de `.env`

### 2. Camada Core (`src/core/`)
- **Interfaces (Protocols)**: Define contratos seguindo Interface Segregation Principle
  - `IApiClient`: Contrato para cliente HTTP
  - `IDataCollector`: Contrato para coletores
  - `IDatabaseManager`: Contrato para gerenciamento de BD
  - `IMetricsCollector`: Contrato para métricas

### 3. Camada de Integração (`src/omie/`)
- **OmieAuthenticator**: Gerencia autenticação da API Omie
- **OmieApiClient**: Cliente HTTP com:
  - Retry automático (urllib3)
  - Pool de conexões HTTP
  - Timeout configurável
  - Tratamento de erros

### 4. Camada de Coleta (`src/collectors/`)
- **BaseCollector**: Classe abstrata base (Template Method Pattern)
  - Define fluxo padrão de coleta
  - Suporta paginação automática
  - Transformação de dados genérica
- **Coletores Específicos**: Herdam de `BaseCollector`
  - Cada coletor implementa métodos abstratos
  - Define schema da tabela
  - Customiza payload quando necessário

### 5. Camada de Persistência (`src/database/`)
- **DatabaseManager**: Gerenciador de banco de dados
  - Pool de conexões MySQL (Singleton)
  - Criação automática de tabelas
  - Inserção em lote (`executemany`)
  - Tratamento de duplicatas (ON DUPLICATE KEY UPDATE)
  - Context managers para gerenciamento de conexões

### 6. Camada de Métricas (`src/metrics/`)
- **MetricsCollector**: Coletor de métricas (Singleton)
  - Timer por operação
  - Estatísticas agregadas
  - Relatórios detalhados
- **MetricRecord**: Registro individual de métrica

### 7. Camada de Orquestração (`src/orchestrator.py`)
- **DataOrchestrator**: Orquestrador principal
  - Coordena todas as coletas
  - Execução paralela (ThreadPoolExecutor)
  - Execução sequencial (opcional)
  - Inicialização de banco de dados
  - Coletas específicas (ex: financeiras)

## 🔄 Fluxo de Execução

```
1. Inicialização
   ├── Carrega configurações (.env)
   ├── Cria pool de conexões MySQL
   ├── Cria cliente HTTP Omie
   └── Inicializa métricas

2. Preparação do Banco
   ├── Cria banco de dados (se não existir)
   └── Cria todas as tabelas

3. Coleta de Dados
   ├── Para cada coletor:
   │   ├── Inicia timer
   │   ├── Faz requisição à API (com paginação)
   │   ├── Transforma dados
   │   ├── Insere no banco (lote)
   │   └── Finaliza timer
   └── Executa em paralelo (ThreadPoolExecutor)

4. Métricas e Relatórios
   ├── Agrega métricas
   ├── Calcula estatísticas
   └── Exibe relatório

5. Limpeza
   ├── Fecha conexões HTTP
   └── Fecha pool MySQL
```

## 🎯 Princípios SOLID Aplicados

### Single Responsibility Principle (SRP)
- Cada classe tem uma única responsabilidade
- `OmieAuthenticator`: Apenas autenticação
- `OmieApiClient`: Apenas comunicação HTTP
- `DatabaseManager`: Apenas persistência
- `MetricsCollector`: Apenas métricas

### Open/Closed Principle (OCP)
- `BaseCollector` é aberta para extensão, fechada para modificação
- Novos coletores são criados herdando de `BaseCollector`
- Não é necessário modificar código existente

### Liskov Substitution Principle (LSP)
- Qualquer coletor pode substituir `BaseCollector`
- Interfaces garantem substituibilidade

### Interface Segregation Principle (ISP)
- Interfaces pequenas e específicas
- Classes não dependem de métodos que não usam
- `IApiClient`, `IDataCollector`, etc. são focadas

### Dependency Inversion Principle (DIP)
- Dependências através de abstrações (interfaces)
- `BaseCollector` depende de `IApiClient`, não de implementação concreta
- Facilita testes e manutenção

## 🚀 Otimizações de Performance

### 1. Pool de Conexões MySQL
- Reutilização de conexões
- Configurável (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`)
- Reduz overhead de criar/fechar conexões

### 2. Execução Paralela
- `ThreadPoolExecutor` para coletas simultâneas
- Configurável (`max_workers`)
- Reduz tempo total de execução

### 3. Inserção em Lote
- `executemany` ao invés de múltiplos `execute`
- Reduz round-trips ao banco
- Muito mais rápido para grandes volumes

### 4. Paginação Automática
- Coleta todas as páginas automaticamente
- Evita perda de dados
- Otimiza uso de memória

### 5. Retry Automático
- Trata erros temporários
- Backoff exponencial
- Aumenta robustez

## 📊 Métricas Coletadas

- **Tempo Total**: Soma de todos os tempos
- **Tempo Médio**: Média por operação
- **Tempo Mínimo/Máximo**: Extremos
- **Total de Registros**: Soma de registros coletados
- **Taxa de Sucesso**: Operações bem-sucedidas vs. falhas
- **Detalhes por Operação**: Tempo, registros, erros

## 🔧 Extensibilidade

### Adicionar Novo Endpoint

1. Criar novo coletor em `src/collectors/`
2. Herdar de `BaseCollector`
3. Implementar métodos abstratos
4. Registrar no `__init__.py`
5. Adicionar ao orquestrador (opcional)

### Adicionar Nova Métrica

1. Estender `MetricRecord`
2. Adicionar campos em `MetricsCollector`
3. Atualizar agregações

### Mudar Banco de Dados

1. Implementar `IDatabaseManager`
2. Criar nova classe (ex: `PostgreSQLManager`)
3. Substituir no orquestrador

## 🛡️ Tratamento de Erros

- **Try/Except** em pontos críticos
- **Logging** detalhado de erros
- **Retry** automático para erros temporários
- **Rollback** de transações em caso de erro
- **Métricas** de falhas

## 📝 Boas Práticas Aplicadas

- ✅ Type hints em todas as funções
- ✅ Docstrings em todas as classes/métodos
- ✅ Logging estruturado
- ✅ Context managers para recursos
- ✅ Validação de configurações (Pydantic)
- ✅ Separação de responsabilidades
- ✅ Código DRY (Don't Repeat Yourself)
- ✅ Nomes descritivos

## 🔍 Testabilidade

A arquitetura facilita testes:
- Dependências injetadas
- Interfaces permitem mocks
- Classes pequenas e focadas
- Separação de lógica e I/O

## 📈 Escalabilidade

O sistema pode escalar:
- Aumentando `max_workers` para mais paralelismo
- Aumentando `DB_POOL_SIZE` para mais conexões
- Adicionando mais coletores sem modificar código existente
- Distribuindo coletas em múltiplos processos/servidores
