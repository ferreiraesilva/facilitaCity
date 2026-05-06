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
STATUS_URL = f"{BASE_URL}/users/{{user_id}}/status"
CSV_PATH = Path("csv/supervisores_status.csv")

HEADERS = HEADERS_BASE.copy()
HEADERS["content-length"] = "0"

def main():
    if not CSV_PATH.exists(): return

    delim = detect_delimiter(CSV_PATH)
    rows = []
    with open(CSV_PATH, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        rows = [dict(row) for row in reader]

    print(f">>> Iniciando atualização de status para {len(rows)} supervisores...")
    
    for row in rows:
        user_id = row.get("Id", "").strip()
        name = row.get("Nome", "Desconhecido").strip()
        if not user_id: continue

        print(f"  [PROCESSANDO] ID: {user_id} - Nome: {name}...", end="\r")
        
        try:
            resp = requests.put(STATUS_URL.format(user_id=user_id), headers=HEADERS, timeout=20)
            if resp.status_code in [200, 204]:
                print(f"  [OK] Status atualizado: {name} (ID: {user_id})")
            else:
                print(f"  [ERRO] Falha: {resp.status_code}")
        except Exception as e:
            print(f"  [EXCEÇÃO] {str(e)}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()
