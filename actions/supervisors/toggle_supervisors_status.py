import csv
import requests
import time
import sys
from pathlib import Path

# Garantir que o diretório raiz está no path para importar utils
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from utils.helpers import detect_delimiter, get_api_config

# Carregar config centralizada
BASE_URL, HEADERS_BASE, COOKIES = get_api_config()
EDIT_URL = f"{BASE_URL}/users/{{user_id}}/edit"
STATUS_URL = f"{BASE_URL}/users/{{user_id}}/status"
CSV_PATH = Path("csv/supervisores.csv")

HEADERS = HEADERS_BASE.copy()
HEADERS["content-length"] = "0"

def main():
    if not CSV_PATH.exists(): return

    print("\n" + "="*40)
    print("   MENU DE STATUS SUPERVISORES (Lote)")
    print("="*40)
    print(" [1] Ativar supervisores (apenas os inativos)")
    print(" [2] Inativar supervisores (apenas os ativos)")
    print(" [0] Cancelar")
    print("="*40)
    
    escolha = input("Escolha uma opção: ").strip()
    if escolha not in ["1", "2"]: return

    target_status = "active" if escolha == "1" else "inactive"
    action_label = "ATIVAR" if escolha == "1" else "INATIVAR"

    delim = detect_delimiter(CSV_PATH)
    supervisors = {} 
    with open(CSV_PATH, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        for row in reader:
            id_sup = row.get("id_sup", "").strip()
            if id_sup and id_sup != "0":
                supervisors[id_sup] = row.get("nome_sup", "Desconhecido").strip()

    total = len(supervisors)
    print(f">>> Processando {total} supervisores únicos para {action_label}...\n")
    
    for i, (user_id, name) in enumerate(supervisors.items(), 1):
        print(f"[{i}/{total}] Supervisor: {name} (ID: {user_id})")
        
        try:
            resp_get = requests.get(EDIT_URL.format(user_id=user_id), headers=HEADERS_BASE, timeout=20)
            if resp_get.status_code != 200: continue
            current_status = resp_get.json().get("status", "unknown")
            
            if current_status == target_status:
                print(f"  [PULADO] Já está {current_status}.")
                continue
            
            print(f"  Mudando de {current_status} para {target_status}...")
            resp_put = requests.put(STATUS_URL.format(user_id=user_id), headers=HEADERS, timeout=20)
            if resp_put.status_code in [200, 204]:
                print(f"  [OK] Sucesso.")
        except Exception as e:
            print(f"  [EXCEÇÃO] {str(e)}")
        
        time.sleep(0.3)

if __name__ == "__main__":
    main()
