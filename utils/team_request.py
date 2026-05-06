import argparse
import csv
import json
from pathlib import Path
from typing import Any

try:
    import requests
except ModuleNotFoundError:
    requests = None


DEFAULT_URL = "https://city.api.facilitavendas.com/api/v1/teams/"
DEFAULT_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXUyJ9."
    "eyJhdWQiOiJodHRwczpcL1wvY2l0eS5mYWNpbGl0YXZlbmRhcy5jb20iLCJnb3Njb3JlLXRva2Vu"
    "LXVzZXIiOiJleUpwZGlJNklsYzNaMlZHUTBveGRIQjVXWGhrWlVwdVVWbDFkVUU5UFNJc0luWmhi"
    "SFZsSWpvaWFIUllPR2hPWWt4Uk1HNTJVbkE1ZWpjMFoyOVFUMWhQYXpOSVEyeGxhbFZZYzNGUWFY"
    "enhUWEpvVGxGblpubExWMVZFWVU1c2RWSnljR1JMY2pWNmFsRTNlR2c0YTFWTWVVSlZUVFpFY0ZS"
    "RVhDOVVVbUZSUFQwaUxDSnRZV01pT2lJNVlXTTBZalE0TldSaU16bGtNamN5TTJVeE9XTXdPRFl3"
    "WmpnM1lqRTBaR015TVRJMVlUUmlOalppTVRJd05UYzVZVGt5Wm1ZMlkyUmhaREk1T1RReUluMD0i"
    "LCJzdWIiOjUxNywiaXNzIjoiaHR0cHM6XC9cL2NpdHkuYXBpLmZhY2lsaXRhdmVuZGFzLmNvbVwv"
    "YXBpXC92MVwvYXV0aGVudGljYXRlIiwiaWF0IjoiMTc3NjE5ODY0NiIsImV4cCI6IjE3ODEzODI2"
    "NDYiLCJuYmYiOiIxNzc2MTk4NjQ2IiwianRpIjoiZjBiZTMzNDg0MjkwNmRkYmYxNjUwODI1Mjlj"
    "YjVhOTIifQ.YmI4NDA2YWVjODk1ODAwMTNmNzg4NDQ5OWZhZjNmYWI4ZDM1NjU5ZTU3NDI3NmI1"
    "MmY0NWMwZmU3N2EzY2I1MA"
)
DEFAULT_GOSCORE_TOKEN = "518c2b22e9372a2e8bd0cda98b14e21d"
DEFAULT_NAME = "TESTE01"
DEFAULT_CNPJ = ""
DEFAULT_CSV_PATH = ".venv/Scripts/imob.csv"
DEFAULT_NAME_COLUMN = "Imobiliaria"
DEFAULT_ID_COLUMN = "team_id"
DEFAULT_ENCODING = "utf-8-sig"


def build_headers(token: str, goscore_token: str) -> dict[str, str]:
    return {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token}",
        "goscore-token": goscore_token,
    }


def create_team(
    url: str,
    token: str,
    goscore_token: str,
    name: str,
    cnpj: str = "",
    timeout: int = 30,
) -> Any:
    if requests is None:
        raise ModuleNotFoundError(
            "A biblioteca 'requests' não está instalada. Instale com: pip install requests"
        )

    headers = build_headers(token=token, goscore_token=goscore_token)
    data = {
        "name": name,
        "cnpj": cnpj,
    }
    return requests.post(url, headers=headers, files={}, data=data, timeout=timeout)


def print_response(response: Any) -> None:
    print(f"Status: {response.status_code}")
    print("Headers:")
    print(json.dumps(dict(response.headers), indent=2, ensure_ascii=False))
    print("Body:")

    try:
        body: Any = response.json()
        print(json.dumps(body, indent=2, ensure_ascii=False))
    except ValueError:
        print(response.text)


def read_csv_rows(csv_path: Path, encoding: str) -> tuple[list[dict[str, str]], list[str]]:
    with csv_path.open(mode="r", encoding=encoding, newline="") as file:
        reader = csv.DictReader(file)
        rows = [dict(row) for row in reader]
        fieldnames = list(reader.fieldnames or [])
    return rows, fieldnames


