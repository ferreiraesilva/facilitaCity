import csv
import requests
import time
import os
from pathlib import Path

# Configurações da API
SEARCH_URL = "https://city.api.facilitavendas.com/api/v1/teams/search/true"
CREATE_MEMBER_BASE_URL = "https://city.api.facilitavendas.com/api/v1/teams/{team_id}/members"
CSV_PATH = Path("csv/gerentes.csv")


HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXUyJ9.eyJhdWQiOiJodHRwczpcL1wvY2l0eS5mYWNpbGl0YXZlbmRhcy5jb20iLCJnb3Njb3JlLXRva2VuLXVzZXIiOiJleUpwZGlJNkluQjBUMEZ6T0ZoalJVOTZUSGhuUWpod01HYzJhMEU5UFNJc0luWmhiSFZsSWpvaVFVMHhWekpoWEM5c01rbHJUMGhSY210RVRVUlFVMlZJT0ZCMVZHUnNValF4UTF3dk0yUjVVamhWVTBGdU1XcFVUMmh3V1drMWRXTkxkRU5yWkdOMWMyVTBWRWhoVlVkeU1sRlNPV3R5YUhWcE1tOVpPVnBNWnowOUlpd2liV0ZqSWpvaU9XSTNPRGcwTTJNeE4yUTNPR0UwTldabVlqUXhOV1l6WWprNE1qUTJOVGM0WW1NNFpEQmlaVGt5T0dReE9ETTNNVGxoTlRFeU4yVmhNalV6TjJVMFlpSjkiLCJzdWIiOjUxNywiaXNzIjoiaHR0cHM6XC9cL2NpdHkuYXBpLmZhY2lsaXRhdmVuZGFzLmNvbVwvYXBpXC92MVwvYXV0aGVudGljYXRlIiwiaWF0IjoiMTc3NjIwMTIyNiIsImV4cCI6IjE3ODEzODUyMjYiLCJuYmYiOiIxNzc2MjAxMjI2IiwianRpIjoiMWY5NjdjNzcxMmQ1NjdiNjBjOGVkMGYyNGYzM2JiZDUifQ.MzJmMTdiMWJmZDAzYzU2YTVkMjgwNGQwMzhiZTE0MDc2ZTFhMjljZjY4Nzk3NjQ2ZDg0Yzk1MTEyN2JjMGQwNA",
    "goscore-token": "518c2b22e9372a2e8bd0cda98b14e21d",
    "origin": "https://city.facilitavendas.com",
    "referer": "https://city.facilitavendas.com/",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
}

COOKIES = {
    "PHPSESSID": "fa5efebcb74sham4sbhvcnjbd6",
    "refresh_token": "f7cb854840aa834debb6d15c5b023a32",
    "cartalyst_sentry": "eyJpdiI6Im1WeUNQbVRYTFJ0T0UzaERoMlh2S1E9PSIsInZhbHVlIjoia3h0T0czMk5KdTJZbUtIUExUQkF3TFlXbG5SbEpqcHg3c0MwOWF3RWZcL3g0dTNPRXVUQW5tcHBlQ1laSmMrM0lqN2Q1dU9cL2VLMHFUbFltNHdpVVJ3NWZUaDhBSEYyc2gxN2ZoYWJsUUN0ZUVzWU9Bd2dGTG16QW4zeVpobkkzUCIsIm1hYyI6ImFkNDI3M2MyOTU1NmRlMzc0ZWNhNmNlMDBiMjNjMjBjOWU1ZWZkNDMxM2RkN2ZlNWE2ODUyNGZjOGMyMjQ2YTEifQ==",
}

def normalize(text):
    if not text:
        return ""
    return " ".join(text.lower().split())

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
        if response.status_code != 200:
            print(f"Erro ao buscar equipes: {response.status_code}")
            print(response.text)
            return teams_map
            
        items = response.json()
        if isinstance(items, list):
            for item in items:
                name = item.get("name")
                team_id = item.get("id")
                if name and team_id:
                    teams_map[normalize(name)] = team_id
        else:
            print("Resposta da API não é uma lista.")
    except Exception as e:
        print(f"Exceção ao buscar equipes: {e}")
        
    print(f">>> Busca concluída. {len(teams_map)} equipes carregadas.")
    return teams_map

    return teams_map

def main():
    # 1. Carregar mapeamento de times
    teams_map = fetch_all_teams()
    if not teams_map:
        print("Erro: Não foi possível carregar as equipes.")
        return

    # 2. Ler e sincronizar CSV
    delim = detect_delimiter(CSV_PATH)
    print(f">>> Lendo CSV: {CSV_PATH} (Delimitador: '{delim}')")
    rows = []
    fieldnames = []
    
    with open(CSV_PATH, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        fieldnames = list(reader.fieldnames)
        if "idImobiliaria" not in fieldnames:
            fieldnames.append("idImobiliaria")
        if "Id" not in fieldnames:
            fieldnames.append("Id")
        rows = [dict(row) for row in reader]

    # Preenchendo idImobiliaria
    synced_count = 0
    for row in rows:
        name = row.get("Imobiliaria")
        norm_name = normalize(name)
        # Se não tem ID mas tem nome, tenta buscar
        if not row.get("idImobiliaria") and norm_name in teams_map:
            row["idImobiliaria"] = teams_map[norm_name]
            synced_count += 1
        elif row.get("idImobiliaria"):
            synced_count += 1
            
    print(f">>> Sincronização offline: {synced_count} IDs mapeados.")


    # 3. Criar membros
    print(">>> Iniciando criação de usuários gerentes...")
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for row in rows:
        team_id = row.get("idImobiliaria")
        email = row.get("Email", "").strip()
        name = row.get("Nome", "Gerente").strip()
        existing_id = row.get("Id", "").strip()
        
        if not email:
            skip_count += 1
            continue
            
        if existing_id:
            print(f"  [INFO] Pulando {name}: Já possui ID {existing_id}")
            skip_count += 1
            continue
            
        if not team_id:
            print(f"  [AVISO] Pulando {name}: Time '{row.get('Imobiliaria')}' não encontrado na API.")
            fail_count += 1
            continue

        # Payload de criação
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
                # Tenta capturar o ID do gerente criado
                new_id = user_data.get("data", {}).get("id") or user_data.get("id")
                if new_id:
                    row["Id"] = str(new_id)
                    print(f"  [OK] Criado: {name} ({email}) no time {team_id} - ID: {new_id}")
                else:
                    print(f"  [OK] Criado: {name} ({email}) no time {team_id} (ID não retornado no JSON)")
                success_count += 1
            else:

                reason = "Erro desconhecido"
                try:
                    reason = resp.json().get("msg", resp.text)
                except:
                    reason = resp.text
                print(f"  [ERRO] Falha ao criar {name}: {resp.status_code} - {reason}")
                fail_count += 1
        except Exception as e:
            print(f"  [EXCEÇÃO] {name}: {str(e)}")
            fail_count += 1
        
        time.sleep(0.2) # Evitar rate limit

    # 4. Salvar CSV com team_id atualizado
    with open(CSV_PATH, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delim)
        writer.writeheader()
        writer.writerows(rows)

    print("\n" + "="*40)
    print(f"RESULTADO FINAL:")
    print(f"Total de registros: {len(rows)}")
    print(f"Usuários criados: {success_count}")
    print(f"Falhas/Avisos: {fail_count}")
    print(f"Pulados (sem e-mail): {skip_count}")
    print(f"CSV atualizado com team_id: {CSV_PATH}")
    print("="*40)

if __name__ == "__main__":
    main()
