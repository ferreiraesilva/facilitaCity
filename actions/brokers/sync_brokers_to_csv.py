import requests
import csv
import sys
from pathlib import Path

# Garantir que o diretório raiz está no path para importar utils
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from utils.helpers import detect_delimiter, get_api_config

# Carregar config centralizada
BASE_URL, HEADERS, COOKIES = get_api_config()
URL = f"{BASE_URL}/datatable/brokers"
CSV_PATH = Path("csv/corretores.csv")

PAYLOAD_TEMPLATE = {
    "draw": 1,
    "columns": [
        {"data": "broker_id", "name": "teams_brokers.id", "searchable": True, "orderable": False, "search": {"value": "", "regex": False}},
        {"data": "first_name", "name": "u.first_name", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
        {"data": "email", "name": "u.email", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
        {"data": "team_name", "name": "t.name", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
        {"data": "broker_id", "name": "teams_brokers.id", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
        {"data": "broker_created_at", "name": "u.created_at", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
        {"data": "team_id", "name": "t.id", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}
    ],
    "order": [{"column": 0, "dir": "desc"}],
    "start": 0,
    "length": 100,
    "search": {"value": "", "regex": False}
}

def fetch_all_brokers():
    all_data = []
    start = 0
    length = 100
    total_records = 1
    
    print(">>> Iniciando consulta à API datatable de corretores...")
    
    while start < total_records:
        payload = PAYLOAD_TEMPLATE.copy()
        payload["start"] = start
        payload["length"] = length
        
        try:
            resp = requests.post(URL, headers=HEADERS, cookies=COOKIES, json=payload, timeout=30)
            if resp.status_code != 200: break
            data = resp.json()
            total_records = data.get("recordsTotal", 0)
            items = data.get("data", [])
            if not items: break
            all_data.extend(items)
            start += length
        except Exception: break
            
    print(f"\n>>> Consulta concluída. Total coletado: {len(all_data)}")
    return all_data

def save_to_csv(brokers):
    delim = detect_delimiter(CSV_PATH)
    fieldnames = ["Id", "Nome", "Email", "manager_id", "idImobiliaria", "Imobiliaria"]
    
    with open(CSV_PATH, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delim)
        writer.writeheader()
        for b in brokers:
            writer.writerow({
                "Id": b.get("id"),
                "Nome": b.get("first_name"),
                "Email": b.get("email"),
                "manager_id": "", 
                "idImobiliaria": b.get("team_id"),
                "Imobiliaria": b.get("team_name")
            })
    print(f">>> CSV atualizado: {CSV_PATH}")

def main():
    brokers = fetch_all_brokers()
    if brokers: save_to_csv(brokers)

if __name__ == "__main__":
    main()
