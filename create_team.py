import csv
import requests
import time
import sys
import json


URL = "https://city.api.facilitavendas.com/api/v1/teams/"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXUyJ9.eyJhdWQiOiJodHRwczpcL1wvY2l0eS5mYWNpbGl0YXZlbmRhcy5jb20iLCJnb3Njb3JlLXRva2VuLXVzZXIiOiJleUpwZGlJNkluQjBUMEZ6T0ZoalJVOTZUSGhuUWpod01HYzJhMEU5UFNJc0luWmhiSFZsSWpvaVFVMHhWekpoWEM5c01rbHJUMGhSY210RVRVUlFVMlZJT0ZCMVZHUnNValF4UTF3dk0yUjVVamhWVTBGdU1XcFVUMmh3V1drMWRXTkxkRU5yWkdOMWMyVTBWRWhoVlVkeU1sRlNPV3R5YUhWcE1tOVpPVnBNWnowOUlpd2liV0ZqSWpvaU9XSTNPRGcwTTJNeE4yUTNPR0UwTldabVlqUXhOV1l6WWprNE1qUTJOVGM0WW1NNFpEQmlaVGt5T0dReE9ETTNNVGxoTlRFeU4yVmhNalV6TjJVMFlpSjkiLCJzdWIiOjUxNywiaXNzIjoiaHR0cHM6XC9cL2NpdHkuYXBpLmZhY2lsaXRhdmVuZGFzLmNvbVwvYXBpXC92MVwvYXV0aGVudGljYXRlIiwiaWF0IjoiMTc3NjIwMTIyNiIsImV4cCI6IjE3ODEzODUyMjYiLCJuYmYiOiIxNzc2MjAxMjI2IiwianRpIjoiMWY5NjdjNzcxMmQ1NjdiNjBjOGVkMGYyNGYzM2JiZDUifQ.MzJmMTdiMWJmZDAzYzU2YTVkMjgwNGQwMzhiZTE0MDc2ZTFhMjljZjY4Nzk3NjQ2ZDg0Yzk1MTEyN2JjMGQwNA",
    "goscore-token": "518c2b22e9372a2e8bd0cda98b14e21d",
    "origin": "https://city.facilitavendas.com",
    "referer": "https://city.facilitavendas.com/",
    "sec-ch-ua": '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
}

COOKIES = {
    "_ga": "GA1.1.1582189440.1776201035",
    "_clck": "is2ztc%5E2%5Eg57%5E0%5E2295",
    "_ga_4Y48ZYP9EX": "GS2.1.s1776201034$o1$g1$t1776201219$j60$l0$h0",
    "PHPSESSID": "fa5efebcb74sham4sbhvcnjbd6",
    "refresh_token": "f7cb854840aa834debb6d15c5b023a32",
    "cartalyst_sentry": "eyJpdiI6Im1WeUNQbVRYTFJ0T0UzaERoMlh2S1E9PSIsInZhbHVlIjoia3h0T0czMk5KdTJZbUtIUExUQkF3TFlXbG5SbEpqcHg3c0MwOWF3RWZcL3g0dTNPRXVUQW5tcHBlQ1laSmMrM0lqN2Q1dU9cL2VLMHFUbFltNHdpVVJ3NWZUaDhBSEYyc2gxN2ZoYWJsUUN0ZUVzWU9Bd2dGTG16QW4zeVpobkkzUCIsIm1hYyI6ImFkNDI3M2MyOTU1NmRlMzc0ZWNhNmNlMDBiMjNjMjBjOWU1ZWZkNDMxM2RkN2ZlNWE2ODUyNGZjOGMyMjQ2YTEifQ==",
    "_clsk": "1c3qi82%5E1776201246905%5E6%5E1%5Ea.clarity.ms%2Fcollect",
    "_ga_P4WF2YCTNX": "GS2.1.s1776201034$o1$g1$t1776201247$j32$l0$h0",
    "laravel_session": "eyJpdiI6IjIrSzMrdnFjQUYwc0xVUzBwRGNVZ3c9PSIsInZhbHVlIjoibXhaV2JPM0poQVRNYUhpRzYwa3lvU2x0dDJuQXlaVGRFcmhBVEVyUGtNVW5wVWJ0bjZhRE8rRnIzcmo0UmpjdENTZkk3WEVMWGphSVNpZW8yVmw1ZWc9PSIsIm1hYyI6Ijc0ODMxZGE3YjViZTBhNzk5Y2EyMzlhNmIxNjA0MGM3MzgyNGU4ODExZjk5OGQyZTBkMDI2MjE4NDdjYTlhMzkifQ==",
}

MAX_RETRIES = 3
RETRY_DELAY = 10


def detect_delimiter(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            header = f.readline()
            if header.count(';') > header.count(','):
                return ';'
            return ','
    except Exception:
        return ';' # Fallback


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

    return result  # retorna o último resultado com erro


def main():
    csv_path = "csv/imob.csv"

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
            print(f"\n!!! PROGRAMA INTERROMPIDO - Possivel necessidade de novo token !!!")
            print(f"Ultima imobiliaria tentada: {name}")
            print(f"Cadastradas com sucesso ate aqui: {success}")
            print(f"Restantes: {total - i}")
            sys.exit(1)

        # Pequena pausa para nao sobrecarregar a API
        time.sleep(0.3)

    print(f"\n=== RESULTADO FINAL ===")
    print(f"Sucesso: {success}")
    print(f"Pulados: {skipped}")
    print(f"Erros:   {errors}")
    print(f"Total:   {total}")



if __name__ == "__main__":
    main()
