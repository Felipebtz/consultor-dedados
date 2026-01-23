"""
Script alternativo para instalar dependencias.
Use este script se o pip tiver problemas de encoding.
"""
import subprocess
import sys
import os

# Define encoding UTF-8 para evitar problemas
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Lista de dependencias
dependencies = [
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "requests>=2.31.0",
    "urllib3>=2.0.0",
    "mysql-connector-python>=8.2.0"
]

def install_package(package):
    """Instala um pacote individualmente."""
    try:
        print(f"Instalando {package}...")
        # Usa PYTHONIOENCODING e --no-cache-dir
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package, "--no-cache-dir"],
            env=env
        )
        print(f"[OK] {package} instalado com sucesso\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Erro ao instalar {package}\n")
        return False

def main():
    """Instala todas as dependencias."""
    print("="*60)
    print("INSTALACAO DE DEPENDENCIAS")
    print("="*60)
    print()
    
    success_count = 0
    failed = []
    
    for package in dependencies:
        if install_package(package):
            success_count += 1
        else:
            failed.append(package)
    
    print("="*60)
    print(f"Instalados: {success_count}/{len(dependencies)}")
    if failed:
        print(f"Falharam: {', '.join(failed)}")
    print("="*60)

if __name__ == "__main__":
    main()
