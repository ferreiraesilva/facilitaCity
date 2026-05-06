import csv
import requests
import time
from pathlib import Path

# Configurações
CREATE_MEMBER_BASE_URL = "https://city.api.facilitavendas.com/api/v1/teams/{team_id}/members"
BASE_URL = "https://city.api.facilitavendas.com/api/v1/users"
SUP_IMOB_CSV = Path("csv/sup_imob.csv")

HEADERS_OLD = {
    "accept": "application/json, text/plain, */*",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXUyJ9.eyJhdWQiOiJodHRwczpcL1wvY2l0eS5mYWNpbGl0YXZlbmRhcy5jb20iLCJnb3Njb3JlLXRva2VuLXVzZXIiOiJleUpwZGlJNkluQjBUMEZ6T0ZoalJVOTZUSGhuUWpod01HYzJhMEU5UFNJc0luWmhiSFZsSWpvaVFVMHhWekpoWEM5c01rbHJUMGhSY210RVRVUlFVMlZJT0ZCMVZHUnNValF4UTF3dk0yUjVVamhWVTBGdU1XcFVUMmh3V1drMWRXTkxkRU5yWkdOMWMyVTBWRWhoVlVkeU1sRlNPV3R5YUhWcE1tOVpPVnBNWnowOUlpd2liV0ZqSWpvaU9XSTNPRGcwTTJNeE4yUTNPR0UwTldabVlqUXhOV1l6WWprNE1qUTJOVGM0WW1NNFpEQmlaVGt5T0dReE9ETTNNVGxoTlRFeU4yVmhNalV6TjJVMFlpSjkiLCJzdWIiOjUxNywiaXNzIjoiaHR0cHM6XC9cL2NpdHkuYXBpLmZhY2lsaXRhdmVuZGFzLmNvbVwvYXBpXC92MVwvYXV0aGVudGljYXRlIiwiaWF0IjoiMTc3NjIwMTIyNiIsImV4cCI6IjE3ODEzODUyMjYiLCJuYmYiOiIxNzc2MjAxMjI2IiwianRpIjoiMWY5NjdjNzcxMmQ1NjdiNjBjOGVkMGYyNGYzM2JiZDUifQ.MzJmMTdiMWJmZDAzYzU2YTVkMjgwNGQwMzhiZTE0MDc2ZTFhMjljZjY4Nzk3NjQ2ZDg0Yzk1MTEyN2JjMGQwNA",
    "goscore-token": "518c2b22e9372a2e8bd0cda98b14e21d",
    "origin": "https://city.facilitavendas.com",
    "referer": "https://city.facilitavendas.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
}

COOKIES_OLD = {
    "PHPSESSID": "fa5efebcb74sham4sbhvcnjbd6",
    "refresh_token": "f7cb854840aa834debb6d15c5b023a32",
    "cartalyst_sentry": "eyJpdiI6Im1WeUNQbVRYTFJ0T0UzaERoMlh2S1E9PSIsInZhbHVlIjoia3h0T0czMk5KdTJZbUtIUExUQkF3TFlXbG5SbEpqcHg3c0MwOWF3RWZcL3g0dTNPRXVUQW5tcHBlQ1laSmMrM0lqN2Q1dU9cL2VLMHFUbFltNHdpVVJ3NWZUaDhBSEYyc2gxN2ZoYWJsUUN0ZUVzWU9Bd2dGTG16QW4zeVpobkkzUCIsIm1hYyI6ImFkNDI3M2MyOTU1NmRlMzc0ZWNhNmNlMDBiMjNjMjBjOWU1ZWZkNDMxM2RkN2ZlNWE2ODUyNGZjOGMyMjQ2YTEifQ==",
}

