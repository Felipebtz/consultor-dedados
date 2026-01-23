@echo off
chcp 65001 >nul
echo =========================================
echo Testando Coletor: CONTA CORRENTE
echo =========================================
echo.

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist "test_venv\Scripts\activate.bat" (
    call test_venv\Scripts\activate.bat
) else (
    echo [ERRO] Ambiente virtual não encontrado!
    echo Execute install_venv.bat primeiro.
    pause
    exit /b 1
)

python testar_coletor.py conta_corrente

echo.
echo =========================================
echo Teste finalizado.
echo =========================================
pause
