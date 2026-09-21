import tkinter as tk
from tkinter import messagebox

# ============================================================
# IMPORTAÇÕES DO BACK-END E RECONHECIMENTO FACIAL
# ============================================================
# Garanta que os arquivos 'database/db.py' e 'src/camera.py' existam no seu projeto.
try:
    from database.db import cadastrar_cliente, buscar_cliente_por_cpf, buscar_historico_pedidos
except ImportError:
    # Funções de fallback caso o módulo de banco de dados ainda não esteja no mesmo diretório
    def cadastrar_cliente(nome, apelido, email, telefone, endereco, idade, cpf):
        print(f"[DB Simulado] Cadastrando: {nome}, {telefone}")
        return True, "Cliente cadastrado com sucesso!"

    def buscar_cliente_por_cpf(cpf):
        return None

    def buscar_historico_pedidos(cliente_id):
        return []

try:
    from src.camera import reconhecer_cliente
except ImportError:
    # Função simulada de reconhecimento facial
    def reconhecer_cliente():
        print("[Câmera Simulada] Iniciando reconhecimento...")
        return {"status": "novo_cliente"}


# ============================================================
# CONFIGURAÇÕES DE LAYOUT E CORES
# ============================================================

LARGURA = 1200
ALTURA = 700

ROXO_ESCURO = "#17062F"
ROXO = "#3A126B"
ROXO_MEDIO = "#5A1B91"
ROSA = "#E91E83"
ROSA_CLARO = "#F52B91"
AMARELO = "#FFD21C"
BRANCO = "#FFFFFF"
CINZA = "#B9AFC8"
VERDE = "#42A62A"


# ============================================================
# JANELA PRINCIPAL
# ============================================================

janela = tk.Tk()
janela.title("Açaízon - Sistema PDV")
janela.geometry(f"{LARGURA}x{ALTURA}")
janela.minsize(1000, 600)
janela.configure(bg=ROXO_ESCURO)


# ============================================================
# FUNÇÕES DE NAVEGAÇÃO E REGRAS DE NEGÓCIO
# ============================================================

def limpar_conteudo():
    """Remove os widgets da área central."""
    for widget in area_conteudo.winfo_children():
        widget.destroy()


def acionar_camera_reconhecimento():
    """
    Aciona o módulo de reconhecimento facial da Pessoa 1 (Lari).
    Atualiza o painel do cliente se for encontrado ou redireciona para o cadastro.
    """
    janela.iconify()  # Minimiza a janela principal temporariamente
    resultado = reconhecer_cliente()
    janela.deiconify()  # Restaura a janela principal

    if resultado and resultado.get("status") == "encontrado":
        nome = resultado.get("nome", "Cliente")
        cpf = resultado.get("cpf", "-")
        favorito = resultado.get("pedido_favorito", "Açaí Tradicional")
        data_cad = resultado.get("data_cadastro", "Hoje")

        messagebox.showinfo("Açaízon", f"Bem-vindo(a) de volta, {nome}!")
        atualizar_painel_cliente(nome=nome, favorito=favorito, data=data_cad)
        atualizar_ultimos_pedidos(f"Último: {favorito}")
    else:
        messagebox.showwarning(
            "Reconhecimento Facial",
            "Rosto não identificado ou novo cliente.\nPor favor, faça o cadastro manual."
        )
        mostrar_cliente()


