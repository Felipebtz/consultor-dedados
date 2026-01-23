@echo off
chcp 65001 >nul
echo ============================================================
echo CRIANDO AMBIENTE VIRTUAL LIMPO
echo ============================================================
echo.
echo Isso criara um ambiente virtual novo para evitar conflitos
echo.

if exist venv (
    echo Ambiente virtual ja existe. Removendo...
    rmdir /s /q venv
)

echo Criando ambiente virtual...
python -m venv venv

if errorlevel 1 (
    echo ERRO: Nao foi possivel criar o ambiente virtual
    pause
    exit /b 1
)

echo.
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERRO: Nao foi possivel ativar o ambiente virtual
    pause
    exit /b 1
)

echo.
echo Ambiente virtual ativado!
echo.
echo Instalando dependencias...
echo.

set PYTHONIOENCODING=utf-8
python -m pip install --upgrade pip --no-cache-dir
python -m pip install -r requirements.txt --no-cache-dir

echo.
echo ============================================================
echo Instalacao concluida!
echo ============================================================
echo.
echo Para usar o ambiente virtual no futuro, execute:
echo   venv\Scripts\activate.bat
echo.
pause
