import os
import subprocess
import time

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    while True:
        clear()
        print("="*60)
        print("             SISTEMA DE INTEGRAÇÃO FACILITA")
        print("="*60)
        print(" [1] Criar Equipes/Imobiliárias (create_team.py) (imob.csv)")
        print(" [2] Criar Gerentes (create_managers.py) (gerentes.csv)")
        print(" [3] Criar e Vincular Supervisores (assoc_sup_imob.py) (sup_imob.csv)")
        print(" [4] Sincronizar IDs das Imobiliárias (sync_teams.py) (imob.csv)")
        print(" [0] Sair")
        print("="*60)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            print("\n>>> Executando create_team.py...\n")
            subprocess.run(["python", "create_team.py"])
            input("\nProcesso finalizado. Pressione Enter para voltar ao menu...")
        elif opcao == "2":
            print("\n>>> Executando create_managers.py...\n")
            subprocess.run(["python", "create_managers.py"])
            input("\nProcesso finalizado. Pressione Enter para voltar ao menu...")
        elif opcao == "3":
            print("\n>>> Executando assoc_sup_imob.py...\n")
            subprocess.run(["python", "assoc_sup_imob.py"])
            input("\nProcesso finalizado. Pressione Enter para voltar ao menu...")
        elif opcao == "4":
            print("\n>>> Executando sync_teams.py...\n")
            subprocess.run(["python", "utils/sync_teams.py"])
            input("\nProcesso finalizado. Pressione Enter para voltar ao menu...")
        elif opcao == "0":
            print("\nSaindo do sistema. Até logo!")
            break
        else:
            print("\n[ERRO] Opção inválida! Tente novamente.")
            time.sleep(1.5)

if __name__ == "__main__":
    main()