def mostrar_inicio():
    """Mostra a tela inicial com integração de câmera."""
    limpar_conteudo()

    titulo = tk.Label(
        area_conteudo,
        text="Bem-vindo ao Açaízon!",
        font=("Arial", 24, "bold"),
        fg=BRANCO,
        bg=ROXO_ESCURO
    )
    titulo.pack(pady=(35, 10))

    subtitulo = tk.Label(
        area_conteudo,
        text="Mais que açaí, uma energia pra você!",
        font=("Arial", 12),
        fg=CINZA,
        bg=ROXO_ESCURO
    )
    subtitulo.pack()

    # Caixa principal
    caixa = tk.Frame(
        area_conteudo,
        bg="#21103D",
        highlightbackground=ROXO_MEDIO,
        highlightthickness=1
    )
    caixa.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=30
    )

    # Botão interativo da Câmera
    icone_cam = tk.Button(
        caixa,
        text="📷",
        font=("Arial", 50),
        fg=AMARELO,
        bg="#21103D",
        activebackground="#21103D",
        activeforeground=ROSA,
        bd=0,
        cursor="hand2",
        command=acionar_camera_reconhecimento
    )
    icone_cam.pack(pady=(40, 10))

    texto = tk.Label(
        caixa,
        text="Clique na câmera ou posicione seu rosto\npara iniciar o reconhecimento",
        font=("Arial", 14, "bold"),
        fg=BRANCO,
        bg="#21103D",
        justify="center"
    )
    texto.pack()

    linha = tk.Frame(
        caixa,
        bg=AMARELO,
        height=4,
        width=100
    )
    linha.pack(pady=15)

    botao_iniciar_cam = tk.Button(
        caixa,
        text="Iniciar Câmera",
        font=("Arial", 11, "bold"),
        bg=ROSA,
        fg=BRANCO,
        activebackground=ROSA_CLARO,
        activeforeground=BRANCO,
        relief="flat",
        cursor="hand2",
        command=acionar_camera_reconhecimento
    )
    botao_iniciar_cam.pack(pady=5, ipadx=15, ipady=5)

    dica = tk.Label(
        caixa,
        text="Ou escolha uma opção no menu ao lado.",
        font=("Arial", 10),
        fg=CINZA,
        bg="#21103D"
    )
    dica.pack(pady=(10, 0))


def mostrar_cardapio():
    """Mostra o cardápio e conecta a adição de pedidos ao sistema."""
    limpar_conteudo()

    titulo = tk.Label(
        area_conteudo,
        text="🥣 Cardápio",
        font=("Arial", 24, "bold"),
        fg=BRANCO,
        bg=ROXO_ESCURO
    )
    titulo.pack(pady=25)

    produtos = [
        ("Açaí Tradicional", "R$ 15,00"),
        ("Açaí com Morango", "R$ 18,00"),
        ("Açaí com Banana", "R$ 17,00"),
        ("Açaí Especial", "R$ 22,00"),
    ]

    for nome, preco in produtos:
        produto = tk.Frame(
            area_conteudo,
            bg="#261044",
            highlightbackground=ROXO_MEDIO,
            highlightthickness=1
        )
        produto.pack(
            fill="x",
            padx=50,
            pady=7
        )

        nome_label = tk.Label(
            produto,
            text=nome,
            font=("Arial", 13, "bold"),
            fg=BRANCO,
            bg="#261044"
        )
        nome_label.pack(
            side="left",
            padx=20,
            pady=15
        )

        preco_label = tk.Label(
            produto,
            text=preco,
            font=("Arial", 12, "bold"),
            fg=AMARELO,
            bg="#261044"
        )
        preco_label.pack(
            side="right",
            padx=20
        )

        botao = tk.Button(
            produto,
            text="Adicionar",
            font=("Arial", 10, "bold"),
            bg=ROSA,
            fg=BRANCO,
            activebackground=ROSA_CLARO,
            activeforeground=BRANCO,
            relief="flat",
            cursor="hand2",
            command=lambda p=nome: adicionar_produto(p)
        )
        botao.pack(
            side="right",
            padx=10
        )


def adicionar_produto(produto):
    """Adiciona produto ao pedido e atualiza o histórico do painel direito."""
    messagebox.showinfo(
        "Açaízon",
        f"{produto} foi adicionado ao pedido!"
    )
    atualizar_ultimos_pedidos(f"1x {produto}")


