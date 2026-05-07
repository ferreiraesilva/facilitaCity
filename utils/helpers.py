import os
from pathlib import Path

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def detect_delimiter(file_path):
    """Detecta se o CSV usa ';' ou ',' como delimitador."""
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            header = f.readline()
            if header.count(';') > header.count(','):
                return ';'
            return ','
    except Exception:
        return ';'

def load_env():
    """Carrega as variáveis do arquivo .env manualmente."""
    env = {}
    # Procura o .env na raiz do projeto
    # Se estiver sendo chamado de actions/subfolder/script.py, root_path é 2 níveis acima
    # Mas como o helpers.py está em utils/, podemos basear nele
    root_path = Path(__file__).resolve().parent.parent
    env_path = root_path / ".env"
    
    if env_path.exists():
        with env_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env

import shutil
from datetime import datetime

def create_backup(file_path):
    """Cria uma cópia de segurança do arquivo em csv/backup/."""
    file_path = Path(file_path)
    if not file_path.exists():
        return
        
    backup_dir = file_path.parent / "backup"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
    backup_path = backup_dir / backup_name
    
    shutil.copy2(file_path, backup_path)
    print(f">>> Backup criado: {backup_path}")

def get_api_config():
    """Retorna headers e cookies configurados no .env."""
    env = load_env()
    
    base_url = env.get("CITY_API_URL", "https://city.api.facilitavendas.com/api/v1")
    auth = env.get("CITY_AUTHORIZATION", "")
    goscore = env.get("CITY_GOSCORE_TOKEN", "518c2b22e9372a2e8bd0cda98b14e21d")
    
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "authorization": auth,
        "goscore-token": goscore,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "origin": "https://city.facilitavendas.com",
        "referer": "https://city.facilitavendas.com/",
    }
    
    cookies = {}
    if env.get("CITY_PHPSESSID"):
        cookies["PHPSESSID"] = env.get("CITY_PHPSESSID")
    if env.get("CITY_REFRESH_TOKEN"):
        cookies["refresh_token"] = env.get("CITY_REFRESH_TOKEN")
    if env.get("CITY_CARTALYST_SENTRY"):
        cookies["cartalyst_sentry"] = env.get("CITY_CARTALYST_SENTRY")
    if env.get("CITY_LARAVEL_SESSION"):
        cookies["laravel_session"] = env.get("CITY_LARAVEL_SESSION")
        
    return base_url, headers, cookies
