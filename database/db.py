import sqlite3
import os
import json

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


def adicionar_coluna_se_nao_existir(cursor, tabela, coluna, definicao):
    cursor.execute(f"PRAGMA table_info({tabela})")
    colunas = [row[1] for row in cursor.fetchall()]

    if coluna not in colunas:
        cursor.execute(
            f"ALTER TABLE {tabela} ADD COLUMN {coluna} {definicao}"
        )


def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            telefone TEXT,
            pontos_fidelidade INTEGER DEFAULT 0,
            foto_path TEXT
        )
    """)

    # Migração para instalações antigas do projeto.
    # Essas colunas permitem que os dados preenchidos no formulário
    # também sejam persistidos e recuperados pelo Root Master.
    adicionar_coluna_se_nao_existir(cursor, "clientes", "apelido", "TEXT")
    adicionar_coluna_se_nao_existir(cursor, "clientes", "email", "TEXT")
    adicionar_coluna_se_nao_existir(cursor, "clientes", "endereco", "TEXT")
    adicionar_coluna_se_nao_existir(cursor, "clientes", "idade", "INTEGER")

    cursor.execute("""
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
    """)

    conn.commit()
    conn.close()


def cadastrar_cliente(
    nome,
    cpf,
    telefone,
    foto_path="",
    apelido="",
    email="",
    endereco="",
    idade=None
):
    conn = conectar()
    cursor = conn.cursor()

    try:
        idade_valor = None
        if idade not in (None, ""):
            try:
                idade_valor = int(idade)
            except (ValueError, TypeError):
                idade_valor = None

        cursor.execute("""
            INSERT INTO clientes (
                nome,
                cpf,
                telefone,
                pontos_fidelidade,
                foto_path,
                apelido,
                email,
                endereco,
                idade
            )
            VALUES (?, ?, ?, 50, ?, ?, ?, ?, ?)
        """, (
            nome,
            cpf,
            telefone,
            foto_path,
            apelido,
            email,
            endereco,
            idade_valor
        ))

        conn.commit()
        cliente_id = cursor.lastrowid
        return True, cliente_id

    except sqlite3.IntegrityError:
        return False, "CPF já cadastrado no Açaízon."

    finally:
        conn.close()


def _cliente_dict(row):
    if not row:
        return None

    return {
        "id": row[0],
        "nome": row[1],
        "cpf": row[2],
        "telefone": row[3],
        "pontos_fidelidade": row[4],
        "foto_path": row[5],
        "apelido": row[6],
        "email": row[7],
        "endereco": row[8],
        "idade": row[9]
    }


def buscar_cliente_por_id(cliente_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            nome,
            cpf,
            telefone,
            pontos_fidelidade,
            foto_path,
            apelido,
            email,
            endereco,
            idade
        FROM clientes
        WHERE id = ?
    """, (cliente_id,))

    row = cursor.fetchone()
    conn.close()

    return _cliente_dict(row)


def buscar_ultimo_cliente():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            nome,
            cpf,
            telefone,
            pontos_fidelidade,
            foto_path,
            apelido,
            email,
            endereco,
            idade
        FROM clientes
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    return _cliente_dict(row)


def listar_clientes():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            nome,
            cpf,
            telefone,
            pontos_fidelidade,
            foto_path,
            apelido,
            email,
            endereco,
            idade
        FROM clientes
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [_cliente_dict(row) for row in rows]


def buscar_ultimo_pedido(cliente_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            tamanho,
            toppings,
            forma_pagamento,
            opcao_entrega
        FROM pedidos
        WHERE cliente_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (cliente_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "tamanho": row[0],
            "toppings": row[1],
            "forma_pagamento": row[2],
            "opcao_entrega": row[3]
        }

    return None


def salvar_pedido(
    cliente_id,
    tamanho,
    toppings,
    forma_pagamento,
    opcao_entrega,
    subtotal,
    taxa_entrega,
    total
):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pedidos (
            cliente_id,
            tamanho,
            toppings,
            forma_pagamento,
            opcao_entrega,
            subtotal,
            taxa_entrega,
            total
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cliente_id,
        tamanho,
        toppings,
        forma_pagamento,
        opcao_entrega,
        subtotal,
        taxa_entrega,
        total
    ))

    cursor.execute("""
        UPDATE clientes
        SET pontos_fidelidade = pontos_fidelidade + 10
        WHERE id = ?
    """, (cliente_id,))

    pedido_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return True, pedido_id


def _pedido_dict(row):
    if not row:
        return None

    return {
        "id": row[0],
        "cliente_id": row[1],
        "cliente_nome": row[2],
        "cliente_cpf": row[3],
        "tamanho": row[4],
        "toppings": row[5],
        "forma_pagamento": row[6],
        "opcao_entrega": row[7],
        "subtotal": row[8],
        "taxa_entrega": row[9],
        "total": row[10],
        "data_hora": row[11]
    }


def listar_pedidos():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            p.id,
            p.cliente_id,
            c.nome,
            c.cpf,
            p.tamanho,
            p.toppings,
            p.forma_pagamento,
            p.opcao_entrega,
            p.subtotal,
            p.taxa_entrega,
            p.total,
            p.data_hora
        FROM pedidos p
        INNER JOIN clientes c ON c.id = p.cliente_id
        ORDER BY p.id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [_pedido_dict(row) for row in rows]


def buscar_pedido_por_id(pedido_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            p.id,
            p.cliente_id,
            c.nome,
            c.cpf,
            p.tamanho,
            p.toppings,
            p.forma_pagamento,
            p.opcao_entrega,
            p.subtotal,
            p.taxa_entrega,
            p.total,
            p.data_hora
        FROM pedidos p
        INNER JOIN clientes c ON c.id = p.cliente_id
        WHERE p.id = ?
    """, (pedido_id,))

    row = cursor.fetchone()
    conn.close()

    return _pedido_dict(row)


def exportar_dados_json(dados, caminho):
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


if __name__ == "__main__":
    inicializar_banco()
    print("Banco de dados inicializado com sucesso.")
