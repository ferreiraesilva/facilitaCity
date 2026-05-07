import csv
import requests
import sys
import time
from pathlib import Path

# Garantir que o diretório raiz está no path para importar utils
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from utils.helpers import detect_delimiter, get_api_config

def main():
    # Carregar config centralizada
    base_url_v1, headers, cookies = get_api_config()
    
    # Derivar URL v2 para o endpoint de status em massa
    # De: https://city.api.facilitavendas.com/api/v1
    # Para: https://city.api.facilitavendas.com/api/v2/users/statuses
    base_url_v2 = base_url_v1.replace("/api/v1", "/api/v2")
    BULK_STATUS_URL = f"{base_url_v2}/users/statuses"
    
    csv_path = Path("csv/gerentes.csv")
    if not csv_path.exists():
        print(f"[ERRO] Arquivo {csv_path} não encontrado.")
        return

    print("\n" + "="*40)
    print("   BLOQUEIO/LIBERAÇÃO EM MASSA (V2)")
    print("="*40)
    print(" [1] ATIVAR todos os gerentes da lista")
    print(" [2] INATIVAR todos os gerentes da lista")
    print(" [0] Cancelar")
    print("="*40)
    
    escolha = input("Escolha uma opção: ").strip()
    if escolha not in ["1", "2"]:
        return

    target_status = "active" if escolha == "1" else "inactive"
    action_label = "ATIVAR" if escolha == "1" else "INATIVAR"

    # Ler IDs do CSV
    delim = detect_delimiter(csv_path)
    user_ids = []
    with open(csv_path, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        for row in reader:
            uid = row.get("Id", "").strip()
            if uid and uid != "0":
                user_ids.append(int(uid))

    if not user_ids:
        print("[AVISO] Nenhum ID encontrado no CSV.")
        return

    print(f">>> {action_label} {len(user_ids)} gerentes...")
    
    # Preparar payload
    payload = {
        "users": user_ids,
        "status": target_status
    }
    
    # Headers adicionais necessários para o v2 conforme o curl
    headers["content-type"] = "application/json"
    
    try:
        print(f"Enviando requisição para {BULK_STATUS_URL}...")
        resp = requests.post(BULK_STATUS_URL, headers=headers, cookies=cookies, json=payload, timeout=30)
        
        if resp.status_code in [200, 201]:
            print(f"\n[OK] SUCESSO! Todos os {len(user_ids)} gerentes foram processados.")
            print(f"Resposta: {resp.text[:200]}")
        else:
            print(f"\n[ERRO] Código {resp.status_code}")
            print(f"Detalhes: {resp.text[:500]}")
            if resp.status_code == 401:
                print("\n[DICA] O token de autorização pode ter expirado ou não ser válido para a API v2.")
                print("Verifique se o CITY_AUTHORIZATION no seu arquivo .env está atualizado.")
    except Exception as e:
        print(f"\n[EXCEÇÃO] {str(e)}")

if __name__ == "__main__":
    main()
