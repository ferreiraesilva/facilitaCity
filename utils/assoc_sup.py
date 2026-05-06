import csv
import requests
import time
from pathlib import Path

# Configurações
BASE_URL = "https://city.api.facilitavendas.com/api/v1/users"
SUP_CSV = Path(".venv/Scripts/sup.csv")
IMOB_CSV = Path(".venv/Scripts/imob.csv")

HEADERS = {
    "accept": "application/json, text/plain, */*",
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

def load_supervisors():
    sups = []
    with open(SUP_CSV, mode="r", encoding="utf-8") as f:
        # Nota: O arquivo usa ';' como delimitador
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if len(row) >= 3:
                sups.append({
                    "name": row[0],
                    "email": row[1],
                    "id": row[2]
                })
    return sups

def load_team_mappings():
    mappings = {} # Gerente -> [team_ids]
    with open(IMOB_CSV, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            gerente = row["GerenteCV"]
            team_id = row["team_id"]
            if gerente and team_id:
                if gerente not in mappings:
                    mappings[gerente] = []
                mappings[gerente].append(team_id)
    return mappings

def associate_supervisor(sup, team_ids):
    user_id = sup["id"]
    email = sup["email"]
    url = f"{BASE_URL}/{user_id}"
    
    # Montando o payload multipart/form-data
    # Usaremos o parâmetro 'files' do requests para simular o comportamento do curl se necessário,
    # mas campos de formulário simples são passados em 'data'.
    # Como o curl usa multipart, passaremos uma estrutura que o requests converte para tal.
    
    payload = {
        "user_group": (None, "supervisor"),
        "email": (None, email),
    }
    
    for i, tid in enumerate(team_ids):
        payload[f"changeTeamOrManager[{i}]"] = (None, str(tid))
    
    print(f"Associando {sup['name']} (ID {user_id}) a {len(team_ids)} equipes...")
    
    response = requests.post(url, headers=HEADERS, cookies=COOKIES, files=payload)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("status") == "success":
            print(f"  [OK] Usuário atualizado com sucesso!")
        else:
            print(f"  [ERRO] API retornou erro: {result.get('msg')}")
    else:
        print(f"  [ERRO] Falha na requisição (Status {response.status_code}): {response.text}")

def main():
    sups = load_supervisors()
    mappings = load_team_mappings()
    
    for sup in sups:
        name = sup["name"]
        if name in mappings:
            team_ids = mappings[name]
            associate_supervisor(sup, team_ids)
            time.sleep(0.5) # Pausa amigável entre chamadas
        else:
            print(f"Aviso: Nenhuma equipe encontrada em imob.csv para o gerente '{name}'")

if __name__ == "__main__":
    main()
