import os
import sys
import json
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
sys.path.append(PROJECT_ROOT)

from database.db import (
    cadastrar_cliente,
    buscar_cliente_por_id,
    buscar_ultimo_pedido,
    salvar_pedido,
    listar_clientes,
    listar_pedidos,
    buscar_pedido_por_id,
    exportar_dados_json
)
from src.camera import capturar_foto_cadastro

LARGURA, ALTURA = 1200, 700
ROXO_ESCURO = "#17062F"
ROXO_MEDIO = "#5A1B91"
ROSA, ROSA_CLARO = "#E91E83", "#F52B91"
AMARELO, BRANCO, CINZA, VERDE = "#FFD21C", "#FFFFFF", "#B9AFC8", "#42A62A"

ROOT_MASTER_USUARIO = "root"
ROOT_MASTER_SENHA = "admin123"

logo_img_ref = None
cliente_logado = None
carrinho = []
desconto_fidelidade = 0.0

janela = tk.Tk()
janela.title("Açaízon - Sistema PDV")
janela.geometry(f"{LARGURA}x{ALTURA}")
janela.configure(bg=ROXO_ESCURO)

PRODUTOS = [
    {
        "id": 1,
        "nome": "Monte o seu Açaí",
        "descricao": "Escolha o tamanho e selecione os acompanhamentos que você mais gosta!",
        "preco_300ml": 14.00, "preco_500ml": 20.00, "preco_700ml": 26.00,
        "emoji": "🥣"
    },
    {
        "id": 2,
        "nome": "Açaí Tradicional",
        "descricao": "Açaí puro e cremoso, batido com xarope de guaraná tradicional da casa.",
        "preco_300ml": 12.00, "preco_500ml": 17.00, "preco_700ml": 22.00,
        "emoji": "🥛"
    },
    {
        "id": 3,
        "nome": "Açaí Premium",
        "descricao": "Açaí cremoso acompanhado de camadas generosas de Nutella, Leite Ninho e Morango.",
        "preco_300ml": 18.00, "preco_500ml": 24.00, "preco_700ml": 30.00,
        "emoji": "🍧"
    },
    {
        "id": 4,
        "nome": "Açaí Especial",
        "descricao": "Nossa receita secreta especial! Açaí com Banana, Kiwi, Paçoca, Mel e Calda Extra.",
        "preco_300ml": 20.00, "preco_500ml": 27.00, "preco_700ml": 34.00,
        "emoji": "🍨"
    }
]

ACOMPANHAMENTOS = [
    "Leite em Pó", "Granola", "Paçoca", "Leite Condensado",
    "Morango", "Banana", "Nutella", "Uva", "Mel", "Confete"
]


def carregar_logo():
    global logo_img_ref

    caminhos_possiveis = [
        os.path.join(PROJECT_ROOT, "assets", "logo_acai.png"),
        os.path.join(BASE_DIR, "assets", "logo_acai.png"),
        os.path.join(os.path.dirname(__file__), "..", "assets", "logo_acai.png"),
        os.path.join("assets", "logo_acai.png")
    ]

    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            try:
                img = Image.open(caminho)
                img = img.convert("RGBA")
                img = img.resize((120, 120), Image.Resampling.LANCZOS)
                logo_img_ref = ImageTk.PhotoImage(img)
                return logo_img_ref
            except Exception as e:
                print(f"Erro ao carregar imagem PNG: {e}")
                return None

    print("⚠️ Imagem 'logo_acai.png' não foi encontrada na pasta 'assets'.")
    return None


def limpar_conteudo():
    for widget in area_conteudo.winfo_children():
        widget.destroy()


def mascarar_dado(texto, visiveis=3):
    if not texto:
        return "-"
    texto = str(texto)
    if len(texto) <= visiveis:
        return "*" * len(texto)
    return "*" * (len(texto) - visiveis) + texto[-visiveis:]


