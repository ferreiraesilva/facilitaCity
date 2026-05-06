import csv
import requests
import time
from pathlib import Path

# Configurações da API
SEARCH_URL = "https://city.api.facilitavendas.com/api/v1/teams/search/true"
DETAIL_URL = "https://city.api.facilitavendas.com/api/v1/teams/{team_id}"
CSV_PATH = Path("csv/sup_imob.csv")

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXUyJ9.eyJhdWQiOiJodHRwczpcL1wvY2l0eS5mYWNpbGl0YXZlbmRhcy5jb20iLCJnb3Njb3JlLXRva2VuLXVzZXIiOiJleUpwZGlJNkluQjBUMEZ6T0ZoalJVOTZUSGhuUWpod01HYzJhMEU5UFNJc0luWmhiSFZsSWpvaVFVMHhWekpoWEM5c01rbHJUMGhSY210RVRVUlFVMlZJT0ZCMVZHUnNValF4UTF3dk0yUjVVamhWVTBGdU1XcFVUMmh3V1drMWRXTkxkRU5yWkdOMWMyVTBWRWhoVlVkeU1sRlNPV3R5YUhWcE1tOVpPVnBNWnowOUlpd2liV0ZqSWpvaU9XSTNPRGcwTTJNeE4yUTNPR0UwTldabVlqUXhOV1l6WWprNE1qUTJOVGM0WW1NNFpEQmlaVGt5T0dReE9ETTNNVGxoTlRFeU4yVmhNalV6TjJVMFlpSjkiLCJzdWIiOjUxNywiaXNzIjoiaHR0cHM6XC9cL2NpdHkuYXBpLmZhY2lsaXRhdmVuZGFzLmNvbVwvYXBpXC92MVwvYXV0aGVudGljYXRlIiwiaWF0IjoiMTc3NjIwMTIyNiIsImV4cCI6IjE3ODEzODUyMjYiLCJuYmYiOiIxNzc2MjAxMjI2IiwianRpIjoiMWY5NjdjNzcxMmQ1NjdiNjBjOGVkMGYyNGYzM2JiZDUifQ.MzJmMTdiMWJmZDAzYzU2YTVkMjgwNGQwMzhiZTE0MDc2ZTFhMjljZjY4Nzk3NjQ2ZDg0Yzk1MTEyN2JjMGQwNA",
    "goscore-token": "518c2b22e9372a2e8bd0cda98b14e21d",
}

COOKIES = {
    "PHPSESSID": "fa5efebcb74sham4sbhvcnjbd6",
    "refresh_token": "f7cb854840aa834debb6d15c5b023a32",
}

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
    print(">>> Buscando lista de equipes na API...", flush=True)
    env = load_env()
    endpoint = env.get("endpoint", "https://api.facilitaapp.com/").rstrip("/")
    url = f"{endpoint}/platform/v1/teams"
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "api-instance": env.get("api-instance", ""),
        "api-key": env.get("api-key", ""),
        "token-user": env.get("token-user", "")
    }
    
    teams = []
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"Erro ao buscar equipes: {response.status_code}", flush=True)
            print(response.text, flush=True)
            return teams
            
        items = response.json()
        if isinstance(items, list):
            for item in items:
                teams.append({
                    "id": item.get("id"),
                    "name": item.get("name")
                })
        else:
            print("Resposta da API não é uma lista.", flush=True)
    except Exception as e:
        print(f"Exceção ao buscar equipes: {e}", flush=True)
        
    print(f">>> {len(teams)} equipes encontradas.", flush=True)
    return teams

    return teams

def fetch_team_supervisors(team_id):
    env = load_env()
    endpoint = env.get("endpoint", "https://api.facilitaapp.com/").rstrip("/")
    url = f"{endpoint}/platform/v1/supervisors"
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "api-instance": env.get("api-instance", ""),
        "api-key": env.get("api-key", ""),
        "token-user": env.get("token-user", "")
    }
    
    params = {"team_id": team_id}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            items = response.json()
            return items if isinstance(items, list) else []
    except Exception as e:
        print(f"\nExceção ao buscar supervisores do time {team_id}: {e}", flush=True)
    return []


def save_csv(rows):
    fieldnames = ["id_imob", "nome_imob", "id_sup", "nome_sup"]
    with open(CSV_PATH, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

def main():
    teams = fetch_all_teams()
    if not teams:
        print("Nenhuma equipe para processar.", flush=True)
        return

    print(">>> Consultando supervisores vinculados a cada equipe...", flush=True)
    rows = []
    
    total = len(teams)
    for i, team in enumerate(teams, start=1):
        team_id = team["id"]
        team_name = team["name"]
        
        print(f"[{i}/{total}] Consultando: {team_name} ...", flush=True)
        
        supervisors = fetch_team_supervisors(team_id)
        
        for sup in supervisors:
            rows.append({
                "id_imob": str(team_id),
                "nome_imob": team_name,
                "id_sup": str(sup.get("id")),
                "nome_sup": sup.get("first_name")
            })
            
        # Salva incrementalmente a cada 20 equipes
        if i % 20 == 0:
            save_csv(rows)
            print(f"   [AUTO-SAVE] {len(rows)} vínculos salvos até agora.", flush=True)
            
        time.sleep(0.1)
        
    # Salva o resultado final
    save_csv(rows)
    print(f"\n>>> Consulta concluída. Total de {len(rows)} vínculos salvos em {CSV_PATH}", flush=True)

if __name__ == "__main__":
    main()
