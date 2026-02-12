@echo off
chcp 65001 >nul

cd /d "%~dp0"

echo ============================================================
echo COLETA APENAS: PEDIDOS DE VENDA
echo ============================================================
echo.

if not exist venv (
    echo Ambiente virtual nao encontrado! Execute install_venv.bat primeiro.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
set PYTHONPATH=%CD%

echo Atualizando pedido_vendas no banco (painel)...
echo.
python testar_coletor.py pedido_vendas

echo.
echo ============================================================
echo Concluido! Atualize o painel/dashboard para ver os dados.
echo ============================================================
pause
