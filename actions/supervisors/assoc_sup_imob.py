import csv
import requests
import time
import sys
from pathlib import Path

# Garantir que o diretório raiz está no path para importar utils
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from utils.helpers import detect_delimiter, load_env, get_api_config

# Carregar config centralizada
BASE_URL_CENTRAL, HEADERS, COOKIES = get_api_config()
CREATE_MEMBER_BASE_URL = f"{BASE_URL_CENTRAL}/teams/{{team_id}}/members"
BASE_URL = f"{BASE_URL_CENTRAL}/users"
SUP_IMOB_CSV = Path("csv/supervisores.csv")

def fetch_valid_team_ids():
    print(">>> Buscando equipes válidas na API...")
    env = load_env()
    endpoint = env.get("endpoint", "https://api.facilitaapp.com/").rstrip("/")
    url = f"{endpoint}/platform/v1/teams"
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "api-instance": env.get("api-instance", ""),
        "api-key": env.get("api-key", ""),
        "token-user": env.get("token-user", "")
    }
    
    valid_ids = set()
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            items = response.json()
            if isinstance(items, list):
                for item in items:
                    if "id" in item: valid_ids.add(str(item["id"]))
    except Exception:
        pass
    return valid_ids

def associate_supervisor(user_id, email, name, team_ids):
    url = f"{BASE_URL}/{user_id}"
    payload = {
        "user_group": (None, "supervisor"),
        "email": (None, email),
    }
    for i, tid in enumerate(team_ids):
        payload[f"changeTeamOrManager[{i}]"] = (None, str(tid))
    
    print(f"Associando {name} (ID {user_id}) a {len(team_ids)} equipes...")
    response = requests.post(url, headers=HEADERS, cookies=COOKIES, files=payload)
    if response.status_code == 200:
        print(f"  [OK] Sucesso.")
    else:
        print(f"  [ERRO] Status {response.status_code}")

def create_supervisor(name, email, team_id):
    print(f"Criando supervisor {name} ({email}) na imobiliária inicial {team_id}...")
    payload = {
        "first_name": name,
        "email": email,
        "password": "city@123",
        "user_group": "supervisor"
    }
    url = CREATE_MEMBER_BASE_URL.format(team_id=team_id)
    try:
        resp = requests.post(url, headers=HEADERS, cookies=COOKIES, json=payload)
        if resp.status_code in [200, 201]:
            user_data = resp.json()
            new_id = user_data.get("data", {}).get("id") or user_data.get("id")
            return str(new_id) if new_id else None
    except Exception:
        pass
    return None

def main():
    if not SUP_IMOB_CSV.exists(): return
        
    valid_teams = fetch_valid_team_ids()
    delim = detect_delimiter(SUP_IMOB_CSV)

    rows = []
    with open(SUP_IMOB_CSV, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delim)
        fieldnames = reader.fieldnames
        rows = [dict(row) for row in reader]
        
    groups = {}
    for row in rows:
        email = row.get("email_sup", "").strip()
        if not email: continue
        if email not in groups:
            groups[email] = {"name": row.get("nome_sup", ""), "id": row.get("id_sup", ""), "teams": []}
        if row.get("id_imob"): groups[email]["teams"].append(row["id_imob"])

    csv_updated = False
    for email, info in groups.items():
        sup_id = info["id"]
        teams = [t for t in info["teams"] if t in valid_teams]
        if not teams: continue
            
        if not sup_id:
            new_id = create_supervisor(info["name"], email, teams[0])
            if new_id:
                sup_id = new_id
                csv_updated = True
                for row in rows:
                    if row.get("email_sup", "").strip() == email: row["id_sup"] = new_id
                
        if sup_id:
            associate_supervisor(sup_id, email, info["name"], teams)
            time.sleep(0.5)

    if csv_updated:
        with open(SUP_IMOB_CSV, mode="w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delim)
            writer.writeheader()
            writer.writerows(rows)

if __name__ == "__main__":
    main()
