# Solução Definitiva para Problema do pip

## 🔴 Problema Identificado

O erro `UnicodeDecodeError: 'charmap' codec can't decode byte` ocorre porque o pip está tentando ler metadados de pacotes já instalados que têm encoding incorreto. Isso é um bug conhecido do Python 3.13 no Windows.

## ✅ Solução Recomendada: Ambiente Virtual Limpo

A **melhor solução** é criar um ambiente virtual novo e limpo:

### Opção 1: Script Automático (Mais Fácil)

Execute:
```bash
install_venv.bat
```

Este script:
1. Cria um ambiente virtual novo
2. Ativa o ambiente
3. Instala todas as dependências

### Opção 2: Manual

No PowerShell:

```powershell
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Se der erro de política de execução, execute primeiro:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Instalar dependências
$env:PYTHONIOENCODING="utf-8"
pip install -r requirements.txt
```

**Para usar no futuro**, sempre ative o ambiente virtual primeiro:
```powershell
.\venv\Scripts\Activate.ps1
```

## 🔧 Solução Alternativa: Corrigir pip Atual

Se você não quiser usar ambiente virtual, tente:

### Opção 1: Script de Correção

Execute:
```bash
install_fix.bat
```

### Opção 2: Reinstalar pip

```powershell
# Desinstalar pip
python -m pip uninstall pip -y

# Reinstalar pip
python -m ensurepip --upgrade

# Tentar instalar novamente
$env:PYTHONIOENCODING="utf-8"
pip install -r requirements.txt
```

### Opção 3: Usar get-pip.py

```powershell
# Baixar get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

# Executar
python get-pip.py

# Instalar dependências
$env:PYTHONIOENCODING="utf-8"
pip install -r requirements.txt
```

## 🎯 Por que Ambiente Virtual é Melhor?

1. **Isolamento**: Não interfere com outros projetos
2. **Limpo**: Sem conflitos de pacotes antigos
3. **Portável**: Pode ser recriado facilmente
4. **Seguro**: Não mexe no Python global

## 📝 Após Instalação

Depois de instalar as dependências (em qualquer método):

1. **Configure o arquivo `.env`**:
   ```bash
   copy env.example .env
   # Edite .env com suas credenciais
   ```

2. **Teste a instalação**:
   ```bash
   python -c "import pydantic; import requests; import mysql.connector; print('OK!')"
   ```

3. **Execute o sistema**:
   ```bash
   python -m src.main
   ```

## 🆘 Se Nada Funcionar

Como último recurso, você pode instalar os pacotes manualmente baixando os wheels:

1. Acesse: https://pypi.org/
2. Baixe os arquivos `.whl` para:
   - pydantic
   - pydantic-settings
   - requests
   - urllib3
   - mysql-connector-python

3. Instale diretamente:
   ```bash
   pip install caminho\para\arquivo.whl
   ```

Mas **recomendo fortemente usar o ambiente virtual** - é a solução mais limpa e profissional.
