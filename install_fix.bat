@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PIP_NO_BUILD_ISOLATION=1
set PIP_DISABLE_PIP_VERSION_CHECK=1

echo ============================================================
echo INSTALACAO DE DEPENDENCIAS - MODO CORRECAO
echo ============================================================
echo.
echo Tentando atualizar pip primeiro...
echo.

python -m pip install --upgrade pip --no-cache-dir --disable-pip-version-check 2>nul
if errorlevel 1 (
    echo AVISO: Nao foi possivel atualizar o pip, continuando...
    echo.
)

echo Instalando dependencias...
echo.

python -m pip install --no-cache-dir --disable-pip-version-check --no-deps pydantic 2>nul
python -m pip install --no-cache-dir --disable-pip-version-check pydantic-settings 2>nul
python -m pip install --no-cache-dir --disable-pip-version-check requests 2>nul
python -m pip install --no-cache-dir --disable-pip-version-check urllib3 2>nul
python -m pip install --no-cache-dir --disable-pip-version-check mysql-connector-python 2>nul

echo.
echo ============================================================
echo Verificando instalacao...
echo ============================================================
python -c "import pydantic; print('[OK] pydantic instalado')" 2>nul || echo [ERRO] pydantic nao instalado
python -c "import pydantic_settings; print('[OK] pydantic-settings instalado')" 2>nul || echo [ERRO] pydantic-settings nao instalado
python -c "import requests; print('[OK] requests instalado')" 2>nul || echo [ERRO] requests nao instalado
python -c "import urllib3; print('[OK] urllib3 instalado')" 2>nul || echo [ERRO] urllib3 nao instalado
python -c "import mysql.connector; print('[OK] mysql-connector-python instalado')" 2>nul || echo [ERRO] mysql-connector-python nao instalado

echo.
echo ============================================================
echo Processo concluido!
echo ============================================================
pause
