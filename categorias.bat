@echo off
chcp 65001 >nul
echo =========================================
echo Testando Coletor: CATEGORIAS
echo =========================================
echo.

cd /d "%~dp0"

REM Ativar ambiente virtual
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ERRO: Ambiente virtual nao encontrado!
    echo Execute install_venv.bat primeiro.
    pause
    exit /b 1
)

REM Executar o teste
python testar_coletor.py categorias

echo.
echo =========================================
echo Teste finalizado.
echo =========================================
pause
