import csv
import requests
import time
import sys
from pathlib import Path

# Garantir que o diretório raiz está no path para importar utils
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from utils.helpers import detect_delimiter, load_env, get_api_config, create_backup

# Carregar config centralizada
BASE_URL, HEADERS_CITY, COOKIES = get_api_config()
CSV_PATH = Path("csv/supervisores.csv")

def main():
    if not CSV_PATH.exists(): return

    print(">>> Iniciando vinculação de supervisores às imobiliárias...")
    env = load_env()
    endpoint = env.get("endpoint", "https://api.facilitaapp.com/").rstrip("/")
    url = f"{endpoint}/platform/v1/supervisors/associate"
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "api-instance": env.get("api-instance", ""),
        "api-key": env.get("api-key", ""),
        "token-user": env.get("token-user", "")
    }

    delim = detect_delimiter(CSV_PATH)
    rows = []
    with open(CSV_PATH, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        rows = [dict(row) for row in reader]

    total = len(rows)
    success_count = 0
    
    for i, row in enumerate(rows, 1):
        sup_id = row.get("id_sup")
        team_id = row.get("id_imob")
        email = row.get("email_sup")
        
        if not sup_id or not team_id:
            continue

        print(f"[{i}/{total}] Vinculando: {email} (ID: {sup_id}) -> Imob: {team_id}")
        
        payload = {
            "supervisor_id": int(sup_id),
            "team_id": int(team_id)
        }
        
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code in [200, 201, 204]:
                print(f"  [OK] Sucesso.")
                success_count += 1
            else:
                print(f"  [ERRO] Status {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"  [EXCEÇÃO] {e}")
        
        time.sleep(0.3)

    print(f"\nFinalizado. Vínculos realizados com sucesso: {success_count}")

if __name__ == "__main__":
    main()
