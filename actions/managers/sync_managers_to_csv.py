import requests
import csv
import json
import sys
from pathlib import Path

# Garantir que o diretório raiz está no path para importar utils
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from utils.helpers import detect_delimiter, get_api_config, create_backup

# Carregar config centralizada
BASE_URL, HEADERS, COOKIES = get_api_config()
URL = f"{BASE_URL}/datatable/managers"
CSV_PATH = Path("csv/gerentes.csv")

PAYLOAD_TEMPLATE = {
    "draw": 1,
    "columns": [
        {"data": "manager_id", "name": "teams_managers.id", "searchable": True, "orderable": False, "search": {"value": "", "regex": False}},
        {"data": "first_name", "name": "u.first_name", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
        {"data": "email", "name": "u.email", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
        {"data": "team_name", "name": "t.name", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
        {"data": "manager_id", "name": "teams_managers.id", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
        {"data": "manager_created_at", "name": "u.created_at", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
        {"data": "team_id", "name": "t.id", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}
    ],
    "order": [{"column": 0, "dir": "desc"}],
    "start": 0,
    "length": 100,
    "search": {"value": "", "regex": False}
}

def fetch_all_managers():
    all_data = []
    start = 0
    length = 100
    total_records = 1
    
    print(">>> Iniciando consulta à API datatable de gerentes...")
    
    while start < total_records:
        payload = PAYLOAD_TEMPLATE.copy()
        payload["start"] = start
        payload["length"] = length
        
        try:
            resp = requests.post(URL, headers=HEADERS, cookies=COOKIES, json=payload, timeout=30)
            if resp.status_code != 200:
                print(f"  [ERRO] API retornou status {resp.status_code}: {resp.text[:200]}")
                break
            data = resp.json()
            total_records = data.get("recordsTotal", 0)
            items = data.get("data", [])
            if not items: break
            all_data.extend(items)
            start += length
        except Exception as e:
            print(f"  [EXCEÇÃO] {e}")
            break
            
    print(f">>> Consulta concluída. Total de gerentes coletados: {len(all_data)}")
    return all_data

def save_to_csv(managers):
    delim = detect_delimiter(CSV_PATH)
    fieldnames = ["Id", "Nome", "Email", "idImobiliaria", "Imobiliaria"]
    
    with open(CSV_PATH, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delim)
        writer.writeheader()
        for m in managers:
            writer.writerow({
                "Id": m.get("id") or m.get("manager_id"),
                "Nome": m.get("first_name"),
                "Email": m.get("email"),
                "idImobiliaria": m.get("team_id"),
                "Imobiliaria": m.get("team_name")
            })
    print(f">>> CSV atualizado: {CSV_PATH}")

def main():
    managers = fetch_all_managers()
    if managers:
        create_backup(CSV_PATH)
        save_to_csv(managers)

if __name__ == "__main__":
    main()
