import requests
import json
import sys
from pathlib import Path

root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))
from utils.helpers import get_api_config

def main():
    url_base, headers, cookies = get_api_config()
    url = f"{url_base}/datatable/managers"
    start = 0
    total = 1
    all_data = []
    
    print(f"Starting sync from {url}")
    
    while start < total:
        payload = {
            "draw": 1,
            "columns": [{"data": "id", "name": "u.id", "searchable": True, "orderable": True, "search": {"value": "", "regex": False}}],
            "start": start,
            "length": 100,
            "search": {"value": "", "regex": False}
        }
        resp = requests.post(url, headers=headers, cookies=cookies, json=payload)
        if resp.status_code != 200:
            print(f"Error {resp.status_code}")
            break
        data = resp.json()
        total = data.get("recordsTotal", 0)
        items = data.get("data", [])
        if not items: break
        all_data.extend(items)
        print(f"Start {start}: Got {len(items)} items. Total so far: {len(all_data)}/{total}")
        start += 100
        
    print(f"Final count: {len(all_data)}")
    
    # Save to a temporary file
    with open("csv/gerentes_new.csv", "w", encoding="utf-8-sig", newline="") as f:
        import csv
        writer = csv.DictWriter(f, fieldnames=["Id", "Nome", "Email", "idImobiliaria", "Imobiliaria"], delimiter=";")
        writer.writeheader()
        for m in all_data:
            writer.writerow({
                "Id": m.get("id"),
                "Nome": m.get("first_name"),
                "Email": m.get("email"),
                "idImobiliaria": m.get("team_id"),
                "Imobiliaria": m.get("team_name")
            })
    print("Saved to csv/gerentes_new.csv")

if __name__ == "__main__":
    main()
