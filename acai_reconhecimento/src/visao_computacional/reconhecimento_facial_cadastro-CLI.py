import sqlite3
import json
import urllib.request
import pwinput
import os

DB_NAME = 'acai_sistema.db'
CONFIG_FILE = 'config_acaiteria.json'

def inicializar_banco():
    """Cria a tabela no SQLite caso ela não exista."""
    conexao = sqlite3.connect(DB_NAME)
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            apelido TEXT,
            email TEXT,
            telefone TEXT,
            endereco TEXT,
            idade TEXT,
            acai_preferido TEXT NOT NULL
        )
    ''')
    conexao.commit()
    conexao.close()

def verificar_configuracoes_sistema():
    """Usa JSON, OS e URLLIB para checar configurações e rede."""
    print("[CLI] Verificando configurações do sistema...")
    if not os.path.exists(CONFIG_FILE):
        config_padrao = {
            "nome_loja": "Açaíteria Delírio Roxo",
            "clube_fidelidade": "Cupom de 10% ativo",
            "status_sistema": "Online"
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_padrao, f, ensure_ascii=False, indent=4)
        print(f"[JSON] Arquivo '{CONFIG_FILE}' gerado com sucesso.")
    
    try:
        urllib.request.urlopen("https://www.google.com", timeout=2)
        print("[URLLIB] Conexão com a rede estabelecida.")
    except Exception:
        print("[URLLIB] Modo offline ativado.")

def painel_administrativo_real():
    """Painel CLI para gerenciamento e cadastro manual real."""
    inicializar_banco()
    verificar_configuracoes_sistema()
    
    print("\n========================================")
    print(" PAINEL ADMINISTRATIVO - DELÍRIO ROXO (CLI)")
    print("========================================")
    
    senha = pwinput.pwinput(prompt="Digite a senha de Administrador (padrão: admin123): ", mask="*")
    
    if senha == "admin123":
        print("\n[ACESSO PERMITIDO] Bem-vindo ao painel de controle.")
        while True:
            print("\n1. Cadastrar novo cliente manualmente")
            print("2. Listar clientes cadastrados")
            print("3. Sair")
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                nome = input("Nome completo: ").strip()
                email = input("E-mail: ").strip()
                telefone = input("Telefone: ").strip()
                acai = input("Açaí preferido (com adicionais): ").strip()
                
                if not nome or not acai:
                    print("[ERRO] Nome e Açaí preferido são obrigatórios!")
                    continue
                
                conexao = sqlite3.connect(DB_NAME)
                cursor = conexao.cursor()
                cursor.execute('''
                    INSERT INTO clientes (nome, email, telefone, acai_preferido) 
                    VALUES (?, ?, ?, ?)
                ''', (nome, email, telefone, acai))
                conexao.commit()
                conexao.close()
                print(f"[SUCESSO] Cliente '{nome}' cadastrado com dados reais!")
                
            elif opcao == "2":
                conexao = sqlite3.connect(DB_NAME)
                cursor = conexao.cursor()
                cursor.execute("SELECT id, nome, acai_preferido FROM clientes;")
                clientes = cursor.fetchall()
                conexao.close()
                
                print("\n--- CLIENTES CADASTRADOS ---")
                if not clientes:
                    print("Nenhum cliente cadastrado ainda.")
                for c in clientes:
                    print(f"ID: {c[0]} | Nome: {c[1]} | Açaí: {c[2]}")
                print("----------------------------")
                
            elif opcao == "3":
                print("Saindo do painel CLI...")
                break
            else:
                print("[OPÇÃO INVÁLIDA] Tente novamente.")
    else:
        print("[ERRO] Senha incorreta! Acesso negado.")

if __name__ == "__main__":
    painel_administrativo_real()