import csv
import requests
import time
import sys
import json
from pathlib import Path

# Garantir que o diretório raiz está no path para importar utils
root_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_path))

from utils.helpers import detect_delimiter, get_api_config

# Carregar config centralizada
BASE_URL, HEADERS, COOKIES = get_api_config()
URL = f"{BASE_URL}/teams/"

MAX_RETRIES = 3
RETRY_DELAY = 10

def create_team(name: str, cnpj: str = "") -> dict:
    """Cria uma equipe (imobiliária) no Facilita."""
    payload = {
        "name": (None, name),
        "cnpj": (None, cnpj),
    }
    response = requests.post(URL, headers=HEADERS, cookies=COOKIES, files=payload)
    return {"status": response.status_code, "body": response.text}

def create_team_with_retry(name: str) -> dict:
    """Tenta criar a equipe com até MAX_RETRIES tentativas."""
    for attempt in range(1, MAX_RETRIES + 1):
        result = create_team(name)
        if result["status"] in (200, 201):
            return result

        print(f"ERRO (tentativa {attempt}/{MAX_RETRIES}) - Status {result['status']}: {result['body']}")

        if attempt < MAX_RETRIES:
            print(f"  Aguardando {RETRY_DELAY}s antes de tentar novamente...")
            time.sleep(RETRY_DELAY)

    return result

def main():
    csv_path = Path("csv/imobiliarias.csv")

    print("=== IMPORTACAO EM LOTE DE EQUIPES ===")
    success = 0
    errors = 0
    skipped = 0

    delim = detect_delimiter(csv_path)
    print(f"Delimitador detectado: '{delim}'")

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        fieldnames = list(reader.fieldnames)
        rows = [dict(row) for row in reader]

    total = len(rows)
    print(f"Total de imobiliarias para processar: {total}\n")

    for i, row in enumerate(rows, 1):
        name = row.get("nome", "").strip()
        existing_id = row.get("id", "").strip()

        if existing_id:
            print(f"[{i}/{total}] Pulando: {name} (Já possui ID: {existing_id})")
            skipped += 1
            continue

        if not name:
            continue

        print(f"[{i}/{total}] Cadastrando: {name} ... ", end="", flush=True)

        result = create_team_with_retry(name)

        if result["status"] in (200, 201):
            try:
                body = json.loads(result["body"])
                new_id = body.get("data", {}).get("id") or body.get("id")
                if new_id:
                    row["id"] = str(new_id)
                    print(f"OK ({result['status']}) - ID: {new_id}")
                else:
                    print(f"OK ({result['status']}) - ID não retornado")
            except:
                print(f"OK ({result['status']}) - Resposta não é JSON")
            
            success += 1
            
            # Salva o CSV atualizado
            with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delim)
                writer.writeheader()
                writer.writerows(rows)
        else:
            print(f"FALHA DEFINITIVA apos {MAX_RETRIES} tentativas!")
            errors += 1
            print(f"\n!!! PROGRAMA INTERROMPIDO - Verifique as credenciais no .env !!!")
            print(f"Ultima imobiliaria tentada: {name}")
            sys.exit(1)

        time.sleep(0.3)

    print(f"\n=== RESULTADO FINAL ===")
    print(f"Sucesso: {success}")
    print(f"Pulados: {skipped}")
    print(f"Erros:   {errors}")
    print(f"Total:   {total}")

if __name__ == "__main__":
    main()