def atualizar_painel_direito():
    for widget in painel_direito.winfo_children():
        widget.destroy()

    tk.Label(
        painel_direito,
        text="👤 Painel do Cliente",
        font=("Arial", 11, "bold"),
        fg=BRANCO,
        bg="#21103D"
    ).pack(pady=(15, 10))

    if cliente_logado:
        info = tk.Frame(
            painel_direito,
            bg="#261044",
            highlightbackground=ROXO_MEDIO,
            highlightthickness=1
        )
        info.pack(fill="x", padx=15, pady=5)

        tk.Label(
            info,
            text=f"Olá, {cliente_logado.get('nome')}!",
            font=("Arial", 10, "bold"),
            fg=AMARELO,
            bg="#261044"
        ).pack(anchor="w", padx=10, pady=(8, 2))

        tk.Label(
            info,
            text=f"CPF: ***.***.{mascarar_dado(cliente_logado.get('cpf'), 3)}",
            font=("Arial", 8),
            fg=BRANCO,
            bg="#261044"
        ).pack(anchor="w", padx=10)

        pts = cliente_logado.get('pontos', 0)

        tk.Label(
            info,
            text=f"Pontos: {pts} pts 💜",
            font=("Arial", 9, "bold"),
            fg=ROSA_CLARO,
            bg="#261044"
        ).pack(anchor="w", padx=10, pady=(2, 8))

        tk.Button(
            painel_direito,
            text="Sair da Conta",
            font=("Arial", 9, "bold"),
            bg=ROSA,
            fg=BRANCO,
            relief="flat",
            cursor="hand2",
            command=deslogar_cliente
        ).pack(fill="x", padx=15, pady=5)

    else:
        tk.Label(
            painel_direito,
            text="Olá!\nCadastre-se para acumular pontos!",
            font=("Arial", 9),
            fg=CINZA,
            bg="#21103D",
            justify="center"
        ).pack(pady=5)

        tk.Button(
            painel_direito,
            text="🔑 Entrar (Face ID)",
            font=("Arial", 9, "bold"),
            bg=ROXO_MEDIO,
            fg=BRANCO,
            relief="flat",
            cursor="hand2",
            command=lambda: main_ref.acionar_login_face_id()
            if main_ref
            else messagebox.showwarning(
                "Atenção",
                "Execute o sistema através do main.py"
            )
        ).pack(fill="x", padx=15, pady=3)

        tk.Button(
            painel_direito,
            text="👤 Cadastrar Cliente + Face ID",
            font=("Arial", 10, "bold"),
            bg=AMARELO,
            fg="#3B2600",
            relief="flat",
            cursor="hand2",
            command=abrir_modal_cadastro
        ).pack(fill="x", padx=15, pady=5)

    tk.Label(
        painel_direito,
        text="🛒 Seu Carrinho",
        font=("Arial", 10, "bold"),
        fg=VERDE,
        bg="#21103D"
    ).pack(anchor="w", padx=15, pady=(15, 5))

    f_pedidos = tk.Frame(
        painel_direito,
        bg="#261044",
        highlightbackground=ROXO_MEDIO,
        highlightthickness=1
    )
    f_pedidos.pack(fill="x", padx=15)

    if carrinho:
        subtotal = sum(i['preco'] for i in carrinho)

        for item in carrinho:
            tk.Label(
                f_pedidos,
                text=f"• {item['nome']} - R$ {item['preco']:.2f}",
                font=("Arial", 8, "bold"),
                fg=BRANCO,
                bg="#261044",
                anchor="w"
            ).pack(fill="x", padx=8, pady=(4, 0))

            if item.get("detalhes"):
                tk.Label(
                    f_pedidos,
                    text=f"  ({item['detalhes']})",
                    font=("Arial", 7),
                    fg=CINZA,
                    bg="#261044",
                    anchor="w"
                ).pack(fill="x", padx=8)

        tk.Label(
            f_pedidos,
            text=f"Subtotal: R$ {subtotal:.2f}",
            font=("Arial", 10, "bold"),
            fg=AMARELO,
            bg="#261044"
        ).pack(pady=8)

        tk.Button(
            f_pedidos,
            text="Finalizar Pedido",
            font=("Arial", 9, "bold"),
            bg=VERDE,
            fg=BRANCO,
            relief="flat",
            cursor="hand2",
            command=mostrar_checkout
        ).pack(fill="x", padx=10, pady=(0, 10))

    else:
        tk.Label(
            f_pedidos,
            text="Nenhum item selecionado",
            font=("Arial", 9),
            fg=CINZA,
            bg="#261044"
        ).pack(pady=15)


def deslogar_cliente():
    global cliente_logado, desconto_fidelidade

    cliente_logado = None
    desconto_fidelidade = 0.0
    atualizar_painel_direito()

    messagebox.showinfo("Açaízon", "Sessão encerrada.")


def abrir_modal_cadastro():
    win = tk.Toplevel(janela)
    win.title("Cadastro Açaízon")
    win.geometry("400x520")
    win.configure(bg=ROXO_ESCURO)

    tk.Label(
        win,
        text="Novo Cadastro",
        font=("Arial", 14, "bold"),
        fg=BRANCO,
        bg=ROXO_ESCURO
    ).pack(pady=10)

    campos = [
        ("Nome:", "nome"),
        ("Apelido:", "apelido"),
        ("E-mail:", "email"),
        ("Telefone:", "telefone"),
        ("Endereço:", "endereco"),
        ("Idade:", "idade"),
        ("CPF:", "cpf")
    ]

    entries = {}

    for label, key in campos:
        f = tk.Frame(win, bg=ROXO_ESCURO)
        f.pack(fill="x", padx=20, pady=2)

        tk.Label(
            f,
            text=label,
            font=("Arial", 8, "bold"),
            fg=CINZA,
            bg=ROXO_ESCURO,
            width=12,
            anchor="w"
        ).pack(side="left")

        e = tk.Entry(f)
        e.pack(side="right", fill="x", expand=True)
        entries[key] = e

    foto_path_var = tk.StringVar(value="")

    def tirar_foto():
        cpf_val = entries["cpf"].get().strip()

        if not cpf_val:
            messagebox.showwarning(
                "Atenção",
                "Preencha o CPF antes do Face ID."
            )
            return

        sucesso, res = capturar_foto_cadastro(cpf_val)

        if sucesso:
            foto_path_var.set(res)
            messagebox.showinfo(
                "Face ID",
                "Foto capturada com sucesso!"
            )
        else:
            messagebox.showerror("Erro", res)

    tk.Button(
        win,
        text="📷 Capturar Face ID (Câmera)",
        font=("Arial", 9, "bold"),
        bg=ROXO_MEDIO,
        fg=BRANCO,
        command=tirar_foto
    ).pack(pady=10)

    def salvar():
        global cliente_logado

        nome = entries["nome"].get().strip()
        cpf = entries["cpf"].get().strip()

        if not nome or not cpf:
            messagebox.showwarning(
                "Atenção",
                "Preencha pelo menos Nome e CPF."
            )
            return

        ok, cid = cadastrar_cliente(
            nome,
            cpf,
            entries["telefone"].get().strip(),
            foto_path_var.get(),
            entries["apelido"].get().strip(),
            entries["email"].get().strip(),
            entries["endereco"].get().strip(),
            entries["idade"].get().strip()
        )

        if ok:
            cliente_logado = {
                "id": cid,
                "nome": nome,
                "apelido": entries["apelido"].get().strip(),
                "email": entries["email"].get().strip(),
                "cpf": cpf,
                "telefone": entries["telefone"].get().strip(),
                "endereco": entries["endereco"].get().strip(),
                "pontos": 50
            }

            atualizar_painel_direito()
            win.destroy()

            messagebox.showinfo(
                "Sucesso",
                "Cliente cadastrado com sucesso!"
            )
        else:
            messagebox.showerror("Erro", str(cid))

    tk.Button(
        win,
        text="Salvar Cadastro",
        font=("Arial", 10, "bold"),
        bg=AMARELO,
        fg="#3B2600",
        command=salvar
    ).pack(pady=10)