def detect_delimiter(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            header = f.readline()
            if header.count(';') > header.count(','):
                return ';'
            return ','
    except Exception:
        return ';' # Fallback


def load_env():
    env = {}
    env_path = Path(".env")
    if env_path.exists():
        with env_path.open("r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    env[k.strip()] = v.strip()
    return env

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
                    if "id" in item:
                        valid_ids.add(str(item["id"]))
    except Exception as e:
        print(f"Erro ao buscar equipes: {e}")
        
    print(f">>> {len(valid_ids)} equipes válidas encontradas.")
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
    
    response = requests.post(url, headers=HEADERS_OLD, cookies=COOKIES_OLD, files=payload)
    
    if response.status_code == 200:
        try:
            result = response.json()
            if result.get("status") == "success":
                print(f"  [OK] Vínculos atualizados com sucesso!")
            else:
                print(f"  [ERRO] API retornou erro ao vincular: {result.get('msg')}")
        except:
            print(f"  [OK] Requisição aceita (Resposta não JSON).")
    else:
        print(f"  [ERRO] Falha ao vincular (Status {response.status_code}): {response.text}")

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
        resp = requests.post(url, headers=HEADERS_OLD, cookies=COOKIES_OLD, json=payload)
        if resp.status_code in [200, 201]:
            user_data = resp.json()
            new_id = user_data.get("data", {}).get("id") or user_data.get("id")
            if new_id:
                print(f"  [OK] Supervisor criado com sucesso! ID: {new_id}")
                return str(new_id)
            else:
                print(f"  [OK] Supervisor criado (ID não retornado).")
                return None
        else:
            reason = "Erro desconhecido"
            try:
                reason = resp.json().get("msg", resp.text)
            except:
                reason = resp.text
            print(f"  [ERRO] Falha ao criar supervisor: {resp.status_code} - {reason}")
            return None
    except Exception as e:
        print(f"  [EXCEÇÃO] Falha ao criar supervisor: {str(e)}")
        return None

def main():
    print("=== CRIAÇÃO E VÍNCULO DE SUPERVISORES EM LOTE ===")
    
    if not SUP_IMOB_CSV.exists():
        print(f"Erro: {SUP_IMOB_CSV} não encontrado.")
        return
        
    valid_teams = fetch_valid_team_ids()
    
    # Detectar delimitador
    delim = detect_delimiter(SUP_IMOB_CSV)
    print(f"Delimitador detectado em {SUP_IMOB_CSV.name}: '{delim}'")

    # Ler todas as linhas do CSV
    rows = []
    with open(SUP_IMOB_CSV, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=delim)
        fieldnames = reader.fieldnames
        rows = [dict(row) for row in reader]
        
    # Agrupar por supervisor (usando e-mail como chave única)
    groups = {}
    for row in rows:
        email = row.get("email_sup", "").strip()
        name = row.get("nome_sup", "").strip()
        sup_id = row.get("id_sup", "").strip()
        team_id = row.get("id_imob", "").strip()
        
        if not email:
            continue
            
        if email not in groups:
            groups[email] = {
                "name": name,
                "id": sup_id,
                "teams": []
            }
            
        if team_id:
            groups[email]["teams"].append(team_id)

    # Processar cada supervisor
    csv_updated = False
    
    for email, info in groups.items():
        sup_id = info["id"]
        name = info["name"]
        teams = info["teams"]
        
        # Filtra apenas equipes válidas
        filtered_teams = [t for t in teams if t in valid_teams]
        
        if not filtered_teams:
            print(f"[AVISO] Nenhuma imobiliária válida encontrada para {name}.")
            continue
            
        # Se não tem ID, cria primeiro
        if not sup_id:
            initial_team = filtered_teams[0]
            new_id = create_supervisor(name, email, initial_team)
            if new_id:
                sup_id = new_id
                info["id"] = new_id
                csv_updated = True
                # Atualiza nas linhas para salvar depois
                for row in rows:
                    if row.get("email_sup", "").strip() == email:
                        row["id_sup"] = new_id
            else:
                print(f"[ERRO] Pulando vínculos de {name} pois a criação falhou.")
                continue
                
        # Vincula nas outras imobiliárias
        if sup_id:
            associate_supervisor(sup_id, email, name, filtered_teams)
            time.sleep(0.5)

    # Salvar CSV se atualizamos IDs
    if csv_updated:
        print(f"\nGravando novos IDs no arquivo {SUP_IMOB_CSV}...")
        with open(SUP_IMOB_CSV, mode="w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delim)
            writer.writeheader()
            writer.writerows(rows)
            
    print("\nProcesso concluído.")

if __name__ == "__main__":
    main()
