import csv
from pathlib import Path

def normalize(s):
    return s.strip() if s else ""

def main():
    troca_path = Path("csv/corretores_troca_time.csv")
    gerentes_path = Path("csv/gerentes.csv")
    
    if not troca_path.exists() or not gerentes_path.exists():
        print("Erro: Arquivos não encontrados.")
        return

    # 1. Carregar gerentes e agrupar por idImobiliaria
    # Usamos idImobiliaria como chave primária
    managers_by_imob = {}
    with open(gerentes_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            imob_id = normalize(row.get("idImobiliaria"))
            if not imob_id:
                continue
            if imob_id not in managers_by_imob:
                managers_by_imob[imob_id] = []
            managers_by_imob[imob_id].append(row)

    # 2. Selecionar o melhor gerente para cada imobiliária
    selected_manager = {}
    for imob_id, managers in managers_by_imob.items():
        # Filtra os que NÃO começam com "Gerente -"
        # Usamos .strip() para garantir que espaços não atrapalhem a comparação
        real_managers = [m for m in managers if not normalize(m["Nome"]).startswith("Gerente -")]
        
        if real_managers:
            # Pega o primeiro gerente real
            selected_manager[imob_id] = real_managers[0]
        else:
            # Fallback para o gerente automático se for o único
            selected_manager[imob_id] = managers[0]

    # 3. Ler o arquivo de troca e atualizar
    rows = []
    fieldnames = []
    delim = ";"
    
    with open(troca_path, mode="r", encoding="utf-8-sig") as f:
        # Detectar delimitador
        sample = f.read(1024)
        f.seek(0)
        delim = ";" if sample.count(";") > sample.count(",") else ","
        
        reader = csv.DictReader(f, delimiter=delim)
        fieldnames = list(reader.fieldnames)
        
        # Garantir colunas novas
        if "id_gerente" not in fieldnames:
            fieldnames.append("id_gerente")
        if "nome_gerente" not in fieldnames:
            fieldnames.append("nome_gerente")
            
        for row in reader:
            imob_id = normalize(row.get("idImobiliaria"))
            mgr = selected_manager.get(imob_id)
            
            if mgr:
                row["id_gerente"] = mgr["Id"]
                row["nome_gerente"] = mgr["Nome"]
            else:
                row["id_gerente"] = ""
                row["nome_gerente"] = ""
            rows.append(row)

    # 4. Salvar o arquivo atualizado
    # Usando o mesmo delimitador detectado
    with open(troca_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delim)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Sucesso! Arquivo {troca_path.name} atualizado com as colunas id_gerente e nome_gerente.")

if __name__ == "__main__":
    main()
