import subprocess
import time
from utils.helpers import clear

# Dicionário central: categoria -> lista de (label, caminho do script)
MENUS = {
    "IMOBILIÁRIAS (Equipes)": [
        ("Sincronizar IDs das Imobiliárias",   "actions/imob/sync_teams.py"),
        ("Criar Equipes/Imobiliárias",         "actions/imob/create_team.py"),        
    ],
    "SUPERVISORES": [
        ("Sincronizar Supervisores da API",     "actions/supervisors/sync_sup_imob.py"),
        ("Criar e Vincular Supervisores",       "actions/supervisors/assoc_sup_imob.py"),
        ("Ativar/Inativar TODOS da lista",      "actions/supervisors/toggle_supervisors_status.py"),
        ("Ativar/Inativar ALGUNS via CSV",      "actions/supervisors/update_supervisors_status.py"),
    ],
    "GERENTES": [
        ("Sincronizar Gerentes da API",         "actions/managers/sync_managers_to_csv.py"),
        ("Criar Gerentes em Massa",             "actions/managers/create_managers.py"),
        ("Ativar/Inativar TODOS da lista",      "actions/managers/toggle_managers_status.py"),
        ("Ativar/Inativar ALGUNS via CSV",      "actions/managers/update_managers_status.py"),
        ("BLOQUEIO/LIBERAÇÃO EM MASSA (V2)",    "actions/managers/bulk_status_managers.py"),
    ],
    "CORRETORES": [
        ("Sincronizar Corretores da API",       "actions/brokers/sync_brokers_to_csv.py"),
        ("Criar Corretores em Massa",           "actions/brokers/create_brokers.py"),
        ("Ativar/Inativar TODOS da lista",      "actions/brokers/toggle_brokers_status.py"),
        ("Ativar/Inativar ALGUNS via CSV",      "actions/brokers/update_brokers_status.py"),
        ("BLOQUEIO/LIBERAÇÃO EM MASSA (V2)",    "actions/brokers/bulk_status_brokers.py"),
    ],
}

def run_menu(title, options):
    """Menu genérico: exibe opções e executa o script escolhido."""
    while True:
        clear()
        print("=" * 60)
        print(f"             {title}")
        print("=" * 60)
        for i, (label, _) in enumerate(options, 1):
            print(f" [{i}] {label}")
        print(" [0] Voltar")
        print("=" * 60)

        opcao = input("Escolha uma opção: ").strip()
        if opcao == "0":
            break
        if opcao.isdigit() and 1 <= int(opcao) <= len(options):
            _, script = options[int(opcao) - 1]
            print(f"\n>>> Executando {script}...\n")
            subprocess.run(["python", script])
            input("\nProcesso finalizado. Pressione Enter para voltar...")

def main():
    categorias = list(MENUS.keys())
    while True:
        clear()
        print("=" * 60)
        print("             SISTEMA DE INTEGRAÇÃO FACILITA")
        print("=" * 60)
        for i, cat in enumerate(categorias, 1):
            print(f" [{i}] {cat}")
        print(" [0] Sair")
        print("=" * 60)

        opcao = input("Escolha uma categoria: ").strip()
        if opcao == "0":
            print("\nSaindo do sistema. Até logo!")
            break
        if opcao.isdigit() and 1 <= int(opcao) <= len(categorias):
            cat = categorias[int(opcao) - 1]
            run_menu(cat, MENUS[cat])
        else:
            print("\n[ERRO] Opção inválida!")
            time.sleep(1.5)

if __name__ == "__main__":
    main()
