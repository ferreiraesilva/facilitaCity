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
BASE_URL, HEADERS, COOKIES = get_api_config()
CREATE_BROKER_URL = f"{BASE_URL}/teams/newbroker"
CREATE_MEMBER_BASE_URL = f"{BASE_URL}/teams/{{team_id}}/members"
CSV_PATH = Path("csv/corretores.csv")

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
    if not CSV_PATH.exists(): return
    
    teams_map = fetch_all_teams()
    if not teams_map:
        print("Aviso: Não foi possível carregar as equipes para mapeamento por nome.")

    delim = detect_delimiter(CSV_PATH)
    rows = []
    fieldnames = []
    
    with open(CSV_PATH, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        fieldnames = list(reader.fieldnames)
        if "idImobiliaria" not in fieldnames: fieldnames.append("idImobiliaria")
        if "Id" not in fieldnames: fieldnames.append("Id")
        rows = [dict(row) for row in reader]

    # Pré-processamento: Resolver idImobiliaria se estiver vazio mas tiver o nome
    for row in rows:
        name_imob = row.get("Imobiliaria")
        norm_name = normalize(name_imob)
        if not row.get("idImobiliaria") and norm_name in teams_map:
            row["idImobiliaria"] = teams_map[norm_name]

    print(f">>> Iniciando criação de corretores...")
    success_count = 0
    
    for row in rows:
        email = row.get("Email", "").strip()
        name = row.get("Nome", "").strip()
        manager_id = row.get("manager_id", "").strip()
        team_id = row.get("idImobiliaria", "").strip()
        existing_id = row.get("Id", "").strip()
        
        # Permitir se tiver email e nome, e um dos IDs (manager ou team)
        if not email or not name or existing_id: continue
        
        # O manager_id na API parece ser o ID da equipe (team_id) quando não há um gerente específico
        target_manager_id = manager_id if manager_id else team_id
        if not target_manager_id: continue

        payload = {
            "first_name": name,
            "email": email,
            "password": "123456789",
            "user_group": "broker",
            "manager_id": int(target_manager_id)
        }
        
        try:
            # Sempre usar o endpoint de newbroker conforme o curl funcional
            resp = requests.post(CREATE_BROKER_URL, headers=HEADERS, cookies=COOKIES, json=payload, timeout=20)

            if resp.status_code in [200, 201]:
                data = resp.json()
                new_id = (data.get("data", {}) or {}).get("id") or data.get("id")
                if new_id:
                    row["Id"] = str(new_id)
                    print(f"  [OK] Criado: {name} ({email}) - ID: {new_id}")
                    success_count += 1
                else:
                    print(f"  [ERRO] Resposta sem ID para: {name} ({email})")
            else:
                print(f"  [ERRO] Status {resp.status_code} para: {name} ({email}) - {resp.text[:100]}")
        except Exception as e:
            print(f"  [EXCEÇÃO] {e} para: {name} ({email})")
        
        time.sleep(0.3)

    # Criar backup antes de salvar os IDs novos
    create_backup(CSV_PATH)

    with open(CSV_PATH, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delim)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nFinalizado. Corretores criados: {success_count}")

if __name__ == "__main__":
    main()
