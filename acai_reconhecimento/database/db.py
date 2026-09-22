import sqlite3
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
DB_PATH = os.path.join(BASE_DIR, "acai_sistema.db")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo_acaizon.png")

def garantir_diretorios():
    os.makedirs(BASE_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)

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
            apelido TEXT,
            email TEXT,
            telefone TEXT,
            endereco TEXT,
            idade INTEGER,
            cpf TEXT UNIQUE NOT NULL,
            pontos_fidelidade INTEGER DEFAULT 0,
            face_encoding TEXT NOT NULL
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

def obter_caminho_logo():
    if os.path.exists(LOGO_PATH):
        return LOGO_PATH
    return None

def cadastrar_cliente_com_faceid(nome, apelido, email, telefone, endereco, idade, cpf, face_encoding):
    if face_encoding is None:
        return False, "O cadastramento do Face ID é obrigatório."

    conn = conectar()
    cursor = conn.cursor()
    encoding_json = json.dumps(face_encoding)

    try:
        cursor.execute('''
            INSERT INTO clientes (nome, apelido, email, telefone, endereco, idade, cpf, face_encoding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, apelido, email, telefone, endereco, idade, cpf, encoding_json))
        conn.commit()
        return True, cursor.lastrowid
    except sqlite3.IntegrityError:
        return False, "CPF já cadastrado no Açaízon."
    finally:
        conn.close()

def obter_todos_encodings():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT id, face_encoding FROM clientes WHERE face_encoding IS NOT NULL')
    registros = cursor.fetchall()
    conn.close()

    resultado = []
    for cliente_id, encoding_str in registros:
        if encoding_str:
            try:
                resultado.append((cliente_id, json.loads(encoding_str)))
            except Exception:
                pass
    return resultado

def buscar_cliente_por_id(cliente_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, apelido, email, telefone, endereco, idade, cpf, pontos_fidelidade FROM clientes WHERE id = ?', (cliente_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0], "nome": row[1], "apelido": row[2], "email": row[3],
            "telefone": row[4], "endereco": row[5], "idade": row[6], "cpf": row[7],
            "pontos_fidelidade": row[8]
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

inicializar_banco()