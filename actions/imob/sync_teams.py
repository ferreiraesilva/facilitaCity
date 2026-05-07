import csv
import requests
import time
import json
import sys
from pathlib import Path

# Garantir que o diretório raiz está no path para importar utils
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from utils.helpers import detect_delimiter, load_env, get_api_config, create_backup

# Carregar config centralizada (para obter base_url se necessário)
BASE_URL, _, _ = get_api_config()
CSV_PATH = Path("csv/imobiliarias.csv")

def normalize(text):
    if not text:
        return ""
    return " ".join(text.lower().split())

def fetch_all_teams():
    print("Iniciando busca de equipes na API...")
    env = load_env()
    # Este script usa a API de plataforma v1
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
            return teams_map
            
        items = response.json()
        if isinstance(items, list):
            for item in items:
                name = item.get("name")
                team_id = item.get("id")
                if name and team_id:
                    teams_map[normalize(name)] = team_id
    except Exception as e:
        print(f"Exceção ao buscar equipes: {e}")
        
    print(f"Busca concluída. Total de equipes encontradas: {len(teams_map)}")
    return teams_map

def sync_csv(teams_map):
    delim = detect_delimiter(CSV_PATH)
    
    rows = []
    fieldnames = []
    
    try:
        with open(CSV_PATH, mode="r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=delim)
            fieldnames = list(reader.fieldnames)
            if "id" not in fieldnames:
                fieldnames.append("id")
            rows = [dict(row) for row in reader]
    except FileNotFoundError:
        return

    existing_names = {normalize(row.get("nome")): True for row in rows if row.get("nome")}
    
    synced_count = 0
    missing_count = 0
    
    for row in rows:
        name = row.get("nome")
        norm_name = normalize(name)
        if norm_name in teams_map:
            row["id"] = teams_map[norm_name]
            synced_count += 1
        else:
            missing_count += 1

    added_count = 0
    for norm_name, team_id in teams_map.items():
        if norm_name not in existing_names:
            new_row = {"id": team_id, "nome": norm_name.title()}
            for col in fieldnames:
                if col not in new_row:
                    new_row[col] = ""
            rows.append(new_row)
            added_count += 1
            existing_names[norm_name] = True

    # Criar backup antes de salvar
    create_backup(CSV_PATH)

    with open(CSV_PATH, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delim)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Sincronização finalizada. IDs atualizados: {synced_count}, Adicionados: {added_count}")

def main():
    teams_map = fetch_all_teams()
    if teams_map:
        sync_csv(teams_map)

if __name__ == "__main__":
    main()
