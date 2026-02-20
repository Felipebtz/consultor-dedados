import pandas as pd
from google.cloud import storage
from novo_projeto.config import GCS_BUCKET_NAME, GCS_PROJECT_ID, GCS_CREDENTIALS_PATH
import os
import sys

PEDIDO_ID = '23498'

print("="*60, flush=True)
print(f"BUSCANDO PEDIDO DE COMPRA {PEDIDO_ID}", flush=True)
print("="*60, flush=True)
sys.stdout.flush()

try:
    # Conectar ao GCS
    print("\n[INFO] Conectando ao GCS...", flush=True)
    client = storage.Client.from_service_account_json(
        json_credentials_path=GCS_CREDENTIALS_PATH,
        project=GCS_PROJECT_ID
    )
    bucket = client.bucket(GCS_BUCKET_NAME)
    print(f"[INFO] Conectado ao bucket: {GCS_BUCKET_NAME}", flush=True)
    sys.stdout.flush()
    
    # 1. VERIFICAR BRONZE
    print("\n" + "="*60, flush=True)
    print("[1] VERIFICANDO CAMADA BRONZE - PEDIDOS DE COMPRA", flush=True)
    print("="*60, flush=True)
    sys.stdout.flush()
    
    # Listar arquivos bronze
    print("[INFO] Listando arquivos bronze/pedido_compra/...", flush=True)
    sys.stdout.flush()
    blobs = list(bucket.list_blobs(prefix='bronze/pedido_compra/'))
    arquivos_parquet = [b.name for b in blobs if b.name.endswith('.parquet')]
    print(f"[INFO] Total de arquivos .parquet encontrados: {len(arquivos_parquet)}", flush=True)
    sys.stdout.flush()
    
    # Mostrar alguns arquivos
    if len(arquivos_parquet) > 0:
        print(f"\n[INFO] Primeiros 5 arquivos:", flush=True)
        for arq in arquivos_parquet[:5]:
            print(f"  - {arq}", flush=True)
        sys.stdout.flush()
    
    encontrado_bronze = False
    arquivo_encontrado_bronze = None
    
    for i, arquivo_gcs in enumerate(arquivos_parquet):
        print(f"\n[{i+1}/{len(arquivos_parquet)}] Verificando: {arquivo_gcs}", flush=True)
        sys.stdout.flush()
        
        try:
            # Baixar arquivo temporário
            arquivo_local = f'temp_bronze_compra_{i}.parquet'
            blob = bucket.blob(arquivo_gcs)
            blob.download_to_filename(arquivo_local)
            
            # Carregar e verificar
            df = pd.read_parquet(arquivo_local)
            print(f"  Registros: {len(df)}", flush=True)
            sys.stdout.flush()
            
            # Tentar várias colunas que podem conter o ID do pedido
            colunas_id = ['cNumero', 'nr_pedido', 'nCodPed', 'codigo_pedido', 'cCodIntPed']
            
            for col in colunas_id:
                if col in df.columns:
                    # Verificar se o pedido está neste arquivo
                    mask = df[col].astype(str) == PEDIDO_ID
                    if mask.any():
                        print(f"\n  *** [ENCONTRADO NO BRONZE] ***", flush=True)
                        print(f"  Arquivo: {arquivo_gcs}", flush=True)
                        print(f"  Coluna: {col}", flush=True)
                        sys.stdout.flush()
                        
                        # Mostrar informações do pedido
                        pedido = df[mask].iloc[0]
                        print(f"\n  [DADOS DO PEDIDO NO BRONZE]:", flush=True)
                        colunas_importantes = ['cNumero', 'nCodPed', 'dIncData', 'fl_encerrado_cancelado', 'cEtapa', 'nCodFor']
                        for col_info in colunas_importantes:
                            if col_info in pedido.index:
                                print(f"    {col_info}: {pedido[col_info]}", flush=True)
                        sys.stdout.flush()
                        
                        encontrado_bronze = True
                        arquivo_encontrado_bronze = arquivo_gcs
                        break
            
            # Limpar arquivo temporário
            os.unlink(arquivo_local)
            
            if encontrado_bronze:
                break
                
        except Exception as e:
            print(f"  [ERRO]: {e}", flush=True)
            sys.stdout.flush()
            if os.path.exists(arquivo_local):
                os.unlink(arquivo_local)
    
    if not encontrado_bronze:
        print(f"\n[RESULTADO] Pedido {PEDIDO_ID} NÃO encontrado na camada Bronze", flush=True)
        sys.stdout.flush()
    
    # 2. VERIFICAR SILVER
    print("\n" + "="*60, flush=True)
    print("[2] VERIFICANDO CAMADA SILVER - PEDIDOS DE COMPRA", flush=True)
    print("="*60, flush=True)
    sys.stdout.flush()
    
    arquivo_silver = 'silver/pedidos_compras/pedidos_compras.parquet'
    arquivo_local = 'temp_silver_compra.parquet'
    encontrado_silver = False
    
    try:
        print(f"[INFO] Baixando: {arquivo_silver}", flush=True)
        sys.stdout.flush()
        blob = bucket.blob(arquivo_silver)
        blob.download_to_filename(arquivo_local)
        
        df = pd.read_parquet(arquivo_local)
        print(f"[INFO] Arquivo carregado: {len(df)} registros, {len(df.columns)} colunas", flush=True)
        sys.stdout.flush()
        
        # Verificar colunas
        colunas_id = ['nr_pedido', 'codigo_pedido', 'cNumero', 'nCodPed']
        
        for col in colunas_id:
            if col in df.columns:
                mask = df[col].astype(str) == PEDIDO_ID
                if mask.any():
                    print(f"\n  *** [ENCONTRADO NO SILVER] ***", flush=True)
                    print(f"  Coluna: {col}", flush=True)
                    print(f"  Total de linhas: {mask.sum()}", flush=True)
                    sys.stdout.flush()
                    
                    encontrado_silver = True
                    break
        
        if not encontrado_silver:
            print(f"\n[RESULTADO] Pedido {PEDIDO_ID} NÃO encontrado na camada Silver", flush=True)
            print(f"[DEBUG] Colunas disponíveis: {df.columns.tolist()[:15]}", flush=True)
            sys.stdout.flush()
        
        os.unlink(arquivo_local)
        
    except Exception as e:
        print(f"[ERRO] Erro ao verificar Silver: {e}", flush=True)
        sys.stdout.flush()
        if os.path.exists(arquivo_local):
            os.unlink(arquivo_local)
    
    # 3. VERIFICAR GOLD
    print("\n" + "="*60, flush=True)
    print("[3] VERIFICANDO CAMADA GOLD - PEDIDOS DE COMPRA", flush=True)
    print("="*60, flush=True)
    sys.stdout.flush()
    
    arquivo_gold = 'gold/pedidos/gold_pedido_compra_fato.parquet'
    arquivo_local = 'temp_gold_compra.parquet'
    encontrado_gold = False
    
    try:
        print(f"[INFO] Baixando: {arquivo_gold}", flush=True)
        sys.stdout.flush()
        blob = bucket.blob(arquivo_gold)
        blob.download_to_filename(arquivo_local)
        
        df = pd.read_parquet(arquivo_local)
        print(f"[INFO] Arquivo carregado: {len(df)} registros, {len(df.columns)} colunas", flush=True)
        sys.stdout.flush()
        
        # Verificar colunas
        colunas_id = ['nr_pedido', 'codigo_pedido']
        
        for col in colunas_id:
            if col in df.columns:
                mask = df[col].astype(str) == PEDIDO_ID
                if mask.any():
                    print(f"\n  *** [ENCONTRADO NO GOLD] ***", flush=True)
                    print(f"  Coluna: {col}", flush=True)
                    print(f"  Total de linhas: {mask.sum()}", flush=True)
                    sys.stdout.flush()
                    
                    encontrado_gold = True
                    break
        
        if not encontrado_gold:
            print(f"\n[RESULTADO] Pedido {PEDIDO_ID} NÃO encontrado na camada Gold", flush=True)
            sys.stdout.flush()
        
        os.unlink(arquivo_local)
        
    except Exception as e:
        print(f"[ERRO] Erro ao verificar Gold: {e}", flush=True)
        sys.stdout.flush()
        if os.path.exists(arquivo_local):
            os.unlink(arquivo_local)
    
    # RESUMO FINAL
    print("\n" + "="*80, flush=True)
    print("RESUMO DA INVESTIGAÇÃO", flush=True)
    print("="*80, flush=True)
    print(f"Bronze: {'✓ SIM' if encontrado_bronze else '✗ NÃO'}", flush=True)
    print(f"Silver: {'✓ SIM' if encontrado_silver else '✗ NÃO'}", flush=True)
    print(f"Gold:   {'✓ SIM' if encontrado_gold else '✗ NÃO'}", flush=True)
    sys.stdout.flush()
    
    # DIAGNÓSTICO
    print("\n[DIAGNÓSTICO]", flush=True)
    if encontrado_bronze and not encontrado_silver:
        print("→ O pedido está no Bronze mas NÃO passou para o Silver.", flush=True)
        print("  Possíveis causas:", flush=True)
        print("    1. O script nsilver_pedido_compra_stg.py não foi executado após a última coleta", flush=True)
        print("    2. O pedido pode ter sido filtrado durante o processamento", flush=True)
        print("  Solução:", flush=True)
        print("    Execute: python nsilver_pedido_compra_stg.py", flush=True)
    elif encontrado_bronze and encontrado_silver and not encontrado_gold:
        print("→ O pedido está no Bronze e Silver mas NÃO chegou ao Gold.", flush=True)
        print("  Possíveis causas:", flush=True)
        print("    1. O script ngold_pedido_compra.py não foi executado após a última atualização do Silver", flush=True)
        print("    2. O pedido pode ter sido filtrado/removido durante a transformação Gold", flush=True)
        print("  Solução:", flush=True)
        print("    Execute: python ngold_pedido_compra.py", flush=True)
    elif not encontrado_bronze:
        print("→ O pedido NÃO está na camada Bronze.", flush=True)
        print("  Possíveis causas:", flush=True)
        print("    1. O pedido ainda não foi coletado da API Omie", flush=True)
        print("    2. O pedido pode estar em um status que não é coletado:", flush=True)
        print("       - Pedidos ENCERRADOS (fl_encerrado_cancelado='T')", flush=True)
        print("       - Pedidos CANCELADOS", flush=True)
        print("    3. O pedido pode estar fora do período de coleta configurado", flush=True)
        print("  Verificações:", flush=True)
        print(f"    - Verifique se o pedido {PEDIDO_ID} existe na API Omie", flush=True)
        print(f"    - Verifique o status do pedido (encerrado/cancelado?)", flush=True)
        print(f"    - Verifique a data do pedido e o período de coleta configurado", flush=True)
        print("  Solução:", flush=True)
        print("    Se o pedido estiver encerrado/cancelado, ajuste o script nbronze_pedido_compra.py:", flush=True)
        print("    - Linha 42: lExibirPedidosCancelados: 'T'", flush=True)
        print("    - Linha 43: lExibirPedidosEncerrados: 'T'", flush=True)
        
    sys.stdout.flush()
    
    print("\n" + "="*80, flush=True)
    sys.stdout.flush()

except Exception as e:
    print(f"\n[ERRO CRÍTICO] {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.stdout.flush()

