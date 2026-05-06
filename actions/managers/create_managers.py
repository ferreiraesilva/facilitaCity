import csv
import requests
import time
import os
import sys
from pathlib import Path

# Garantir que o diretório raiz está no path para importar utils
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from utils.helpers import detect_delimiter, load_env, get_api_config

# Carregar config centralizada
BASE_URL, HEADERS, COOKIES = get_api_config()
CREATE_MEMBER_BASE_URL = f"{BASE_URL}/teams/{{team_id}}/members"
CSV_PATH = Path("csv/gerentes.csv")

def normalize(text):
    if not text:
        return ""
    return " ".join(text.lower().split())

def fetch_all_teams():
    print(">>> Iniciando busca de equipes na API...")
    env = load_env()
    endpoint = env.get("endpoint", "https://api.facilitaapp.com/").rstrip("/")
    url = f"{endpoint}/platform/v1/teams"
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "api-instance": env.get("api-instance", ""),
        "api-key": env.get("api-key", ""),
        "token-user": env.get("token-user", "")
    }
    
    teams_map = {}
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            items = response.json()
            if isinstance(items, list):
                for item in items:
                    name = item.get("name")
                    team_id = item.get("id")
                    if name and team_id:
                        teams_map[normalize(name)] = team_id
    except Exception as e:
        print(f"Exceção ao buscar equipes: {e}")
    return teams_map

def main():
    teams_map = fetch_all_teams()
    if not teams_map:
        print("Erro: Não foi possível carregar as equipes.")
        return

    delim = detect_delimiter(CSV_PATH)
    rows = []
    fieldnames = []
    
    with open(CSV_PATH, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        fieldnames = list(reader.fieldnames)
        if "idImobiliaria" not in fieldnames: fieldnames.append("idImobiliaria")
        if "Id" not in fieldnames: fieldnames.append("Id")
        rows = [dict(row) for row in reader]

    for row in rows:
        name = row.get("Imobiliaria")
        norm_name = normalize(name)
        if not row.get("idImobiliaria") and norm_name in teams_map:
            row["idImobiliaria"] = teams_map[norm_name]

    print(">>> Iniciando criação de usuários gerentes...")
    success_count = 0
    
    for row in rows:
        team_id = row.get("idImobiliaria")
        email = row.get("Email", "").strip()
        name = row.get("Nome", "Gerente").strip()
        existing_id = row.get("Id", "").strip()
        
        if not email or existing_id or not team_id:
            continue

        payload = {
            "first_name": name,
            "email": email,
            "password": "city@123",
            "user_group": "manager"
        }
        
        url = CREATE_MEMBER_BASE_URL.format(team_id=team_id)
        try:
            resp = requests.post(url, headers=HEADERS, cookies=COOKIES, json=payload)
            if resp.status_code in [200, 201]:
                user_data = resp.json()
                new_id = user_data.get("data", {}).get("id") or user_data.get("id")
                if new_id:
                    row["Id"] = str(new_id)
                    print(f"  [OK] Criado: {name} ({email}) - ID: {new_id}")
                    success_count += 1
        except Exception:
            pass
        
        time.sleep(0.2) 

    with open(CSV_PATH, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delim)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nFinalizado. Usuários criados: {success_count}")

if __name__ == "__main__":
    main()
