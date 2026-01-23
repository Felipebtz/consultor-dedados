"""
Script para debugar a estrutura das respostas da API Omie.
Execute este script para ver a estrutura real das respostas.
"""
import json
from src.config import Settings
from src.omie import OmieApiClient
from src.collectors import ServicosCollector, OrdemServicoCollector

settings = Settings()
client = OmieApiClient(settings.omie)

print("="*80)
print("DEBUG - Estrutura das Respostas da API")
print("="*80)

# Testa Serviços
print("\n1. TESTANDO SERVIÇOS")
print("-"*80)
servicos_collector = ServicosCollector(client)
payload = servicos_collector.build_payload(pagina=1, registros_por_pagina=20)
response = client.request(servicos_collector.get_endpoint(), servicos_collector.get_method(), payload)
print(f"Chaves na resposta: {list(response.keys())}")
print(f"Estrutura completa (primeiros 500 chars):")
print(json.dumps(response, indent=2, ensure_ascii=False)[:500])

# Testa Ordem de Serviço
print("\n2. TESTANDO ORDEM DE SERVIÇO")
print("-"*80)
os_collector = OrdemServicoCollector(client)
payload = os_collector.build_payload(pagina=1, registros_por_pagina=50)
response = client.request(os_collector.get_endpoint(), os_collector.get_method(), payload)
print(f"Chaves na resposta: {list(response.keys())}")
print(f"Estrutura completa (primeiros 500 chars):")
print(json.dumps(response, indent=2, ensure_ascii=False)[:500])

client.close()