def mostrar_cliente():
    """Mostra o formulário de cadastro conectado ao Back-end (db.py)."""
    limpar_conteudo()

    titulo = tk.Label(
        area_conteudo,
        text="👤 Cliente",
        font=("Arial", 24, "bold"),
        fg=BRANCO,
        bg=ROXO_ESCURO
    )
    titulo.pack(pady=25)

    formulario = tk.Frame(
        area_conteudo,
        bg="#21103D",
        highlightbackground=ROXO_MEDIO,
        highlightthickness=1
    )
    formulario.pack(
        padx=60,
        pady=10,
        fill="x"
    )

    # Campo Nome
    tk.Label(
        formulario,
        text="Nome do cliente",
        font=("Arial", 11, "bold"),
        fg=BRANCO,
        bg="#21103D"
    ).pack(anchor="w", padx=25, pady=(25, 5))

    entrada_nome = tk.Entry(
        formulario,
        font=("Arial", 12),
        bg="#32194F",
        fg=BRANCO,
        insertbackground=BRANCO,
        relief="flat"
    )
    entrada_nome.pack(fill="x", padx=25, ipady=8)

    # Campo Telefone / CPF
    tk.Label(
        formulario,
        text="Telefone / CPF",
        font=("Arial", 11, "bold"),
        fg=BRANCO,
        bg="#21103D"
    ).pack(anchor="w", padx=25, pady=(20, 5))

    entrada_telefone = tk.Entry(
        formulario,
        font=("Arial", 12),
        bg="#32194F",
        fg=BRANCO,
        insertbackground=BRANCO,
        relief="flat"
    )
    entrada_telefone.pack(fill="x", padx=25, ipady=8)

    def cadastrar():
        nome = entrada_nome.get().strip()
        telefone = entrada_telefone.get().strip()

        if not nome:
            messagebox.showwarning(
                "Atenção",
                "Digite o nome do cliente."
            )
            return

        # Conexão real com a função do banco de dados (db.py)
        sucesso, res = cadastrar_cliente(
            nome=nome,
            apelido="",
            email="",
            telefone=telefone,
            endereco="",
            idade=0,
            cpf=telefone
        )

        if sucesso:
            messagebox.showinfo(
                "Cadastro",
                f"Cliente {nome} cadastrado com sucesso!"
            )
            # Atualiza o painel direito dinamicamente
            atualizar_painel_cliente(nome=nome, favorito="-", data="Hoje")
            entrada_nome.delete(0, tk.END)
            entrada_telefone.delete(0, tk.END)
        else:
            messagebox.showerror("Erro", f"Erro ao cadastrar: {res}")

    tk.Button(
        formulario,
        text="Cadastrar Cliente",
        font=("Arial", 11, "bold"),
        bg=AMARELO,
        fg="#3B2600",
        activebackground="#FFE45C",
        relief="flat",
        cursor="hand2",
        command=cadastrar
    ).pack(
        pady=25,
        ipadx=20,
        ipady=8
    )


def mostrar_configuracoes():
    """Mostra configurações."""
    limpar_conteudo()

    titulo = tk.Label(
        area_conteudo,
        text="⚙️ Configurações",
        font=("Arial", 24, "bold"),
        fg=BRANCO,
        bg=ROXO_ESCURO
    )
    titulo.pack(pady=30)

    opcoes = [
        "Configurações da conta",
        "Configurações do sistema",
        "Impressora",
        "Forma de pagamento"
    ]

    for opcao in opcoes:
        botao = tk.Button(
            area_conteudo,
            text=opcao,
            font=("Arial", 12),
            bg="#32134F",
            fg=BRANCO,
            activebackground=ROXO_MEDIO,
            activeforeground=BRANCO,
            relief="flat",
            anchor="w",
            cursor="hand2"
        )
        botao.pack(
            fill="x",
            padx=70,
            pady=6,
            ipady=10
        )


def sair():
    """Fecha o sistema."""
    resposta = messagebox.askyesno(
        "Sair",
        "Deseja realmente sair do Açaízon?"
    )
    if resposta:
        janela.destroy()


# ============================================================
# CABEÇALHO
# ============================================================

