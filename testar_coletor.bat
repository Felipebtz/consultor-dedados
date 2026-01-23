@echo off
chcp 65001 >nul
echo ========================================
echo TESTE DE COLETOR INDIVIDUAL
echo ========================================
echo.

if "%1"=="" (
    echo Uso: testar_coletor.bat ^<nome_do_coletor^>
    echo.
    echo Coletores disponíveis:
    echo   - clientes
    echo   - produtos
    echo   - servicos
    echo   - categorias
    echo   - contas_receber
    echo   - contas_pagar
    echo   - extrato
    echo   - ordem_servico
    echo   - contas_dre
    echo.
    echo Exemplo:
    echo   testar_coletor.bat servicos
    echo   testar_coletor.bat ordem_servico
    echo.
    pause
    exit /b
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo Executando teste do coletor: %1
echo.

python testar_coletor.py %1

echo.
pause
