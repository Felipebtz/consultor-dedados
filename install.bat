@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
echo ============================================================
echo INSTALACAO DE DEPENDENCIAS
echo ============================================================
echo.
python -m pip install pydantic>=2.0.0 --no-cache-dir
python -m pip install pydantic-settings>=2.0.0 --no-cache-dir
python -m pip install requests>=2.31.0 --no-cache-dir
python -m pip install urllib3>=2.0.0 --no-cache-dir
python -m pip install mysql-connector-python>=8.2.0 --no-cache-dir
echo.
echo ============================================================
echo Instalacao concluida!
echo ============================================================
pause