def abrir_modal_personalizar(produto):
    win = tk.Toplevel(janela)
    win.title(f"Personalizar {produto['nome']}")
    win.geometry("420x550")
    win.configure(bg=ROXO_ESCURO)

    tk.Label(
        win,
        text=f"{produto['emoji']} {produto['nome']}",
        font=("Arial", 14, "bold"),
        fg=BRANCO,
        bg=ROXO_ESCURO
    ).pack(pady=10)

    tk.Label(
        win,
        text="1. Escolha o Tamanho:",
        font=("Arial", 10, "bold"),
        fg=AMARELO,
        bg=ROXO_ESCURO
    ).pack(anchor="w", padx=20, pady=(5, 2))

    tamanho_var = tk.StringVar(value="500ml")

    f_tamanhos = tk.Frame(win, bg=ROXO_ESCURO)
    f_tamanhos.pack(fill="x", padx=20)

    r1 = tk.Radiobutton(
        f_tamanhos,
        text=f"300ml (R$ {produto['preco_300ml']:.2f})",
        variable=tamanho_var,
        value="300ml",
        bg=ROXO_ESCURO,
        fg=BRANCO,
        selectcolor="#21103D",
        activebackground=ROXO_ESCURO
    )

    r2 = tk.Radiobutton(
        f_tamanhos,
        text=f"500ml (R$ {produto['preco_500ml']:.2f})",
        variable=tamanho_var,
        value="500ml",
        bg=ROXO_ESCURO,
        fg=BRANCO,
        selectcolor="#21103D",
        activebackground=ROXO_ESCURO
    )

    r3 = tk.Radiobutton(
        f_tamanhos,
        text=f"700ml (R$ {produto['preco_700ml']:.2f})",
        variable=tamanho_var,
        value="700ml",
        bg=ROXO_ESCURO,
        fg=BRANCO,
        selectcolor="#21103D",
        activebackground=ROXO_ESCURO
    )

    r1.pack(anchor="w")
    r2.pack(anchor="w")
    r3.pack(anchor="w")

    tk.Label(
        win,
        text="2. Escolha os Acompanhamentos:",
        font=("Arial", 10, "bold"),
        fg=AMARELO,
        bg=ROXO_ESCURO
    ).pack(anchor="w", padx=20, pady=(15, 2))

    f_toppings = tk.Frame(
        win,
        bg="#21103D",
        highlightbackground=ROXO_MEDIO,
        highlightthickness=1
    )
    f_toppings.pack(fill="both", expand=True, padx=20, pady=5)

    checks = {}

    for top in ACOMPANHAMENTOS:
        var = tk.BooleanVar()

        cb = tk.Checkbutton(
            f_toppings,
            text=top,
            variable=var,
            bg="#21103D",
            fg=BRANCO,
            selectcolor=ROXO_ESCURO,
            activebackground="#21103D"
        )

        cb.pack(anchor="w", padx=10, pady=1)
        checks[top] = var

    def adicionar_personalizado():
        tam = tamanho_var.get()
        preco_base = produto[f'preco_{tam}']

        selecionados = [
            top for top, var in checks.items()
            if var.get()
        ]

        detalhes_str = (
            f"{tam} | " +
            (", ".join(selecionados)
             if selecionados
             else "Sem acompanhamentos")
        )

        carrinho.append({
            "nome": f"{produto['nome']} ({tam})",
            "tamanho": tam,
            "toppings": (
                ", ".join(selecionados)
                if selecionados
                else "Nenhum"
            ),
            "detalhes": detalhes_str,
            "preco": preco_base
        })

        atualizar_painel_direito()
        win.destroy()

        messagebox.showinfo(
            "Açaízon",
            "Seu açaí personalizado foi adicionado ao carrinho!"
        )

    tk.Button(
        win,
        text="Adicionar ao Carrinho 🛒",
        font=("Arial", 11, "bold"),
        bg=ROSA,
        fg=BRANCO,
        relief="flat",
        cursor="hand2",
        command=adicionar_personalizado
    ).pack(pady=15)


def mostrar_inicio():
    limpar_conteudo()

    tk.Label(
        area_conteudo,
        text="Bem-vindo ao Açaízon!",
        font=("Arial", 24, "bold"),
        fg=BRANCO,
        bg=ROXO_ESCURO
    ).pack(pady=(35, 10))

    tk.Label(
        area_conteudo,
        text="Mais que açaí, uma energia pra você!",
        font=("Arial", 12),
        fg=CINZA,
        bg=ROXO_ESCURO
    ).pack()


def adicionar_direto_ao_carrinho(produto, tamanho="500ml"):
    preco = produto[f'preco_{tamanho}']

    carrinho.append({
        "nome": produto["nome"],
        "tamanho": tamanho,
        "toppings": "Receita Padrão",
        "detalhes": f"{tamanho} | Padrão da Casa",
        "preco": preco
    })

    atualizar_painel_direito()

    messagebox.showinfo(
        "Açaízon",
        f"{produto['nome']} ({tamanho}) adicionado ao carrinho!"
    )


