import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
DB_PATH = os.path.join(BASE_DIR, "acai_sistema.db")
FACES_DIR = os.path.join(PROJECT_ROOT, "assets", "faces")

def garantir_diretorios():
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(FACES_DIR, exist_ok=True)

def conectar():
    garantir_diretorios()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            telefone TEXT,
            pontos_fidelidade INTEGER DEFAULT 0,
            foto_path TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            tamanho TEXT NOT NULL,
            toppings TEXT,
            forma_pagamento TEXT,
            opcao_entrega TEXT,
            subtotal REAL,
            taxa_entrega REAL,
            total REAL,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

def cadastrar_cliente(nome, cpf, telefone, foto_path=""):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO clientes (nome, cpf, telefone, pontos_fidelidade, foto_path)
            VALUES (?, ?, ?, 50, ?)
        ''', (nome, cpf, telefone, foto_path))
        conn.commit()
        cliente_id = cursor.lastrowid
        return True, cliente_id
    except sqlite3.IntegrityError:
        return False, "CPF já cadastrado no Açaízon."
    finally:
        conn.close()

def buscar_cliente_por_id(cliente_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, cpf, telefone, pontos_fidelidade, foto_path FROM clientes WHERE id = ?', (cliente_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0], "nome": row[1], "cpf": row[2],
            "telefone": row[3], "pontos_fidelidade": row[4], "foto_path": row[5]
        }
    return None

def buscar_ultimo_cliente():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cpf, telefone, pontos_fidelidade, foto_path FROM clientes ORDER BY id DESC LIMIT 1;")
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0], "nome": row[1], "cpf": row[2],
            "telefone": row[3], "pontos_fidelidade": row[4], "foto_path": row[5]
        }
    return None

def buscar_ultimo_pedido(cliente_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT tamanho, toppings, forma_pagamento, opcao_entrega 
        FROM pedidos WHERE cliente_id = ? ORDER BY id DESC LIMIT 1
    ''', (cliente_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {"tamanho": row[0], "toppings": row[1], "forma_pagamento": row[2], "opcao_entrega": row[3]}
    return None

def salvar_pedido(cliente_id, tamanho, toppings, forma_pagamento, opcao_entrega, subtotal, taxa_entrega, total):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO pedidos (cliente_id, tamanho, toppings, forma_pagamento, opcao_entrega, subtotal, taxa_entrega, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (cliente_id, tamanho, toppings, forma_pagamento, opcao_entrega, subtotal, taxa_entrega, total))

    cursor.execute('UPDATE clientes SET pontos_fidelidade = pontos_fidelidade + 10 WHERE id = ?', (cliente_id,))
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    inicializar_banco()