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
CSV_PATH = Path("csv/gerentes.csv")

HEADERS = HEADERS_BASE.copy()
HEADERS["content-length"] = "0"

def main():
    if not CSV_PATH.exists(): return

    print("\n" + "="*30)
    print("   MENU DE STATUS")
    print("="*30)
    print(" [1] Ativar gerentes (apenas os inativos)")
    print(" [2] Inativar gerentes (apenas os ativos)")
    print(" [0] Cancelar")
    print("="*30)
    
    escolha = input("Escolha uma opção: ").strip()
    if escolha not in ["1", "2"]: return

    target_status = "active" if escolha == "1" else "inactive"
    action_label = "ATIVAR" if escolha == "1" else "INATIVAR"

    delim = detect_delimiter(CSV_PATH)
    rows = []
    with open(CSV_PATH, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        rows = [dict(row) for row in reader]

    total = len(rows)
    print(f">>> Processando {total} gerentes para {action_label}...\n")
    
    for i, row in enumerate(rows, 1):
        user_id = row.get("Id", "").strip()
        name = row.get("Nome", "Desconhecido").strip()
        if not user_id or user_id == "0": continue

        print(f"[{i}/{total}] Gerente: {name} (ID: {user_id})")
        
        try:
            # 1. Consultar status atual
            resp_get = requests.get(EDIT_URL.format(user_id=user_id), headers=HEADERS_BASE, timeout=20)
            if resp_get.status_code != 200: continue
            current_status = resp_get.json().get("status", "unknown")
            
            if current_status == target_status:
                print(f"  [PULADO] Já está {current_status}.")
                continue
            
            # 2. Alternar status
            print(f"  Mudando de {current_status} para {target_status}...")
            resp_put = requests.put(STATUS_URL.format(user_id=user_id), headers=HEADERS, timeout=20)
            if resp_put.status_code in [200, 204]:
                print(f"  [OK] Sucesso.")
        except Exception as e:
            print(f"  [EXCEÇÃO] {str(e)}")
        
        time.sleep(0.3)

if __name__ == "__main__":
    main()
