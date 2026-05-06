import csv
import requests
import time
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Garantir que o diretório raiz está no path para importar utils
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from utils.helpers import detect_delimiter, load_env, get_api_config

# Carregar config centralizada
BASE_URL, HEADERS_CITY, COOKIES = get_api_config()
CSV_PATH = Path("csv/supervisores.csv")

# Configuração de Paralelismo
MAX_WORKERS = 10 

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
        if response.status_code == 200:
            items = response.json()
            if isinstance(items, list):
                for item in items:
                    teams.append({"id": item.get("id"), "name": item.get("name")})
    except Exception:
        pass
    return teams

def fetch_team_supervisors(team):
    """Função que será executada em paralelo para cada equipe."""
    team_id = team["id"]
    team_name = team["name"]
    
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
    team_rows = []
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            supervisors = response.json()
            if isinstance(supervisors, list):
                for sup in supervisors:
                    team_rows.append({
                        "id_sup": str(sup.get("id")),
                        "nome_sup": sup.get("first_name"),
                        "email_sup": sup.get("email", ""),
                        "id_imob": str(team_id),
                        "nome_imob": team_name
                    })
    except Exception:
        pass
    return team_rows

def save_csv(rows):
    fieldnames = ["id_sup", "nome_sup", "email_sup", "id_imob", "nome_imob"]
    with open(CSV_PATH, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

def main():
    teams = fetch_all_teams()
    if not teams: return

    print(f">>> Consultando supervisores em paralelo ({MAX_WORKERS} conexões)...", flush=True)
    all_rows = []
    total = len(teams)
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_team_supervisors, team): team for team in teams}
        
        completed = 0
        for future in as_completed(futures):
            completed += 1
            result = future.result()
            if result:
                all_rows.extend(result)
            
            if completed % 10 == 0 or completed == total:
                print(f"  Progresso: {completed}/{total} equipes processadas...", end="\r", flush=True)
    
    # Ordenar por id_sup (convertendo para int para ordem numérica correta)
    print("\n>>> Ordenando resultados por ID...", flush=True)
    all_rows.sort(key=lambda x: int(x["id_sup"]) if x["id_sup"].isdigit() else 0)
        
    print(f">>> Processamento concluído. Total de {len(all_rows)} vínculos encontrados.")
    save_csv(all_rows)
    print(f">>> Dados salvos e ordenados em {CSV_PATH}")

if __name__ == "__main__":
    main()
