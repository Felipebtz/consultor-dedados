"""
Entry point para Vercel: expõe o Flask app do dashboard.
Vercel detecta o app em src/app.py e faz o deploy como serverless.
"""
from src.web.app import app

__all__ = ["app"]