def mostrar_cardapio():
    limpar_conteudo()

    tk.Label(
        area_conteudo,
        text="🥣 Nosso Cardápio Especial",
        font=("Arial", 20, "bold"),
        fg=BRANCO,
        bg=ROXO_ESCURO
    ).pack(anchor="w", padx=20, pady=10)

    for prod in PRODUTOS:
        card = tk.Frame(
            area_conteudo,
            bg="#21103D",
            highlightbackground=ROXO_MEDIO,
            highlightthickness=1
        )
        card.pack(fill="x", padx=20, pady=8)

        tk.Label(
            card,
            text=prod["emoji"],
            font=("Arial", 24),
            bg="#21103D"
        ).pack(side="left", padx=15)

        info_frame = tk.Frame(card, bg="#21103D")
        info_frame.pack(
            side="left",
            fill="both",
            expand=True,
            pady=10
        )

        tk.Label(
            info_frame,
            text=prod["nome"],
            font=("Arial", 12, "bold"),
            fg=AMARELO,
            bg="#21103D"
        ).pack(anchor="w")

        tk.Label(
            info_frame,
            text=prod["descricao"],
            font=("Arial", 9),
            fg=CINZA,
            bg="#21103D",
            wraplength=450,
            justify="left"
        ).pack(anchor="w")

        tk.Label(
            info_frame,
            text=f"A partir de R$ {prod['preco_300ml']:.2f}",
            font=("Arial", 10, "bold"),
            fg=BRANCO,
            bg="#21103D"
        ).pack(anchor="w", pady=(2, 0))

        if prod["id"] == 1:
            tk.Button(
                card,
                text="🛠️ Personalizar e Pedir",
                font=("Arial", 9, "bold"),
                bg=ROSA,
                fg=BRANCO,
                relief="flat",
                cursor="hand2",
                command=lambda p=prod: abrir_modal_personalizar(p)
            ).pack(side="right", padx=15, pady=15)
        else:
            tk.Button(
                card,
                text="🛒 Adicionar (500ml)",
                font=("Arial", 9, "bold"),
                bg=VERDE,
                fg=BRANCO,
                relief="flat",
                cursor="hand2",
                command=lambda p=prod: adicionar_direto_ao_carrinho(
                    p,
                    "500ml"
                )
            ).pack(side="right", padx=15, pady=15)


def mostrar_fidelidade():
    limpar_conteudo()

    tk.Label(
        area_conteudo,
        text="💜 Clube Delírio Roxo",
        font=("Arial", 20, "bold"),
        fg=BRANCO,
        bg=ROXO_ESCURO
    ).pack(anchor="w", padx=20, pady=10)

    box = tk.Frame(
        area_conteudo,
        bg="#21103D",
        highlightbackground=ROSA,
        highlightthickness=2
    )
    box.pack(fill="both", expand=True, padx=20, pady=10)

    tk.Label(
        box,
        text="Seu Açaí vale mais!",
        font=("Arial", 16, "bold"),
        fg=AMARELO,
        bg="#21103D"
    ).pack(pady=(20, 5))

    txt = (
        "Quer aproveitar descontos incríveis e cashback nas suas compras?\n"
        "Faça parte do Delírio Roxo!"
    )

    tk.Label(
        box,
        text=txt,
        font=("Arial", 11),
        fg=BRANCO,
        bg="#21103D",
        justify="center"
    ).pack(pady=10)

    def resgatar():
        global desconto_fidelidade

        desconto_fidelidade = 0.10
        atualizar_painel_direito()

        messagebox.showinfo(
            "🎉 Clube Delírio Roxo",
            "Parabéns! Você ativou seu cupom de 10% de desconto no pedido!"
        )

    tk.Button(
        box,
        text="🎁 Entrar no Clube e Ganhar 10% OFF",
        font=("Arial", 11, "bold"),
        bg=ROSA,
        fg=BRANCO,
        relief="flat",
        cursor="hand2",
        command=resgatar
    ).pack(pady=20, ipadx=10, ipady=5)


def mostrar_checkout():
    limpar_conteudo()

    tk.Label(
        area_conteudo,
        text="🛒 Finalizar Pedido",
        font=("Arial", 20, "bold"),
        fg=BRANCO,
        bg=ROXO_ESCURO
    ).pack(anchor="w", padx=20, pady=10)

    if not carrinho:
        tk.Label(
            area_conteudo,
            text="Seu carrinho está vazio!",
            font=("Arial", 12),
            fg=CINZA,
            bg=ROXO_ESCURO
        ).pack(pady=30)
        return

    subtotal = sum(i['preco'] for i in carrinho)
    valor_desconto = subtotal * desconto_fidelidade
    taxa_entrega = 5.00
    total = (subtotal - valor_desconto) + taxa_entrega

    f_checkout = tk.Frame(
        area_conteudo,
        bg="#21103D",
        highlightbackground=ROXO_MEDIO,
        highlightthickness=1
    )
    f_checkout.pack(fill="both", expand=True, padx=20, pady=10)

    tk.Label(
        f_checkout,
        text="Forma de Pagamento:",
        font=("Arial", 11, "bold"),
        fg=AMARELO,
        bg="#21103D"
    ).pack(anchor="w", padx=20, pady=(15, 5))

    pag_var = tk.StringVar(value="Pix")

    for opt in ["Débito", "Pix", "Crédito", "Boleto", "VR"]:
        tk.Radiobutton(
            f_checkout,
            text=opt,
            variable=pag_var,
            value=opt,
            bg="#21103D",
            fg=BRANCO,
            selectcolor=ROXO_ESCURO,
            activebackground="#21103D"
        ).pack(anchor="w", padx=30)

    tk.Label(
        f_checkout,
        text="Opção de Entrega:",
        font=("Arial", 11, "bold"),
        fg=AMARELO,
        bg="#21103D"
    ).pack(anchor="w", padx=20, pady=(15, 5))

    entrega_var = tk.StringVar(value="Delivery")

    for opt in ["Retirar na loja", "Delivery"]:
        tk.Radiobutton(
            f_checkout,
            text=opt,
            variable=entrega_var,
            value=opt,
            bg="#21103D",
            fg=BRANCO,
            selectcolor=ROXO_ESCURO,
            activebackground="#21103D"
        ).pack(anchor="w", padx=30)

    resumo = (
        f"Subtotal: R$ {subtotal:.2f} | "
        f"Desconto: R$ {valor_desconto:.2f} | "
        f"Total: R$ {total:.2f}"
    )

    tk.Label(
        f_checkout,
        text=resumo,
        font=("Arial", 11, "bold"),
        fg=VERDE,
        bg="#21103D"
    ).pack(pady=15)

    def concluir():
        pedido_id = None

        if cliente_logado:
            # O banco atual possui estrutura de pedidos por item principal.
            item = carrinho[0]

            resultado = salvar_pedido(
                cliente_logado["id"],
                item.get("tamanho", "500ml"),
                item.get("toppings", "Padrão"),
                pag_var.get(),
                entrega_var.get(),
                subtotal,
                taxa_entrega,
                total
            )

            if isinstance(resultado, tuple):
                _, pedido_id = resultado
            else:
                # Compatibilidade com versões antigas do db.py.
                pedido_id = None

        mostrar_comprovante_e_status(
            pag_var.get(),
            entrega_var.get(),
            subtotal,
            taxa_entrega,
            total,
            pedido_id
        )

    tk.Button(
        f_checkout,
        text="Confirmar Pedido 🚀",
        font=("Arial", 12, "bold"),
        bg=VERDE,
        fg=BRANCO,
        relief="flat",
        cursor="hand2",
        command=concluir
    ).pack(pady=15)


