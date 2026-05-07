import requests
import csv
import json
import sys
from pathlib import Path

# Garantir que o diretório raiz está no path para importar utils
root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

from utils.helpers import get_api_config

def main():
    BASE_URL, HEADERS, COOKIES = get_api_config()
    URL = f"{BASE_URL}/datatable/managers"
    CSV_PATH = Path("csv/gerentes.csv")
    
    all_data = []
    start = 0
    length = 100 
    total_records = 1
    
    print(f">>> Iniciando sincronização completa de gerentes (Nome ao final)...")
    
    while start < total_records:
        payload = {
            "draw": 1,
            "columns": [
                {"data": "manager_id", "name": "teams_managers.id", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "id", "name": "u.id"},
                {"data": "first_name", "name": "u.first_name"},
                {"data": "email", "name": "u.email"},
                {"data": "team_name", "name": "t.name"},
                {"data": "team_id", "name": "t.id"}
            ],
            "order": [{"column": 0, "dir": "desc"}],
            "start": start,
            "length": length,
            "search": {"value": "", "regex": False}
        }
        
        try:
            resp = requests.post(URL, headers=HEADERS, cookies=COOKIES, json=payload, timeout=60)
            if resp.status_code != 200:
                print(f"  [ERRO] API {resp.status_code}: {resp.text[:200]}")
                break
                
            data = resp.json()
            total_records = data.get("recordsTotal", 0)
            items = data.get("data", [])
            
            if not items:
                break
                
            all_data.extend(items)
            print(f"  Coletados {len(all_data)}/{total_records}...")
            start += length
            
        except Exception as e:
            print(f"  [EXCEÇÃO] {e}")
            break
            
    if all_data:
        print(f">>> Salvando {len(all_data)} gerentes em {CSV_PATH}")
        with open(CSV_PATH, mode="w", encoding="utf-8-sig", newline="") as f:
            # Novo cabeçalho com Nome ao final
            fieldnames = ["Id", "Email", "idImobiliaria", "Imobiliaria", "manager_id", "Nome"]
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
            writer.writeheader()
            for m in all_data:
                writer.writerow({
                    "Id": m.get("id"),
                    "Email": m.get("email"),
                    "idImobiliaria": m.get("team_id"),
                    "Imobiliaria": m.get("team_name"),
                    "manager_id": m.get("manager_id"),
                    "Nome": m.get("first_name")
                })
        print(">>> Sincronização concluída com sucesso!")
    else:
        print(">>> Nenhum dado coletado.")

if __name__ == "__main__":
    main()