def write_csv_rows(
    csv_path: Path,
    rows: list[dict[str, str]],
    fieldnames: list[str],
    encoding: str,
) -> None:
    with csv_path.open(mode="w", encoding=encoding, newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def process_csv(
    csv_path: Path,
    encoding: str,
    name_column: str,
    id_column: str,
    url: str,
    token: str,
    goscore_token: str,
    cnpj: str,
    timeout: int,
) -> None:
    rows, fieldnames = read_csv_rows(csv_path=csv_path, encoding=encoding)

    if name_column not in fieldnames:
        available = ", ".join(fieldnames) or "nenhuma"
        raise ValueError(
            f"Coluna '{name_column}' não encontrada no CSV. Colunas disponíveis: {available}"
        )

    if id_column not in fieldnames:
        fieldnames.append(id_column)
        for row in rows:
            row.setdefault(id_column, "")

    created_count = 0
    skipped_count = 0

    for index, row in enumerate(rows, start=2):
        existing_id = (row.get(id_column) or "").strip()
        name = (row.get(name_column) or "").strip()

        if existing_id:
            skipped_count += 1
            print(f"Linha {index}: ignorada, {id_column} já preenchido com {existing_id}.")
            continue

        if not name:
            skipped_count += 1
            print(f"Linha {index}: ignorada, coluna '{name_column}' vazia.")
            continue

        response = create_team(
            url=url,
            token=token,
            goscore_token=goscore_token,
            name=name,
            cnpj=cnpj,
            timeout=timeout,
        )

        try:
            payload: dict[str, Any] = response.json()
        except ValueError:
            print(
                f"Linha {index}: erro ao criar '{name}'. "
                f"Status {response.status_code}. Resposta não é JSON."
            )
            continue

        if response.ok and payload.get("status") == "success":
            team_id = payload.get("data", {}).get("id")
            if team_id:
                row[id_column] = str(team_id)
                created_count += 1
                print(f"Linha {index}: '{name}' criado com sucesso. ID {team_id}.")
                write_csv_rows(
                    csv_path=csv_path,
                    rows=rows,
                    fieldnames=fieldnames,
                    encoding=encoding,
                )
            else:
                print(
                    f"Linha {index}: '{name}' criado, mas a resposta não trouxe um ID."
                )
        else:
            message = payload.get("msg") or response.text
            print(
                f"Linha {index}: erro ao criar '{name}'. "
                f"Status {response.status_code}. Mensagem: {message}"
            )

    print(
        f"Processamento concluído. Criados: {created_count}. Ignorados: {skipped_count}."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa a criação de teams na API Facilita por linha de comando ou CSV."
    )
    parser.add_argument(
        "--token",
        default=DEFAULT_TOKEN,
        help="Bearer token da API",
    )
    parser.add_argument(
        "--goscore-token",
        default=DEFAULT_GOSCORE_TOKEN,
        help="Valor do header goscore-token",
    )
    parser.add_argument("--name", default=DEFAULT_NAME, help="Nome do time")
    parser.add_argument("--cnpj", default=DEFAULT_CNPJ, help="CNPJ do time")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL da API")
    parser.add_argument(
        "--timeout", type=int, default=30, help="Timeout da requisição em segundos"
    )
    parser.add_argument(
        "--csv-path",
        default=DEFAULT_CSV_PATH,
        help="Caminho do CSV para processamento em lote",
    )
    parser.add_argument(
        "--encoding",
        default=DEFAULT_ENCODING,
        help="Encoding usado para ler e gravar o CSV",
    )
    parser.add_argument(
        "--name-column",
        default=DEFAULT_NAME_COLUMN,
        help="Nome da coluna do CSV que contém o nome a ser criado",
    )
    parser.add_argument(
        "--id-column",
        default=DEFAULT_ID_COLUMN,
        help="Nome da coluna do CSV onde o ID retornado será salvo",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="Processa o CSV em lote em vez de fazer apenas uma requisição",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.csv:
        process_csv(
            csv_path=Path(args.csv_path),
            encoding=args.encoding,
            name_column=args.name_column,
            id_column=args.id_column,
            url=args.url,
            token=args.token,
            goscore_token=args.goscore_token,
            cnpj=args.cnpj,
            timeout=args.timeout,
        )
        return

    response = create_team(
        url=args.url,
        token=args.token,
        goscore_token=args.goscore_token,
        name=args.name,
        cnpj=args.cnpj,
        timeout=args.timeout,
    )
    print_response(response)


if __name__ == "__main__":
    main()
