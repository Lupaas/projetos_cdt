import sqlite3
import json
import urllib.request
import pwinput
import os
from faker import Faker

# Inicializa o Faker para o português do Brasil
fake = Faker('pt_BR')

DB_NAME = 'acaiteria.db'
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
    
    # Teste de conectividade com urllib.request
    try:
        urllib.request.urlopen("https://www.google.com", timeout=2)
        print("[URLLIB] Conexão com a rede estabelecida.")
    except Exception:
        print("[URLLIB] Modo offline ativado.")

def painel_automacao_faker():
    """Automação para popular o banco via terminal exigindo senha segura (pwinput)."""
    inicializar_banco()
    verificar_configuracoes_sistema()
    
    print("\n========================================")
    print(" PAINEL DE AUTOMAÇÃO - DELÍRIO ROXO (CLI)")
    print("========================================")
    
    # Exigência de pwinput para senha segura
    senha = pwinput.pwinput(prompt="Digite a senha de Administrador (padrão: admin123): ", mask="*")
    
    if senha == "admin123":
        conexao = sqlite3.connect(DB_NAME)
        cursor = conexao.cursor()
        
        complementos = ["com Leite Condensado e Morango", "com Paçoca e Banana", "com Ninho e Granola"]
        print("\n[FAKER] Gerando clientes automáticos...")
        
        for _ in range(5):
            nome = fake.name()
            email = fake.email()
            telefone = fake.phone_number()
            endereco = fake.address()
            acai = f"Açaí 500ml {fake.random_element(complementos)}"
            
            cursor.execute('''
                INSERT INTO clientes (nome, apelido, email, telefone, endereco, idade, acai_preferido) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nome, "FakerUser", email, telefone, endereco, "25", acai))
            
        conexao.commit()
        conexao.close()
        print("[SQL] 5 clientes falsos injetados com sucesso no banco de dados!")
    else:
        print("[ERRO] Senha incorreta! Acesso negado.")

if __name__ == "__main__":
    painel_automacao_faker()