cabecalho = tk.Frame(
    janela,
    bg="#3A075C",
    height=105
)
cabecalho.pack(side="top", fill="x")
cabecalho.pack_propagate(False)

# Logo
logo = tk.Label(
    cabecalho,
    text="Açaízon",
    font=("Arial", 30, "bold"),
    fg=BRANCO,
    bg="#3A075C"
)
logo.pack(side="left", padx=35)

# Frase
frase = tk.Label(
    cabecalho,
    text="Mais que Açaí,\né energia pra você! ♡",
    font=("Arial", 10, "italic"),
    fg=BRANCO,
    bg="#3A075C",
    justify="left"
)
frase.pack(side="left", padx=20)

# Logo central
logo_central = tk.Label(
    cabecalho,
    text="🍇\nAçaízon",
    font=("Arial", 15, "bold"),
    fg=BRANCO,
    bg="#3A075C"
)
logo_central.place(relx=0.50, rely=0.50, anchor="center")

# Texto do lado direito
qualidade = tk.Label(
    cabecalho,
    text="Sabor de\nQualidade e Energia! ✨",
    font=("Arial", 11, "bold"),
    fg=BRANCO,
    bg="#3A075C",
    justify="center"
)
qualidade.pack(side="right", padx=40)


# ============================================================
# CORPO PRINCIPAL
# ============================================================

corpo = tk.Frame(janela, bg=ROXO_ESCURO)
corpo.pack(fill="both", expand=True)


# ============================================================
# MENU LATERAL
# ============================================================

menu_lateral = tk.Frame(
    corpo,
    bg="#21103D",
    width=220
)
menu_lateral.pack(side="left", fill="y", padx=(10, 5), pady=10)
menu_lateral.pack_propagate(False)


def criar_botao_menu(texto, comando, ativo=False):
    fundo = ROSA if ativo else "#32134F"

    botao = tk.Button(
        menu_lateral,
        text=texto,
        font=("Arial", 12, "bold"),
        bg=fundo,
        fg=BRANCO,
        activebackground=ROSA_CLARO,
        activeforeground=BRANCO,
        relief="flat",
        cursor="hand2",
        anchor="w",
        padx=20,
        command=comando
    )
    botao.pack(fill="x", padx=10, pady=7, ipady=8)
    return botao


botao_inicio = criar_botao_menu("🏠   Início", mostrar_inicio, True)
botao_cardapio = criar_botao_menu("🥣   Cardápio", mostrar_cardapio)
botao_cliente = criar_botao_menu("👤   Cliente", mostrar_cliente)
botao_config = criar_botao_menu("⚙️   Configurações", mostrar_configuracoes)

frase_menu = tk.Label(
    menu_lateral,
    text="Aqui seu dia\nfica mais doce! ♡",
    font=("Arial", 10, "italic"),
    fg=BRANCO,
    bg="#21103D",
    justify="left"
)
frase_menu.pack(side="bottom", anchor="w", padx=25, pady=35)


# ============================================================
# ÁREA CENTRAL
# ============================================================

area_conteudo = tk.Frame(corpo, bg=ROXO_ESCURO)
area_conteudo.pack(side="left", fill="both", expand=True, padx=5, pady=10)


# ============================================================
# PAINEL DIREITO (DINÂMICO)
# ============================================================

painel_direito = tk.Frame(
    corpo,
    bg="#21103D",
    width=290
)
painel_direito.pack(side="right", fill="y", padx=(5, 10), pady=10)
painel_direito.pack_propagate(False)

# Cadastro
titulo_cadastro = tk.Label(
    painel_direito,
    text="👤  Cadastro + Informações",
    font=("Arial", 11, "bold"),
    fg=BRANCO,
    bg="#21103D"
)
titulo_cadastro.pack(pady=(20, 10))

icone_cliente = tk.Label(
    painel_direito,
    text="●",
    font=("Arial", 35),
    fg=ROSA,
    bg="#21103D"
)
icone_cliente.pack()