def montar_dados_comprovante(
    pagamento,
    entrega,
    subtotal,
    taxa,
    total,
    pedido_id=None
):
    nome_c = (
        cliente_logado.get("nome", "Cliente")
        if cliente_logado
        else "Cliente Visitante"
    )

    end_c = (
        cliente_logado.get("endereco", "Balcão / Retirada")
        if cliente_logado
        else "Não informado"
    )

    tel_c = (
        cliente_logado.get("telefone", "-")
        if cliente_logado
        else "-"
    )

    hora = datetime.datetime.now().strftime(
        "%H:%M:%S - %d/%m/%Y"
    )

    itens = []

    for item in carrinho:
        itens.append({
            "nome": item.get("nome"),
            "tamanho": item.get("tamanho"),
            "toppings": item.get("toppings"),
            "detalhes": item.get("detalhes"),
            "preco": item.get("preco")
        })

    return {
        "sistema": "Açaízon",
        "pedido_id": pedido_id,
        "cliente": {
            "id": cliente_logado.get("id") if cliente_logado else None,
            "nome": nome_c,
            "cpf": cliente_logado.get("cpf") if cliente_logado else None,
            "telefone": tel_c,
            "endereco": end_c
        },
        "data_hora": hora,
        "itens": itens,
        "valores": {
            "subtotal": subtotal,
            "taxa_entrega": taxa,
            "total": total
        },
        "pagamento": pagamento,
        "opcao_entrega": entrega,
        "status": "Em preparação",
        "tempo_estimado": "30-40 min"
    }


