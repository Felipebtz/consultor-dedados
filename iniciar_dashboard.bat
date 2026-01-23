@echo off
chcp 65001 >nul

REM Mudar para o diretório do script
cd /d "%~dp0"

echo ============================================================
echo INICIANDO DASHBOARD WEB
echo ============================================================
echo.

REM Verificar se o ambiente virtual existe
if not exist venv (
    echo Ambiente virtual nao encontrado!
    echo Execute: install_venv.bat primeiro
    pause
    exit /b 1
)

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Configurar PYTHONPATH para incluir o diretório raiz
set PYTHONPATH=%CD%

REM Verificar se Flask está instalado
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Instalando Flask...
    pip install flask>=3.0.0
)

REM Iniciar servidor web
echo.
echo ============================================================
echo Dashboard iniciado!
echo Acesse: http://localhost:5000
echo Diretorio atual: %CD%
echo ============================================================
echo.
python -m src.web.app