texto_cliente = tk.Label(
    painel_direito,
    text="Olá!\nFaça seu cadastro para\nter uma experiência ainda\nmais especial!",
    font=("Arial", 9),
    fg=CINZA,
    bg="#21103D",
    justify="center"
)
texto_cliente.pack(pady=5)

botao_cadastrar = tk.Button(
    painel_direito,
    text="👤  Cadastrar Cliente",
    font=("Arial", 10, "bold"),
    bg=AMARELO,
    fg="#3B2600",
    activebackground="#FFE45C",
    relief="flat",
    cursor="hand2",
    command=mostrar_cliente
)
botao_cadastrar.pack(fill="x", padx=18, pady=12, ipady=7)

# ÚLTIMOS PEDIDOS
titulo_pedidos = tk.Label(
    painel_direito,
    text="♻  Últimos pedidos",
    font=("Arial", 10, "bold"),
    fg=VERDE,
    bg="#21103D"
)
titulo_pedidos.pack(anchor="w", padx=20, pady=(15, 8))

pedidos = tk.Frame(
    painel_direito,
    bg="#261044",
    highlightbackground=ROXO_MEDIO,
    highlightthickness=1
)
pedidos.pack(fill="x", padx=18)

label_icone_pedidos = tk.Label(
    pedidos,
    text="🥣",
    font=("Arial", 25),
    fg=BRANCO,
    bg="#261044"
)
label_icone_pedidos.pack(pady=(12, 3))

label_titulo_pedidos = tk.Label(
    pedidos,
    text="Nenhum pedido encontrado",
    font=("Arial", 9, "bold"),
    fg=BRANCO,
    bg="#261044"
)
label_titulo_pedidos.pack()

label_desc_pedidos = tk.Label(
    pedidos,
    text="Ainda não há pedidos registrados\npara este cliente.",
    font=("Arial", 8),
    fg=CINZA,
    bg="#261044",
    justify="center"
)
label_desc_pedidos.pack(pady=(3, 15))

# INFORMAÇÕES DO CLIENTE
titulo_info = tk.Label(
    painel_direito,
    text="●  Informações do cliente",
    font=("Arial", 10, "bold"),
    fg=AMARELO,
    bg="#21103D"
)
titulo_info.pack(anchor="w", padx=20, pady=(18, 8))

info = tk.Frame(
    painel_direito,
    bg="#261044",
    highlightbackground=ROXO_MEDIO,
    highlightthickness=1
)
info.pack(fill="x", padx=18)

# Rótulo de texto dinâmico para dados do cliente
label_info_dados = tk.Label(
    info,
    text="Nome: -\n\n"
         "Pedido favorito: -\n\n"
         "Data do cadastro: -",
    font=("Arial", 8),
    fg=BRANCO,
    bg="#261044",
    justify="left",
    anchor="w"
)
label_info_dados.pack(fill="x", padx=12, pady=12)


# ============================================================
# FUNÇÕES DE ATUALIZAÇÃO DO PAINEL DIREITO
# ============================================================



def atualizar_painel_cliente(nome, favorito="-", data="-"):
    """Atualiza o bloco 'Informações do cliente' com os dados recebidos."""
    label_info_dados.config(
        text=f"Nome: {nome}\n\n"
             f"Pedido favorito: {favorito}\n\n"
             f"Data do cadastro: {data}"
    )


def atualizar_ultimos_pedidos(detalhe_pedido):
    """Atualiza o bloco 'Últimos pedidos' ao realizar uma compra."""
    label_titulo_pedidos.config(text="Pedido Recente")
    label_desc_pedidos.config(text=detalhe_pedido)


# ============================================================
# FUNÇÃO PRINCIPAL DE INICIALIZAÇÃO
# ============================================================

def iniciar_aplicacao():
    """Função chamada pelo main.py para rodar o sistema."""
    mostrar_inicio()
    janela.mainloop()

# Permite rodar o app.py diretamente para testes se necessário
if __name__ == "__main__":
    iniciar_aplicacao()