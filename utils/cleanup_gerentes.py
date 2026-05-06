import csv
import os

CSV_PATH = "csv/imob_gerentes.csv"
TEMP_PATH = "csv/imob_gerentes_clean.csv"

def cleanup():
    print(f"Iniciando limpeza de: {CSV_PATH}")
    
    rows = []
    fieldnames = []
    
    # Lendo o arquivo original
    # Usamos utf-8-sig para lidar com o BOM se houver
    with open(CSV_PATH, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=';')
        fieldnames = list(reader.fieldnames)
        
        # Corrigindo erro de digitação no cabeçalho se existir
        if "ImoAbiliaria" in fieldnames:
            print("  [INFO] Corrigindo cabeçalho 'ImoAbiliaria' -> 'Imobiliaria'")
            fieldnames = ["Imobiliaria" if f == "ImoAbiliaria" else f for f in fieldnames]
        
        for row in reader:
            # Se mudamos a chave no fieldnames, precisamos mudar no dicionário da linha também
            if "ImoAbiliaria" in row:
                row["Imobiliaria"] = row.pop("ImoAbiliaria")
                
            gerente = row.get("GerenteCV", "")
            
            # Substituição 1: Nome completo da Caroline
            if gerente.strip() == "Caroline Neri":
                row["GerenteCV"] = "Caroline Alves Neri Batista"
            
            # Substituição 2: Branco -> DIRETORIA
            elif not gerente.strip():
                row["GerenteCV"] = "DIRETORIA"
            
            rows.append(row)

    # Gravando o arquivo limpo
    with open(TEMP_PATH, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)

    # Substituindo o original pelo limpo
    os.replace(TEMP_PATH, CSV_PATH)
    print(f"Limpeza concluída com sucesso. {len(rows)} linhas processadas.")

if __name__ == "__main__":
    cleanup()
