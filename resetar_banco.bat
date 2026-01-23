@echo off
chcp 65001 >nul

REM Mudar para o diretório do script
cd /d "%~dp0"

echo ============================================================
echo RESETAR BANCO DE DADOS
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

REM Executar reset
python resetar_banco.py

echo.
pause
