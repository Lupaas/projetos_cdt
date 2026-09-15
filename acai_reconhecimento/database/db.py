import sqlite3
import json
import os
import pwinput

# Define o caminho do banco de dados de forma dinâmica e segura usando a biblioteca os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "acai_sistema.db")

def garantir_diretorio_banco():
    """Garante que a pasta do banco de dados exista no sistema."""
    diretorio = os.path.dirname(DB_PATH)
    if not os.path.exists(diretorio):
        os.makedirs(diretorio, exist_ok=True)

def conectar():
    """Cria e retorna a conexão com o banco de dados."""
    garantir_diretorio_banco()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")  # Ativa chaves estrangeiras
    return conn

def inicializar_banco():
    """Cria as 3 tabelas necessárias caso ainda não existam."""
    conn = conectar()
    cursor = conn.cursor()

    # 1. Tabela de Clientes
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
            face_encoding TEXT
        )
    ''')

    # 2. Tabela de Cardápio (Nova tabela baseada no seu desenho)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cardapio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_item TEXT NOT NULL,
            tamanho TEXT,
            preco REAL NOT NULL,
            acompanhamentos TEXT
        )
    ''')

    # 3. Tabela de Pedidos (Com Chaves Estrangeiras relacionando Clientes e Cardápio)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            cardapio_id INTEGER,
            quantidade INTEGER DEFAULT 1,
            forma_pagamento TEXT,
            tipo_entrega TEXT,
            valor_total REAL,
            data_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE,
            FOREIGN KEY (cardapio_id) REFERENCES cardapio (id) ON DELETE SET NULL
        )
    ''')

    conn.commit()
    conn.close()

# =====================================================================
# FUNÇÕES AUXILIARES E UTILITÁRIAS (os / pwinput)
# =====================================================================

def limpar_tela():
    """Limpa o console de acordo com o sistema operacional."""
    os.system('cls' if os.name == 'nt' else 'clear')

def ler_dado_sensivel(mensagem="Digite um dado confidencial (ex: CPF): "):
    """Lê uma entrada do usuário no terminal de forma oculta usando pwinput."""
    return pwinput.pwinput(prompt=mensagem, mask="*")

# =====================================================================
# 1. CREATE (Inserir)
# =====================================================================

def cadastrar_cliente(nome, apelido, email, telefone, endereco, idade, cpf, face_encoding=None):
    """Insere um novo cliente no banco de dados."""
    conn = conectar()
    cursor = conn.cursor()
    
    # Converte o vetor numérico do rosto para string JSON para salvar no SQLite
    encoding_json = json.dumps(face_encoding) if face_encoding is not None else None

    try:
        cursor.execute('''
            INSERT INTO clientes (nome, apelido, email, telefone, endereco, idade, cpf, face_encoding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, apelido, email, telefone, endereco, idade, cpf, encoding_json))
        conn.commit()
        cliente_id = cursor.lastrowid
        return True, cliente_id
    except sqlite3.IntegrityError:
        return False, "CPF já cadastrado."
    finally:
        conn.close()
        
def cadastrar_item_cardapio(nome_item, tamanho, preco, acompanhamentos):
    """Insere um novo item de açaí/produto no cardápio."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cardapio (nome_item, tamanho, preco, acompanhamentos)
        VALUES (?, ?, ?, ?)
    ''', (nome_item, tamanho, preco, acompanhamentos))
    conn.commit()
    conn.close()
    return True

def salvar_pedido(cliente_id, tamanho, toppings, forma_pagamento, opcao_entrega, subtotal, taxa_entrega, total):
    """Salva um novo pedido e adiciona +10 pontos no clube de fidelidade Delírio Roxo."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO pedidos (cliente_id, tamanho, toppings, forma_pagamento, opcao_entrega, subtotal, taxa_entrega, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (cliente_id, tamanho, toppings, forma_pagamento, opcao_entrega, subtotal, taxa_entrega, total))

    # Regra de Negócio: +10 pontos no Clube Delírio Roxo a cada pedido efetuado
    cursor.execute('''
        UPDATE clientes SET pontos_fidelidade = pontos_fidelidade + 10 WHERE id = ?
    ''', (cliente_id,))

    conn.commit()
    conn.close()
    return True

# =====================================================================
# 2. READ (Consultar)
# =====================================================================

def obter_todos_encodings():
    """Retorna uma lista de tuplas (cliente_id, face_encoding) para a IA (Pessoa 1) comparar."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT id, face_encoding FROM clientes WHERE face_encoding IS NOT NULL')
    registros = cursor.fetchall()
    conn.close()

    resultado = []
    for cliente_id, encoding_str in registros:
        if encoding_str:
            resultado.append((cliente_id, json.loads(encoding_str)))
    return resultado

def buscar_cliente_por_id(cliente_id):
    """Busca dados completos do cliente pelo ID."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, apelido, email, telefone, endereco, idade, cpf, pontos_fidelidade FROM clientes WHERE id = ?', (cliente_id,))
    cliente = cursor.fetchone()
    conn.close()
    return cliente

def buscar_ultimo_pedido(cliente_id):
    """Busca o último pedido do cliente para preencher a opção 'Peça o de sempre!'."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT tamanho, toppings, forma_pagamento, opcao_entrega 
        FROM pedidos WHERE cliente_id = ? ORDER BY id DESC LIMIT 1
    ''', (cliente_id,))
    pedido = cursor.fetchone()
    conn.close()
    return pedido

# =====================================================================
# 3. UPDATE (Atualizar)
# =====================================================================

def atualizar_cliente(cliente_id, nome=None, telefone=None, endereco=None, face_encoding=None):
    """Atualiza dados cadastrais ou a foto/reconhecimento facial do cliente."""
    conn = conectar()
    cursor = conn.cursor()

    if face_encoding is not None:
        cursor.execute('UPDATE clientes SET face_encoding = ? WHERE id = ?', (json.dumps(face_encoding), cliente_id))
    if nome:
        cursor.execute('UPDATE clientes SET nome = ? WHERE id = ?', (nome, cliente_id))
    if telefone:
        cursor.execute('UPDATE clientes SET telefone = ? WHERE id = ?', (telefone, cliente_id))
    if endereco:
        cursor.execute('UPDATE clientes SET endereco = ? WHERE id = ?', (endereco, cliente_id))

    conn.commit()
    conn.close()
    return True

# =====================================================================
# 4. DELETE (Deletar)
# =====================================================================

def deletar_cliente(cliente_id):
    """Remove o cliente do sistema e apaga o histórico de pedidos."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clientes WHERE id = ?', (cliente_id,))
    conn.commit()
    conn.close()
    return True

# Execução de teste
if __name__ == "__main__":
    inicializar_banco()
    print("Banco de dados do Açaízon criado e configurado com sucesso!")