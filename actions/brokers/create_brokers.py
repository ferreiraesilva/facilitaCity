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
BASE_URL, HEADERS, COOKIES = get_api_config()
CREATE_BROKER_URL = f"{BASE_URL}/teams/newbroker"
CSV_PATH = Path("csv/corretores.csv")

def main():
    if not CSV_PATH.exists(): return

    delim = detect_delimiter(CSV_PATH)
    rows = []
    fieldnames = []
    
    with open(CSV_PATH, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        fieldnames = list(reader.fieldnames)
        rows = [dict(row) for row in reader]

    print(f">>> Iniciando criação de corretores...")
    success_count = 0
    
    for row in rows:
        email = row.get("Email", "").strip()
        name = row.get("Nome", "").strip()
        manager_id = row.get("manager_id", "").strip()
        existing_id = row.get("Id", "").strip()
        
        if not email or not name or not manager_id or existing_id: continue

        payload = {
            "first_name": name,
            "email": email,
            "password": "123456789",
            "user_group": "broker",
            "manager_id": int(manager_id)
        }
        
        try:
            resp = requests.post(CREATE_BROKER_URL, headers=HEADERS, cookies=COOKIES, json=payload, timeout=20)
            if resp.status_code in [200, 201]:
                data = resp.json()
                if data.get("status") == "success":
                    new_id = (data.get("data", {}) or {}).get("id") or data.get("id")
                    if new_id:
                        row["Id"] = str(new_id)
                        print(f"  [OK] Criado: {name} ({email}) - ID: {new_id}")
                        success_count += 1
        except Exception:
            pass
        
        time.sleep(0.3)

    with open(CSV_PATH, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delim)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nFinalizado. Corretores criados: {success_count}")

if __name__ == "__main__":
    main()