def mostrar_comprovante_e_status(
    pagamento,
    entrega,
    subtotal,
    taxa,
    total,
    pedido_id=None
):
    limpar_conteudo()

    tk.Label(
        area_conteudo,
        text="🧾 Comprovante do Pedido & Status",
        font=("Arial", 18, "bold"),
        fg=BRANCO,
        bg=ROXO_ESCURO
    ).pack(anchor="w", padx=20, pady=10)

    card = tk.Frame(
        area_conteudo,
        bg="#21103D",
        highlightbackground=VERDE,
        highlightthickness=1
    )
    card.pack(fill="both", expand=True, padx=20, pady=5)

    dados = montar_dados_comprovante(
        pagamento,
        entrega,
        subtotal,
        taxa,
        total,
        pedido_id
    )

    nome_c = dados["cliente"]["nome"]
    end_c = dados["cliente"]["endereco"]
    tel_c = dados["cliente"]["telefone"]
    hora = dados["data_hora"]

    itens_str = "\n".join([
        f"• {i['nome']} ({i.get('detalhes', 'Padrão')})"
        for i in dados["itens"]
    ])

    comp_txt = (
        f"--- COMPROVANTE AÇAÍZON ---\n"
        f"Pedido: {pedido_id or 'Não registrado'}\n"
        f"Cliente: {nome_c}\n"
        f"Endereço: {end_c}\n"
        f"Telefone: {tel_c}\n"
        f"Horário do Pedido: {hora}\n"
        f"----------------------------\n"
        f"Itens do Pedido:\n{itens_str}\n"
        f"----------------------------\n"
        f"Subtotal: R$ {subtotal:.2f}\n"
        f"Taxa de Entrega: R$ {taxa:.2f}\n"
        f"Total do Pedido: R$ {total:.2f}\n"
        f"Pagamento: {pagamento} | Opção: {entrega}\n\n"
        f"🛵 Status da Entrega: Em preparação "
        f"(Tempo estimado: 30-40 min)"
    )

    tk.Label(
        card,
        text=comp_txt,
        font=("Courier", 9),
        fg=BRANCO,
        bg="#21103D",
        justify="left"
    ).pack(anchor="w", padx=15, pady=15)

    def exportar_comprovante():
        dados_exportacao = dict(dados)

        caminho = filedialog.asksaveasfilename(
            parent=janela,
            title="Exportar comprovante",
            defaultextension=".json",
            initialfile=(
                f"comprovante_pedido_"
                f"{pedido_id or 'novo'}.json"
            ),
            filetypes=[
                ("Arquivo JSON", "*.json"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if not caminho:
            return

        try:
            exportar_dados_json(
                dados_exportacao,
                caminho
            )

            messagebox.showinfo(
                "Exportação concluída",
                f"Comprovante exportado com sucesso:\n\n{caminho}"
            )

        except Exception as e:
            messagebox.showerror(
                "Erro na exportação",
                f"Não foi possível exportar o comprovante:\n{e}"
            )

    tk.Button(
        card,
        text="📄 Exportar Comprovante em JSON",
        font=("Arial", 10, "bold"),
        bg=ROXO_MEDIO,
        fg=BRANCO,
        relief="flat",
        cursor="hand2",
        command=exportar_comprovante
    ).pack(pady=(5, 10))

    def novo():
        carrinho.clear()
        atualizar_painel_direito()
        mostrar_inicio()

    tk.Button(
        card,
        text="Voltar ao Início",
        font=("Arial", 10, "bold"),
        bg=AMARELO,
        fg="#3B2600",
        command=novo
    ).pack(pady=10)


# ============================================================
# ROOT MASTER - FUNÇÕES
# ============================================================

def abrir_root_master():
    """Abre a tela de autenticação do administrador."""
    win = tk.Toplevel(janela)
    win.title("Root Master - Açaízon")
    win.geometry("420x330")
    win.configure(bg=ROXO_ESCURO)
    win.resizable(False, False)

    tk.Label(
        win,
        text="🔐 ROOT MASTER",
        font=("Arial", 18, "bold"),
        fg=AMARELO,
        bg=ROXO_ESCURO
    ).pack(pady=(30, 10))

    tk.Label(
        win,
        text="Acesso administrativo",
        font=("Arial", 10),
        fg=CINZA,
        bg=ROXO_ESCURO
    ).pack(pady=(0, 20))

    frame = tk.Frame(win, bg=ROXO_ESCURO)
    frame.pack(fill="x", padx=45)

    tk.Label(
        frame,
        text="Usuário:",
        font=("Arial", 9, "bold"),
        fg=BRANCO,
        bg=ROXO_ESCURO
    ).pack(anchor="w")

    usuario_entry = tk.Entry(frame, font=("Arial", 11))
    usuario_entry.pack(fill="x", pady=(3, 12))

    tk.Label(
        frame,
        text="Senha:",
        font=("Arial", 9, "bold"),
        fg=BRANCO,
        bg=ROXO_ESCURO
    ).pack(anchor="w")

    senha_entry = tk.Entry(
        frame,
        font=("Arial", 11),
        show="*"
    )
    senha_entry.pack(fill="x", pady=(3, 15))

    def autenticar():
        usuario = usuario_entry.get().strip()
        senha = senha_entry.get()

        if (
            usuario == ROOT_MASTER_USUARIO
            and senha == ROOT_MASTER_SENHA
        ):
            win.destroy()
            abrir_painel_root_master()
        else:
            messagebox.showerror(
                "Acesso negado",
                "Usuário ou senha do Root Master incorretos.",
                parent=win
            )

    tk.Button(
        win,
        text="Entrar no Painel",
        font=("Arial", 10, "bold"),
        bg=ROXO_MEDIO,
        fg=BRANCO,
        relief="flat",
        cursor="hand2",
        command=autenticar
    ).pack(fill="x", padx=45, pady=5)

    tk.Button(
        win,
        text="Cancelar",
        font=("Arial", 9),
        bg="#32134F",
        fg=BRANCO,
        relief="flat",
        command=win.destroy
    ).pack(fill="x", padx=45, pady=3)

    usuario_entry.focus_set()
    senha_entry.bind("<Return>", lambda event: autenticar())


def abrir_painel_root_master():
    """Painel administrativo para clientes, pedidos e exportações."""
    win = tk.Toplevel(janela)
    win.title("Açaízon - Root Master")
    win.geometry("1100x650")
    win.configure(bg=ROXO_ESCURO)

    tk.Label(
        win,
        text="👑 ROOT MASTER | Painel Administrativo",
        font=("Arial", 18, "bold"),
        fg=AMARELO,
        bg=ROXO_ESCURO
    ).pack(anchor="w", padx=20, pady=(18, 5))

    tk.Label(
        win,
        text="Gerenciamento e exportação de clientes e pedidos",
        font=("Arial", 9),
        fg=CINZA,
        bg=ROXO_ESCURO
    ).pack(anchor="w", padx=20, pady=(0, 12))

    abas = ttk.Notebook(win)
    abas.pack(fill="both", expand=True, padx=15, pady=10)

    aba_clientes = tk.Frame(abas, bg=ROXO_ESCURO)
    aba_pedidos = tk.Frame(abas, bg=ROXO_ESCURO)

    abas.add(aba_clientes, text="👥 Clientes")
    abas.add(aba_pedidos, text="🧾 Pedidos")

    # ---------------- CLIENTES ----------------
    topo_clientes = tk.Frame(aba_clientes, bg=ROXO_ESCURO)
    topo_clientes.pack(fill="x", pady=8)

    tree_clientes = ttk.Treeview(
        aba_clientes,
        columns=(
            "id",
            "nome",
            "cpf",
            "telefone",
            "email",
            "pontos"
        ),
        show="headings",
        height=17
    )

    configuracao_clientes = {
        "id": ("ID", 60),
        "nome": ("Nome", 180),
        "cpf": ("CPF", 140),
        "telefone": ("Telefone", 120),
        "email": ("E-mail", 220),
        "pontos": ("Pontos", 80)
    }

    for coluna, (titulo, largura) in configuracao_clientes.items():
        tree_clientes.heading(coluna, text=titulo)
        tree_clientes.column(
            coluna,
            width=largura,
            anchor="center"
        )

    tree_clientes.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=5
    )

    def carregar_clientes_tree():
        for item in tree_clientes.get_children():
            tree_clientes.delete(item)

        try:
            clientes = listar_clientes()

            for cliente in clientes:
                tree_clientes.insert(
                    "",
                    "end",
                    iid=str(cliente["id"]),
                    values=(
                        cliente["id"],
                        cliente["nome"],
                        cliente["cpf"],
                        cliente["telefone"] or "-",
                        cliente["email"] or "-",
                        cliente["pontos_fidelidade"]
                    )
                )

        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Não foi possível carregar os clientes:\n{e}",
                parent=win
            )

    def exportar_cliente_selecionado():
        selecionado = tree_clientes.selection()

        if not selecionado:
            messagebox.showwarning(
                "Atenção",
                "Selecione um cliente na tabela.",
                parent=win
            )
            return

        cliente_id = int(selecionado[0])
        cliente = buscar_cliente_por_id(cliente_id)

        if not cliente:
            messagebox.showerror(
                "Erro",
                "Cliente não encontrado.",
                parent=win
            )
            return

        caminho = filedialog.asksaveasfilename(
            parent=win,
            title="Exportar cliente",
            defaultextension=".json",
            initialfile=f"cliente_{cliente_id}.json",
            filetypes=[
                ("Arquivo JSON", "*.json"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if not caminho:
            return

        try:
            exportar_dados_json(cliente, caminho)

            messagebox.showinfo(
                "Exportação concluída",
                f"Cliente exportado com sucesso:\n\n{caminho}",
                parent=win
            )

        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Não foi possível exportar:\n{e}",
                parent=win
            )

    def exportar_todos_clientes():
        clientes = listar_clientes()

        if not clientes:
            messagebox.showinfo(
                "Clientes",
                "Não existem clientes cadastrados.",
                parent=win
            )
            return

        caminho = filedialog.asksaveasfilename(
            parent=win,
            title="Exportar todos os clientes",
            defaultextension=".json",
            initialfile="clientes_acai_zon.json",
            filetypes=[
                ("Arquivo JSON", "*.json"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if not caminho:
            return

        try:
            exportar_dados_json(clientes, caminho)

            messagebox.showinfo(
                "Exportação concluída",
                f"{len(clientes)} cliente(s) exportado(s):\n\n{caminho}",
                parent=win
            )

        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Não foi possível exportar:\n{e}",
                parent=win
            )

    tk.Button(
        topo_clientes,
        text="🔄 Atualizar",
        font=("Arial", 9, "bold"),
        bg="#32134F",
        fg=BRANCO,
        relief="flat",
        command=carregar_clientes_tree
    ).pack(side="left", padx=5)

    tk.Button(
        topo_clientes,
        text="📄 Exportar Cliente Selecionado",
        font=("Arial", 9, "bold"),
        bg=ROXO_MEDIO,
        fg=BRANCO,
        relief="flat",
        command=exportar_cliente_selecionado
    ).pack(side="left", padx=5)

    tk.Button(
        topo_clientes,
        text="📦 Exportar Todos em JSON",
        font=("Arial", 9, "bold"),
        bg=VERDE,
        fg=BRANCO,
        relief="flat",
        command=exportar_todos_clientes
    ).pack(side="left", padx=5)

    # ---------------- PEDIDOS ----------------
    topo_pedidos = tk.Frame(aba_pedidos, bg=ROXO_ESCURO)
    topo_pedidos.pack(fill="x", pady=8)

    tree_pedidos = ttk.Treeview(
        aba_pedidos,
        columns=(
            "id",
            "cliente",
            "tamanho",
            "pagamento",
            "entrega",
            "total",
            "data"
        ),
        show="headings",
        height=17
    )

    configuracao_pedidos = {
        "id": ("Pedido", 70),
        "cliente": ("Cliente", 180),
        "tamanho": ("Tamanho", 100),
        "pagamento": ("Pagamento", 110),
        "entrega": ("Entrega", 120),
        "total": ("Total", 100),
        "data": ("Data/Hora", 160)
    }

    for coluna, (titulo, largura) in configuracao_pedidos.items():
        tree_pedidos.heading(coluna, text=titulo)
        tree_pedidos.column(
            coluna,
            width=largura,
            anchor="center"
        )

    tree_pedidos.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=5
    )

    def carregar_pedidos_tree():
        for item in tree_pedidos.get_children():
            tree_pedidos.delete(item)

        try:
            pedidos = listar_pedidos()

            for pedido in pedidos:
                tree_pedidos.insert(
                    "",
                    "end",
                    iid=str(pedido["id"]),
                    values=(
                        pedido["id"],
                        pedido["cliente_nome"],
                        pedido["tamanho"],
                        pedido["forma_pagamento"],
                        pedido["opcao_entrega"],
                        f"R$ {pedido['total']:.2f}",
                        pedido["data_hora"]
                    )
                )

        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Não foi possível carregar os pedidos:\n{e}",
                parent=win
            )

    def exportar_pedido_selecionado():
        selecionado = tree_pedidos.selection()

        if not selecionado:
            messagebox.showwarning(
                "Atenção",
                "Selecione um pedido na tabela.",
                parent=win
            )
            return

        pedido_id = int(selecionado[0])
        pedido = buscar_pedido_por_id(pedido_id)

        if not pedido:
            messagebox.showerror(
                "Erro",
                "Pedido não encontrado.",
                parent=win
            )
            return

        caminho = filedialog.asksaveasfilename(
            parent=win,
            title="Exportar pedido",
            defaultextension=".json",
            initialfile=f"comprovante_pedido_{pedido_id}.json",
            filetypes=[
                ("Arquivo JSON", "*.json"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if not caminho:
            return

        try:
            exportar_dados_json(pedido, caminho)

            messagebox.showinfo(
                "Exportação concluída",
                f"Comprovante do pedido exportado:\n\n{caminho}",
                parent=win
            )

        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Não foi possível exportar:\n{e}",
                parent=win
            )

    def exportar_todos_pedidos():
        pedidos = listar_pedidos()

        if not pedidos:
            messagebox.showinfo(
                "Pedidos",
                "Não existem pedidos registrados.",
                parent=win
            )
            return

        caminho = filedialog.asksaveasfilename(
            parent=win,
            title="Exportar todos os pedidos",
            defaultextension=".json",
            initialfile="pedidos_acai_zon.json",
            filetypes=[
                ("Arquivo JSON", "*.json"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if not caminho:
            return

        try:
            exportar_dados_json(pedidos, caminho)

            messagebox.showinfo(
                "Exportação concluída",
                f"{len(pedidos)} pedido(s) exportado(s):\n\n{caminho}",
                parent=win
            )

        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Não foi possível exportar:\n{e}",
                parent=win
            )

    tk.Button(
        topo_pedidos,
        text="🔄 Atualizar",
        font=("Arial", 9, "bold"),
        bg="#32134F",
        fg=BRANCO,
        relief="flat",
        command=carregar_pedidos_tree
    ).pack(side="left", padx=5)

    tk.Button(
        topo_pedidos,
        text="📄 Exportar Comprovante",
        font=("Arial", 9, "bold"),
        bg=ROXO_MEDIO,
        fg=BRANCO,
        relief="flat",
        command=exportar_pedido_selecionado
    ).pack(side="left", padx=5)

    tk.Button(
        topo_pedidos,
        text="📦 Exportar Todos em JSON",
        font=("Arial", 9, "bold"),
        bg=VERDE,
        fg=BRANCO,
        relief="flat",
        command=exportar_todos_pedidos
    ).pack(side="left", padx=5)

    # Duplo clique abre os dados completos do registro.
    def mostrar_cliente_detalhes(event=None):
        selecionado = tree_clientes.selection()

        if not selecionado:
            return

        cliente = buscar_cliente_por_id(int(selecionado[0]))

        if not cliente:
            return

        texto = json.dumps(
            cliente,
            ensure_ascii=False,
            indent=4
        )

        messagebox.showinfo(
            "Dados do Cliente",
            texto,
            parent=win
        )

    def mostrar_pedido_detalhes(event=None):
        selecionado = tree_pedidos.selection()

        if not selecionado:
            return

        pedido = buscar_pedido_por_id(int(selecionado[0]))

        if not pedido:
            return

        texto = json.dumps(
            pedido,
            ensure_ascii=False,
            indent=4
        )

        messagebox.showinfo(
            "Dados do Pedido",
            texto,
            parent=win
        )

    tree_clientes.bind(
        "<Double-1>",
        mostrar_cliente_detalhes
    )

    tree_pedidos.bind(
        "<Double-1>",
        mostrar_pedido_detalhes
    )

    carregar_clientes_tree()
    carregar_pedidos_tree()

cabecalho = tk.Frame(
    janela,
    bg="#3A075C",
    height=140
)
cabecalho.pack(side="top", fill="x")

conteudo_cabecalho = tk.Frame(
    cabecalho,
    bg="#3A075C"
)
conteudo_cabecalho.place(
    relx=0.5,
    rely=0.5,
    anchor="center"
)

imagem_logo_carregada = carregar_logo()

if imagem_logo_carregada:
    lbl_logo_img = tk.Label(
        conteudo_cabecalho,
        image=imagem_logo_carregada,
        bg="#3A075C",
        bd=0,
        highlightthickness=0
    )
    lbl_logo_img.image = imagem_logo_carregada
    lbl_logo_img.pack(side="left", padx=10)

corpo = tk.Frame(
    janela,
    bg=ROXO_ESCURO
)
corpo.pack(fill="both", expand=True)

menu_lateral = tk.Frame(
    corpo,
    bg="#21103D",
    width=200
)
menu_lateral.pack(
    side="left",
    fill="y",
    padx=5,
    pady=5
)

botao_inicio = tk.Button(
    menu_lateral,
    text="🏠 Início",
    font=("Arial", 11, "bold"),
    bg="#32134F",
    fg=BRANCO,
    anchor="w",
    relief="flat",
    command=mostrar_inicio
)
botao_inicio.pack(fill="x", padx=10, pady=5)

tk.Button(
    menu_lateral,
    text="🥣 Cardápio",
    font=("Arial", 11, "bold"),
    bg="#32134F",
    fg=BRANCO,
    anchor="w",
    relief="flat",
    command=mostrar_cardapio
).pack(fill="x", padx=10, pady=5)

tk.Button(
    menu_lateral,
    text="💜 Clube Delírio Roxo",
    font=("Arial", 11, "bold"),
    bg="#32134F",
    fg=AMARELO,
    anchor="w",
    relief="flat",
    command=mostrar_fidelidade
).pack(fill="x", padx=10, pady=5)

# Novo acesso administrativo.
tk.Button(
    menu_lateral,
    text="👑 Root Master",
    font=("Arial", 11, "bold"),
    bg="#4A176A",
    fg=AMARELO,
    anchor="w",
    relief="flat",
    cursor="hand2",
    command=abrir_root_master
).pack(fill="x", padx=10, pady=(20, 5))

area_conteudo = tk.Frame(
    corpo,
    bg=ROXO_ESCURO
)
area_conteudo.pack(
    side="left",
    fill="both",
    expand=True,
    padx=5,
    pady=5
)

painel_direito = tk.Frame(
    corpo,
    bg="#21103D",
    width=280
)
painel_direito.pack(
    side="right",
    fill="y",
    padx=5,
    pady=5
)

main_ref = None


def iniciar_aplicacao():
    atualizar_painel_direito()
    mostrar_inicio()
    janela.mainloop()


if __name__ == "__main__":
    iniciar_aplicacao()