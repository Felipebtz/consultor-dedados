# 🚀 Guia Completo de Execução - Passo a Passo

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter:

- ✅ Python 3.8+ instalado
- ✅ MySQL instalado e rodando
- ✅ Credenciais da API Omie (APP_KEY e APP_SECRET)
- ✅ Conexão com internet

---

## 🔧 PASSO 1: Instalação do Ambiente

### Opção A: Usando Ambiente Virtual (Recomendado)

```bash
# 1. Criar ambiente virtual
python -m venv venv

# 2. Ativar ambiente virtual
# No Windows (PowerShell):
venv\Scripts\Activate.ps1

# No Windows (CMD):
venv\Scripts\activate.bat

# 3. Instalar dependências
pip install -r requirements.txt
```

### Opção B: Script Automático (Windows)

```bash
# Execute o script batch
install_venv.bat
```

---

## ⚙️ PASSO 2: Configuração

### 2.1. Criar arquivo `.env`

```bash
# Copie o arquivo de exemplo
copy env.example .env
```

### 2.2. Editar arquivo `.env`

Abra o arquivo `.env` e preencha com suas credenciais:

```env
# API Omie
APP_KEY=2085162581502
APP_SECRET=d9331dd6c75f062db4441e72cff8f00d
BASE_URL=https://app.omie.com.br/api/v1

# Banco de Dados MySQL
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=sua_senha_aqui
DB_NAME=coleta_dados
```

### 2.3. Verificar MySQL

Certifique-se de que o MySQL está rodando:

```bash
# Verificar se o MySQL está rodando
# No XAMPP: Inicie o MySQL pelo painel de controle
```

---

## 🎯 PASSO 3: Executar o Sistema

### 3.1. Ativar Ambiente Virtual (se necessário)

```bash
venv\Scripts\activate.bat
```

### 3.2. Executar Coleta de Dados

```bash
python -m src.main
```

**O que acontece:**
1. ✅ Cria o banco de dados `coleta_dados` (se não existir)
2. ✅ Cria todas as tabelas necessárias
3. ✅ Coleta dados de todas as APIs do Omie
4. ✅ Salva os dados no MySQL
5. ✅ Exibe métricas de performance

### 3.3. Verificar Resultados

Após a execução, você verá:

```
================================================================================
RESULTADOS DAS COLETAS
================================================================================
[OK] clientes: 150 registros
[OK] produtos: 80 registros
[OK] servicos: 25 registros
...
================================================================================

================================================================================
RESUMO DE MÉTRICAS DE PERFORMANCE
================================================================================
Total de Operações: 9
Tempo Total: 45.23s
Tempo Médio: 5.03s
...
```

---

## 🌐 PASSO 4: Acessar o Front-End (Dashboard)

### 4.1. Iniciar o Servidor Web

```bash
# Com ambiente virtual ativado
python -m src.web.app
```

Ou:

```bash
python src/web/app.py
```

### 4.2. Acessar no Navegador

Abra seu navegador e acesse:

```
http://localhost:5000
```

ou

```
http://127.0.0.1:5000
```

---

## 📊 PASSO 5: Usar o Dashboard

### Funcionalidades Disponíveis:

1. **Visão Geral**
   - Total de registros por tabela
   - Última atualização
   - Status das coletas

2. **Dados Financeiros**
   - Contas a Receber
   - Contas a Pagar
   - Extrato
   - Gráficos e estatísticas

3. **Cadastros**
   - Clientes
   - Produtos
   - Serviços
   - Categorias

4. **Métricas de Performance**
   - Tempo de coleta por API
   - Estatísticas de performance
   - Histórico de execuções

---

## 🔄 Execução Automática (Opcional)

### Criar Tarefa Agendada (Windows)

1. Abra o **Agendador de Tarefas**
2. Crie uma nova tarefa
3. Configure para executar:
   ```
   C:\caminho\para\venv\Scripts\python.exe -m src.main
   ```
4. Defina a frequência (diária, semanal, etc.)

### Script Batch para Execução Rápida

Crie um arquivo `executar.bat`:

```batch
@echo off
cd /d "C:\xampp\htdocs\consultor-dedados"
call venv\Scripts\activate.bat
python -m src.main
pause
```

---

## 🐛 Solução de Problemas

### Erro: "ModuleNotFoundError"

**Solução:**
```bash
# Ative o ambiente virtual
venv\Scripts\activate.bat
# Reinstale as dependências
pip install -r requirements.txt
```

### Erro: "Can't connect to MySQL"

**Solução:**
1. Verifique se o MySQL está rodando
2. Confirme as credenciais no arquivo `.env`
3. Teste a conexão:
   ```bash
   mysql -u root -p
   ```

### Erro: "API Omie retornou erro 500"

**Solução:**
- Pode ser problema temporário da API Omie
- Verifique suas credenciais (APP_KEY e APP_SECRET)
- Aguarde alguns minutos e tente novamente

### Erro: "UnicodeDecodeError"

**Solução:**
- Use ambiente virtual (veja PASSO 1)
- Consulte `SOLUCAO_PIP.md` para mais detalhes

---

## 📝 Comandos Úteis

```bash
# Verificar instalação
python -c "import pydantic; import requests; import mysql.connector; print('OK!')"

# Testar conexão MySQL
python -c "import mysql.connector; conn = mysql.connector.connect(host='localhost', user='root', password=''); print('MySQL OK!')"

# Ver logs detalhados
python -m src.main 2>&1 | tee log.txt

# Executar apenas uma coleta específica
python example_usage.py individual
```

---

## 🎯 Próximos Passos

1. ✅ Execute a coleta inicial
2. ✅ Verifique os dados no MySQL
3. ✅ Acesse o dashboard
4. ✅ Configure execução automática (opcional)
5. ✅ Adicione mais APIs conforme necessário

---

## 📞 Suporte

- **Documentação**: Veja `README.md` e `ARCHITECTURE.md`
- **Guia de APIs**: Veja `GUIA_APIS.md`
- **Problemas de Instalação**: Veja `SOLUCAO_PIP.md`
