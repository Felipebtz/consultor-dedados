# Guia de Instalação - Resolução de Problemas

## Problema: UnicodeDecodeError no pip

Se você está enfrentando o erro `UnicodeDecodeError: 'charmap' codec can't decode byte`, isso é um problema conhecido do pip no Windows com Python 3.13, causado por metadados de pacotes instalados com encoding incorreto.

## Soluções (Tente nesta ordem)

### Solução 1: Usar Script Batch (Mais Fácil no Windows)

Execute o arquivo `install.bat`:

```bash
install.bat
```

Este script configura o encoding corretamente e instala cada pacote.

### Solução 2: Instalar Manualmente com Encoding

No PowerShell, execute:

```powershell
$env:PYTHONIOENCODING="utf-8"
python -m pip install pydantic>=2.0.0 --no-cache-dir
python -m pip install pydantic-settings>=2.0.0 --no-cache-dir
python -m pip install requests>=2.31.0 --no-cache-dir
python -m pip install urllib3>=2.0.0 --no-cache-dir
python -m pip install mysql-connector-python>=8.2.0 --no-cache-dir
```

### Solução 3: Usar Ambiente Virtual Limpo (Recomendado)

Crie um ambiente virtual novo para evitar conflitos:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
$env:PYTHONIOENCODING="utf-8"
pip install -r requirements.txt
```

### Solução 4: Limpar e Reinstalar pip

Se o problema persistir, tente reinstalar o pip:

```powershell
python -m pip uninstall pip -y
python -m ensurepip --upgrade
$env:PYTHONIOENCODING="utf-8"
pip install -r requirements.txt
```

### Solução 5: Usar Script Python Alternativo

Execute o script Python:

```bash
python install_dependencies.py
```

## Verificar Instalação

Após instalar, verifique se tudo está correto:

```bash
python -c "import pydantic; import requests; import mysql.connector; print('Todas as dependências instaladas!')"
```

## Dependências Necessárias

- **pydantic** (>=2.0.0): Validação de dados e configurações
- **pydantic-settings** (>=2.0.0): Gerenciamento de configurações
- **requests** (>=2.31.0): Cliente HTTP
- **urllib3** (>=2.0.0): Suporte HTTP (dependência do requests)
- **mysql-connector-python** (>=8.2.0): Conector MySQL

## Próximos Passos

Após instalar as dependências:

1. Copie `env.example` para `.env`
2. Configure suas credenciais no arquivo `.env`
3. Execute: `python -m src.main`
