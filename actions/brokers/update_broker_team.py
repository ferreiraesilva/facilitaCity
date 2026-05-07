import csv
import requests
import sys
import time
from pathlib import Path

# Adicionar raiz ao path
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from utils.helpers import get_api_config

def main():
    CSV_PATH = Path("csv/corretores_troca_time.csv")
    if not CSV_PATH.exists():
        print("Arquivo não encontrado.")
        return

    url_base, headers, cookies = get_api_config()
    
    # Vamos ler o CSV
    with open(CSV_PATH, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)

    print(f">>> Iniciando atualização de {len(rows)} corretores...")

    # Mapeamento cacheado de User ID -> Manager ID (Link ID)
    # Thassiana: 1447 -> 882 (conforme o curl do usuário)
    manager_id_map = {"1447": "882"}

    success_count = 0
    error_count = 0

    for i, row in enumerate(rows):
        broker_id = row.get("Id")
        broker_email = row.get("Email")
        target_manager_user_id = row.get("id_gerente") # User ID (1447)
        
        if not broker_id or not target_manager_user_id:
            print(f"  [PULADO] Linha {i+2}: Faltam dados.")
            continue

        # Precisamos do Manager ID (Link ID). 
        # Se não estiver no cache, assumimos que o usuário quer o que está no cache para a Thassiana.
        manager_link_id = manager_id_map.get(target_manager_user_id)
        
        if not manager_link_id:
            # Se for outro gerente, teríamos que buscar. Mas no momento focamos na Thassiana.
            print(f"  [ERRO] Manager ID (Link) não encontrado para User ID {target_manager_user_id}")
            error_count += 1
            continue

        print(f"  [{i+1}/{len(rows)}] Atualizando {broker_email} (ID {broker_id}) -> Manager {manager_link_id}...")

        url = f"{url_base}/users/{broker_id}"
        
        # O curl usa multipart/form-data
        # Para o requests, passamos como 'files' ou 'data' dependendo da estrutura
        # O curl do usuário:
        # name="user_group" -> broker
        # name="email" -> amanda.reis@homeclass.imb.br
        # name="changeTeamOrManager" -> 882
        
        payload = {
            "user_group": "broker",
            "email": broker_email,
            "changeTeamOrManager": manager_link_id
        }

        # No requests, se passarmos 'data', ele envia como form-encoded. 
        # Mas o Facilita parece aceitar multipart. Vamos tentar data primeiro.
        try:
            resp = requests.post(url, headers=headers, cookies=cookies, data=payload, timeout=30)
            
            if resp.status_code in [200, 201]:
                print(f"    Sucesso!")
                success_count += 1
            else:
                print(f"    Erro {resp.status_code}: {resp.text[:100]}")
                error_count += 1
        except Exception as e:
            print(f"    Exceção: {e}")
            error_count += 1
        
        # Pequeno delay para não sobrecarregar
        time.sleep(0.1)

    print(f"\n>>> Concluído!")
    print(f"Sucesso: {success_count}")
    print(f"Erro: {error_count}")

if __name__ == "__main__":
    main()
