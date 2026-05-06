import csv
import requests
import time
import json
from pathlib import Path

# Configurações da API
SEARCH_URL = "https://city.api.facilitavendas.com/api/v1/teams/search/true"
CSV_PATH = Path("csv/imob.csv")


HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXUyJ9.eyJhdWQiOiJodHRwczpcL1wvY2l0eS5mYWNpbGl0YXZlbmRhcy5jb20iLCJnb3Njb3JlLXRva2VuLXVzZXIiOiJleUpwZGlJNkluQjBUMEZ6T0ZoalJVOTZUSGhuUWpod01HYzJhMEU5UFNJc0luWmhiSFZsSWpvaVFVMHhWekpoWEM5c01rbHJUMGhSY210RVRVUlFVMlZJT0ZCMVZHUnNValF4UTF3dk0yUjVVamhWVTBGdU1XcFVUMmh3V1drMWRXTkxkRU5yWkdOMWMyVTBWRWhoVlVkeU1sRlNPV3R5YUhWcE1tOVpPVnBNWnowOUlpd2liV0ZqSWpvaU9XSTNPRGcwTTJNeE4yUTNPR0UwTldabVlqUXhOV1l6WWprNE1qUTJOVGM0WW1NNFpEQmlaVGt5T0dReE9ETTNNVGxoTlRFeU4yVmhNalV6TjJVMFlpSjkiLCJzdWIiOjUxNywiaXNzIjoiaHR0cHM6XC9cL2NpdHkuYXBpLmZhY2lsaXRhdmVuZGFzLmNvbVwvYXBpXC92MVwvYXV0aGVudGljYXRlIiwiaWF0IjoiMTc3NjIwMTIyNiIsImV4cCI6IjE3ODEzODUyMjYiLCJuYmYiOiIxNzc2MjAxMjI2IiwianRpIjoiMWY5NjdjNzcxMmQ1NjdiNjBjOGVkMGYyNGYzM2JiZDUifQ.MzJmMTdiMWJmZDAzYzU2YTVkMjgwNGQwMzhiZTE0MDc2ZTFhMjljZjY4Nzk3NjQ2ZDg0Yzk1MTEyN2JjMGQwNA",
    "goscore-token": "518c2b22e9372a2e8bd0cda98b14e21d",
    "origin": "https://city.facilitavendas.com",
    "referer": "https://city.facilitavendas.com/",
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
    print("Iniciando busca de equipes na API...")
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
        
    print(f"Busca concluída. Total de equipes encontradas: {len(teams_map)}")
    return teams_map


def sync_csv(teams_map):
    # Detectar delimitador
    delim = detect_delimiter(CSV_PATH)
    print(f"Delimitador detectado: '{delim}'")
    
    # Lendo o CSV original
    rows = []
    fieldnames = []
    
    try:
        with open(CSV_PATH, mode="r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=delim)
            fieldnames = list(reader.fieldnames)
            
            # Garantir colunas necessárias
            if "id" not in fieldnames:
                fieldnames.append("id")
                    
            rows = [dict(row) for row in reader]
    except FileNotFoundError:
        print(f"Erro: Arquivo {CSV_PATH} não encontrado.")
        return

    # Mapear nomes já existentes no CSV para evitar duplicatas
    existing_names = {normalize(row.get("nome")): True for row in rows if row.get("nome")}
    
    # Atualizando IDs existentes
    synced_count = 0
    missing_count = 0
    
    for row in rows:
        name = row.get("nome")
        norm_name = normalize(name)
        
        if norm_name in teams_map:
            team_id = teams_map[norm_name]
            row["id"] = team_id
            synced_count += 1
        else:
            missing_count += 1

    # Adicionando novas equipes encontradas na API que não estão no CSV
    added_count = 0
    # Invertemos o teams_map para facilitar a busca por nome (já está normalizado no fetch)
    for norm_name, team_id in teams_map.items():
        if norm_name not in existing_names:
            # Tentar encontrar o nome original (não normalizado) seria ideal, 
            # mas como não temos, usamos o norm_name capitalizado como fallback
            new_row = {
                "id": team_id,
                "nome": norm_name.title() # Fallback: nome capitalizado
            }
            # Preencher outras colunas se existirem
            for col in fieldnames:
                if col not in new_row:
                    new_row[col] = ""
            
            rows.append(new_row)
            added_count += 1
            existing_names[norm_name] = True

    # Salvando o CSV atualizado
    with open(CSV_PATH, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delim)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Sincronização finalizada.")
    print(f"IDs atualizados: {synced_count}")
    print(f"Novas imobiliárias adicionadas: {added_count}")
    print(f"Imobiliárias no CSV não encontradas na API: {missing_count}")
    print(f"CSV atualizado com sucesso em {CSV_PATH}")

def main():
    teams_map = fetch_all_teams()
    if teams_map:
        sync_csv(teams_map)
    else:
        print("Nenhuma equipe foi carregada da API. Verifique os tokens e cookies.")

if __name__ == "__main__":
    main()
