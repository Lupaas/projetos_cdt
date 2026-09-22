import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Importações com fallback de segurança para o Banco de Dados
try:
    from database.db import cadastrar_cliente, buscar_cliente_por_id, buscar_ultimo_pedido, salvar_pedido
except ImportError:
    def cadastrar_cliente(nome, apelido, email, telefone, endereco, idade, cpf, face_encoding=None):
        return True, 1
    def buscar_cliente_por_id(cliente_id):
        return (1, "Cliente Exemplo", "Exemplo", "cliente@email.com", "11999999999", "Rua Açaí, 123", 20, "123.456.789-00", 120)
    def buscar_ultimo_pedido(cliente_id):
        return ("Açaí Tradicional 500ml", "Granola, Leite em Pó", "Pix", "Entrega")
    def salvar_pedido(cliente_id, tamanho, toppings, forma_pagamento, opcao_entrega, subtotal, taxa_entrega, total):
        return True

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

# Estado Global do Sistema
cliente_logado = None  # Dicionário com informações do cliente
carrinho = []          # Lista de itens adicionados ao pedido atual
logo_cardapio = None

# ============================================================
# JANELA PRINCIPAL
# ============================================================
janela = tk.Tk()
janela.title("Açaízon - Sistema PDV")
janela.geometry(f"{LARGURA}x{ALTURA}")
janela.minsize(1000, 600)
janela.configure(bg=ROXO_ESCURO)

# ============================================================
# FUNÇÕES DE SUPORTE E NAVEGAÇÃO
# ============================================================
def limpar_conteudo():
    for widget in area_conteudo.winfo_children():
        widget.destroy()

def mascarar_dado(texto, visiveis=3):
    """Mascara dados sensíveis mantendo apenas alguns caracteres visíveis (ex: ***.456.***-**)."""
    if not texto or texto == "-":
        return "-"
    if len(texto) <= visiveis:
        return "*" * len(texto)
    return "*" * (len(texto) - visiveis) + texto[-visiveis:]

def atualizar_painel_direito():
    """Atualiza o painel lateral com Login/Máscara e Histórico de Pedidos em tempo real."""
    for widget in painel_direito.winfo_children():
        widget.destroy()

    titulo = tk.Label(painel_direito, text="👤 Painel do Cliente", font=("Arial", 11, "bold"), fg=BRANCO, bg="#21103D")
    titulo.pack(pady=(15, 10))

    if cliente_logado:
        # Informações do Cliente Logado (com Máscara)
        info_frame = tk.Frame(painel_direito, bg="#261044", highlightbackground=ROXO_MEDIO, highlightthickness=1)
        info_frame.pack(fill="x", padx=15, pady=5)

        nome = cliente_logado.get("nome", "Cliente")
        cpf_mascarado = mascarar_dado(cliente_logado.get("cpf", ""), visiveis=3)
        tel_mascarado = mascarar_dado(cliente_logado.get("telefone", ""), visiveis=4)
        pontos = cliente_logado.get("pontos", 120)

        tk.Label(info_frame, text=f"Olá, {nome}!", font=("Arial", 10, "bold"), fg=AMARELO, bg="#261044").pack(anchor="w", padx=10, pady=(8, 2))
        tk.Label(info_frame, text=f"CPF: ***.***.{cpf_mascarado}", font=("Arial", 8), fg=BRANCO, bg="#261044").pack(anchor="w", padx=10)
        tk.Label(info_frame, text=f"Tel: (**) *****-{tel_mascarado}", font=("Arial", 8), fg=BRANCO, bg="#261044").pack(anchor="w", padx=10)
        tk.Label(info_frame, text=f"Pontos: {pontos} pts 💜", font=("Arial", 9, "bold"), fg=ROSA_CLARO, bg="#261044").pack(anchor="w", padx=10, pady=(2, 8))

        btn_sair = tk.Button(
            painel_direito, text="Sair da Conta", font=("Arial", 9, "bold"), bg=ROSA, fg=BRANCO,
            relief="flat", cursor="hand2", command=deslogar_cliente
        )
        btn_sair.pack(fill="x", padx=15, pady=5)
    else:
        # Ações de Login / Cadastro Unificados
        lbl_msg = tk.Label(painel_direito, text="Identifique-se para acumular\npontos e agilizar o pedido!", font=("Arial", 8), fg=CINZA, bg="#21103D", justify="center")
        lbl_msg.pack(pady=5)

        btn_login = tk.Button(
            painel_direito, text="🔑 Entrar na sua Conta", font=("Arial", 9, "bold"), bg=ROXO_MEDIO, fg=BRANCO,
            relief="flat", cursor="hand2", command=abrir_modal_login
        )
        btn_login.pack(fill="x", padx=15, pady=3)

        btn_cad = tk.Button(
            painel_direito, text="👤 Cadastrar-se", font=("Arial", 9, "bold"), bg=AMARELO, fg="#3B2600",
            relief="flat", cursor="hand2", command=abrir_modal_cadastro
        )
        btn_cad.pack(fill="x", padx=15, pady=3)

    # Área de ÚLTIMOS PEDIDOS
    tk.Label(painel_direito, text="♻ Últimos Pedidos / Carrinho", font=("Arial", 10, "bold"), fg=VERDE, bg="#21103D").pack(anchor="w", padx=15, pady=(15, 5))

    frame_pedidos = tk.Frame(painel_direito, bg="#261044", highlightbackground=ROXO_MEDIO, highlightthickness=1)
    frame_pedidos.pack(fill="x", padx=15)

    if carrinho:
        total_carrinho = sum(item['preco'] for item in carrinho)
        for item in carrinho[-3:]:  # Exibe os últimos 3 itens
            tk.Label(frame_pedidos, text=f"• {item['nome']} (R$ {item['preco']:.2f})", font=("Arial", 8), fg=BRANCO, bg="#261044", anchor="w").pack(fill="x", padx=8, pady=2)
        
        tk.Label(frame_pedidos, text=f"Subtotal: R$ {total_carrinho:.2f}", font=("Arial", 9, "bold"), fg=AMARELO, bg="#261044").pack(pady=5)
        
        btn_checkout = tk.Button(
            frame_pedidos, text="🛒 Finalizar Pedido", font=("Arial", 9, "bold"), bg=VERDE, fg=BRANCO,
            relief="flat", cursor="hand2", command=mostrar_checkout
        )
        btn_checkout.pack(fill="x", padx=10, pady=5)
    else:
        tk.Label(frame_pedidos, text="Nenhum item no carrinho.", font=("Arial", 8), fg=CINZA, bg="#261044").pack(pady=12)

def deslogar_cliente():
    global cliente_logado
    cliente_logado = None
    atualizar_painel_direito()
    messagebox.showinfo("Açaízon", "Você saiu da sua conta.")

# ============================================================
# MODAIS DE CADASTRO E LOGIN MANUAL
# ============================================================
def abrir_modal_login():
    win = tk.Toplevel(janela)
    win.title("Entrar na Conta")
    win.geometry("350x250")
    win.configure(bg=ROXO_ESCURO)

    tk.Label(win, text="Login Delírio Roxo", font=("Arial", 14, "bold"), fg=BRANCO, bg=ROXO_ESCURO).pack(pady=15)
    
    tk.Label(win, text="Digite seu CPF ou Telefone:", font=("Arial", 10), fg=CINZA, bg=ROXO_ESCURO).pack(anchor="w", padx=25)
    ent_dado = tk.Entry(win, font=("Arial", 11))
    ent_dado.pack(fill="x", padx=25, pady=5)

    def efetuar_login():
        global cliente_logado
        dado = ent_dado.get().strip()
        if not dado:
            messagebox.showwarning("Atenção", "Preencha o campo de login.")
            return
        # Simulação do login
        cliente_logado = {
            "id": 1,
            "nome": "Cliente Açaízon",
            "cpf": dado,
            "telefone": dado,
            "pontos": 150
        }
        atualizar_painel_direito()
        win.destroy()
        messagebox.showinfo("Sucesso", "Login efetuado com sucesso!")

    tk.Button(win, text="Entrar", font=("Arial", 10, "bold"), bg=ROSA, fg=BRANCO, command=efetuar_login).pack(pady=15, ipadx=10)

def abrir_modal_cadastro():
    win = tk.Toplevel(janela)
    win.title("Cadastro de Cliente")
    win.geometry("350x320")
    win.configure(bg=ROXO_ESCURO)

    tk.Label(win, text="Novo Cadastro", font=("Arial", 14, "bold"), fg=BRANCO, bg=ROXO_ESCURO).pack(pady=10)

    tk.Label(win, text="Nome Completo:", font=("Arial", 9), fg=CINZA, bg=ROXO_ESCURO).pack(anchor="w", padx=25)
    ent_nome = tk.Entry(win)
    ent_nome.pack(fill="x", padx=25, pady=2)

    tk.Label(win, text="CPF:", font=("Arial", 9), fg=CINZA, bg=ROXO_ESCURO).pack(anchor="w", padx=25)
    ent_cpf = tk.Entry(win)
    ent_cpf.pack(fill="x", padx=25, pady=2)

    tk.Label(win, text="Telefone:", font=("Arial", 9), fg=CINZA, bg=ROXO_ESCURO).pack(anchor="w", padx=25)
    ent_tel = tk.Entry(win)
    ent_tel.pack(fill="x", padx=25, pady=2)

    def salvar():
        global cliente_logado
        if not ent_nome.get() or not ent_cpf.get():
            messagebox.showwarning("Atenção", "Preencha os campos obrigatórios.")
            return
        
        cadastrar_cliente(ent_nome.get(), "", "", ent_tel.get(), "", 0, ent_cpf.get())
        cliente_logado = {
            "id": 1,
            "nome": ent_nome.get(),
            "cpf": ent_cpf.get(),
            "telefone": ent_tel.get(),
            "pontos": 50  # Bônus de boas-vindas
        }
        atualizar_painel_direito()
        win.destroy()
        messagebox.showinfo("Sucesso", "Cadastro realizado com sucesso! Você ganhou 50 pontos de boas-vindas!")

    tk.Button(win, text="Finalizar Cadastro", font=("Arial", 10, "bold"), bg=AMARELO, fg="#3B2600", command=salvar).pack(pady=15)

# ============================================================
# TELAS DO MENU LATERAL ESQUERDO
# ============================================================
def mostrar_inicio():
    limpar_conteudo()

    tk.Label(area_conteudo, text="Bem-vindo ao Açaízon!", font=("Arial", 24, "bold"), fg=BRANCO, bg=ROXO_ESCURO).pack(pady=(30, 5))
    tk.Label(area_conteudo, text="Mais que açaí, uma energia pra você!", font=("Arial", 12), fg=CINZA, bg=ROXO_ESCURO).pack()

    caixa = tk.Frame(area_conteudo, bg="#21103D", highlightbackground=ROXO_MEDIO, highlightthickness=1)
    caixa.pack(fill="both", expand=True, padx=35, pady=20)

    tk.Label(caixa, text="📷", font=("Arial", 60), fg=AMARELO, bg="#21103D").pack(pady=(30, 10))
    tk.Label(caixa, text="Posicione seu rosto na câmera para iniciar\nou monte seu pedido no menu ao lado", font=("Arial", 13, "bold"), fg=BRANCO, bg="#21103D", justify="center").pack()

    tk.Button(
        caixa, text="Montar Pedido Agora", font=("Arial", 11, "bold"), bg=ROSA, fg=BRANCO,
        relief="flat", cursor="hand2", command=mostrar_cardapio
    ).pack(pady=20, ipadx=15, ipady=5)

def mostrar_cardapio():
    """Cardápio Completo: 'Monte o seu' + Categorias Prontas."""
    limpar_conteudo()

    tk.Label(area_conteudo, text="🥣 Cardápio Açaízon", font=("Arial", 22, "bold"), fg=BRANCO, bg=ROXO_ESCURO).pack(pady=10)

    # Criando Notebook para Categorias
    aba_parent = ttk.Notebook(area_conteudo)
    aba_parent.pack(fill="both", expand=True, padx=10, pady=5)

    # 1. ABA MONTE O SEU
    tab_custom = tk.Frame(aba_parent, bg="#21103D")
    aba_parent.add(tab_custom, text=" 🛠 Monte o Seu ")

    tk.Label(tab_custom, text="Escolha o Tamanho:", font=("Arial", 11, "bold"), fg=AMARELO, bg="#21103D").pack(anchor="w", padx=20, pady=(10, 2))
    var_tamanho = tk.StringVar(value="300ml - R$ 14,00")
    tamanhos = [("300ml - R$ 14,00", 14.0), ("500ml - R$ 18,00", 18.0), ("700ml - R$ 22,00", 22.0)]
    for text, price in tamanhos:
        tk.Radiobutton(tab_custom, text=text, variable=var_tamanho, value=text, bg="#21103D", fg=BRANCO, selectcolor=ROXO_MEDIO, activebackground="#21103D").pack(anchor="w", padx=35)

    tk.Label(tab_custom, text="Acompanhamentos (2 Grátis / Extras +R$ 3,00):", font=("Arial", 11, "bold"), fg=AMARELO, bg="#21103D").pack(anchor="w", padx=20, pady=(10, 2))
    opts_acomp = ["Granola", "Leite em Pó", "Leite Condensado", "Banana", "Morango", "Paçoca", "Nutella (+R$ 3.00)"]
    vars_acomp = {}
    for opt in opts_acomp:
        var = tk.BooleanVar()
        vars_acomp[opt] = var
        tk.Checkbutton(tab_custom, text=opt, variable=var, bg="#21103D", fg=BRANCO, selectcolor=ROXO_MEDIO, activebackground="#21103D").pack(anchor="w", padx=35)

    def add_custom():
        tam_str = var_tamanho.get()
        preco_base = float(tam_str.split("R$ ")[1].replace(",", "."))
        selecionados = [k for k, v in vars_acomp.items() if v.get()]
        
        # Regra: 2 grátis, adicionais somam R$ 3,00 cada
        extras = max(0, len(selecionados) - 2)
        preco_final = preco_base + (extras * 3.0)

        item = {
            "nome": f"Açaí Custom ({tam_str.split(' -')[0]})",
            "detalhes": ", ".join(selecionados) if selecionados else "Sem adicionais",
            "preco": preco_final
        }
        carrinho.append(item)
        atualizar_painel_direito()
        messagebox.showinfo("Açaízon", f"Açaí Personalizado adicionado! (Total: R$ {preco_final:.2f})")

    tk.Button(tab_custom, text="Adicionar Personalizado ao Carrinho", font=("Arial", 10, "bold"), bg=ROSA, fg=BRANCO, command=add_custom).pack(pady=15)

    # 2. ABAS DE CATEGORIAS PRONTAS
    categorias = {
        "🥤 Açaí Tradicional": [("Açaí Simples 300ml", 12.00), ("Açaí Tradicional 500ml", 16.00)],
        "🌟 Açaí Premium": [("Açaí com Morango & Nutella 500ml", 22.00), ("Açaí Supremo Banana & Paçoca 500ml", 20.00)],
        "👑 Açaí Especial": [("Tigelão da Casa 700ml completo", 26.00), ("Açaízon Power 1 Litro", 34.00)]
    }

    for cat_nome, itens in categorias.items():
        tab_cat = tk.Frame(aba_parent, bg="#21103D")
        aba_parent.add(tab_cat, text=f" {cat_nome} ")

        for nome, preco in itens:
            f = tk.Frame(tab_cat, bg="#261044", highlightbackground=ROXO_MEDIO, highlightthickness=1)
            f.pack(fill="x", padx=20, pady=8)

            tk.Label(f, text=nome, font=("Arial", 11, "bold"), fg=BRANCO, bg="#261044").pack(side="left", padx=15, pady=10)
            tk.Label(f, text=f"R$ {preco:.2f}", font=("Arial", 11, "bold"), fg=AMARELO, bg="#261044").pack(side="right", padx=15)

            def criar_cmd(n=nome, p=preco):
                return lambda: (carrinho.append({"nome": n, "detalhes": "Pronto", "preco": p}), atualizar_painel_direito(), messagebox.showinfo("Açaízon", f"{n} adicionado!"))

            tk.Button(f, text="Adicionar", font=("Arial", 9, "bold"), bg=ROSA, fg=BRANCO, command=criar_cmd()).pack(side="right", padx=5)

def mostrar_clube_delirio():
    """Aba 'Cliente' transformada em 'Clube Delírio Roxo'."""
    limpar_conteudo()

    tk.Label(area_conteudo, text="💜 Clube Delírio Roxo", font=("Arial", 22, "bold"), fg=BRANCO, bg=ROXO_ESCURO).pack(pady=(20, 5))
    tk.Label(area_conteudo, text="Seu programa de recompensas exclusivo!", font=("Arial", 11), fg=CINZA, bg=ROXO_ESCURO).pack()

    caixa = tk.Frame(area_conteudo, bg="#21103D", highlightbackground=ROXO_MEDIO, highlightthickness=1)
    caixa.pack(fill="both", expand=True, padx=40, pady=20)

    pontos = cliente_logado.get("pontos", 0) if cliente_logado else 0

    # Card de Pontuação
    card_p = tk.Frame(caixa, bg="#32134F", highlightbackground=ROXO_MEDIO, highlightthickness=1)
    card_p.pack(fill="x", padx=30, pady=15)

    tk.Label(card_p, text="Seu Saldo Atual de Pontos", font=("Arial", 11, "bold"), fg=AMARELO, bg="#32134F").pack(pady=(10, 2))
    tk.Label(card_p, text=f"{pontos} PTS", font=("Arial", 26, "bold"), fg=BRANCO, bg="#32134F").pack()
    tk.Label(card_p, text="Cada R$ 1,00 gasto = 1 Ponto acumulado", font=("Arial", 8), fg=CINZA, bg="#32134F").pack(pady=(2, 10))

    # Benefícios e Cupons
    tk.Label(caixa, text="🎁 Benefícios Disponíveis:", font=("Arial", 12, "bold"), fg=BRANCO, bg="#21103D").pack(anchor="w", padx=30, pady=(10, 5))

    frame_cupom = tk.Frame(caixa, bg="#261044", highlightbackground=VERDE, highlightthickness=1)
    frame_cupom.pack(fill="x", padx=30, pady=5)

    tk.Label(frame_cupom, text="🏷 Cupom de 10% DE DESCONTO", font=("Arial", 11, "bold"), fg=VERDE, bg="#261044").pack(side="left", padx=15, pady=10)
    
    def usar_cupom():
        if not carrinho:
            messagebox.showwarning("Açaízon", "Adicione itens ao carrinho antes de resgatar o cupom!")
            return
        messagebox.showinfo("Clube Delírio Roxo", "Cupom DELIRIO10 aplicado com sucesso no seu checkout!")

    tk.Button(frame_cupom, text="Resgatar Cupom", font=("Arial", 9, "bold"), bg=VERDE, fg=BRANCO, command=usar_cupom).pack(side="right", padx=15)

def mostrar_configuracoes():
    """Aba Configurações direcionando para ações e opção de Root Master/Sair."""
    limpar_conteudo()

    tk.Label(area_conteudo, text="⚙ Configurações do Sistema", font=("Arial", 22, "bold"), fg=BRANCO, bg=ROXO_ESCURO).pack(pady=20)

    btn_frame = tk.Frame(area_conteudo, bg="#21103D", highlightbackground=ROXO_MEDIO, highlightthickness=1)
    btn_frame.pack(fill="both", expand=True, padx=50, pady=20)

    def acao_limpar_carrinho():
        carrinho.clear()
        atualizar_painel_direito()
        messagebox.showinfo("Configurações", "Carrinho limpo com sucesso.")

    def acao_root_master():
        win = tk.Toplevel(janela)
        win.title("Acesso Master")
        win.geometry("300x180")
        win.configure(bg=ROXO_ESCURO)

        tk.Label(win, text="Área Restrita (Root Master)", font=("Arial", 11, "bold"), fg=AMARELO, bg=ROXO_ESCURO).pack(pady=10)
        ent = tk.Entry(win, show="*")
        ent.pack(pady=5)

        def validar():
            if ent.get() == "admin123":
                win.destroy()
                messagebox.showinfo("Root Master", "Acesso concedido. Banco de dados sincronizado.")
            else:
                messagebox.showerror("Erro", "Senha master incorreta.")

        tk.Button(win, text="Autenticar", bg=ROSA, fg=BRANCO, command=validar).pack(pady=10)

    tk.Button(btn_frame, text="🗑 Esvaziar Carrinho Atual", font=("Arial", 11, "bold"), bg="#32134F", fg=BRANCO, anchor="w", padx=20, command=acao_limpar_carrinho).pack(fill="x", padx=20, pady=10)
    tk.Button(btn_frame, text="🔐 Painel Root Master (Administrador)", font=("Arial", 11, "bold"), bg="#32134F", fg=BRANCO, anchor="w", padx=20, command=acao_root_master).pack(fill="x", padx=20, pady=10)
    tk.Button(btn_frame, text="🚪 Sair do Sistema PDV", font=("Arial", 11, "bold"), bg=ROSA, fg=BRANCO, anchor="w", padx=20, command=janela.destroy).pack(fill="x", padx=20, pady=10)

# ============================================================
# TELA DE CHECKOUT E COMPROVANTE DE PAGAMENTO
# ============================================================
def mostrar_checkout():
    """Tela Final para Fechar o Ciclo do Pedido."""
    limpar_conteudo()

    tk.Label(area_conteudo, text="🛒 Finalizar Pedido / Checkout", font=("Arial", 22, "bold"), fg=BRANCO, bg=ROXO_ESCURO).pack(pady=15)

    container = tk.Frame(area_conteudo, bg="#21103D", highlightbackground=ROXO_MEDIO, highlightthickness=1)
    container.pack(fill="both", expand=True, padx=30, pady=10)

    subtotal = sum(i['preco'] for i in carrinho)
    
    # Forma de Pagamento
    tk.Label(container, text="Forma de Pagamento:", font=("Arial", 11, "bold"), fg=AMARELO, bg="#21103D").pack(anchor="w", padx=25, pady=(15, 2))
    var_pagto = tk.StringVar(value="Pix")
    cbo_pagto = ttk.Combobox(container, textvariable=var_pagto, values=["Pix", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"], state="readonly")
    cbo_pagto.pack(anchor="w", padx=25)

    # Opção de Entrega
    tk.Label(container, text="Opção de Entrega:", font=("Arial", 11, "bold"), fg=AMARELO, bg="#21103D").pack(anchor="w", padx=25, pady=(15, 2))
    var_entrega = tk.StringVar(value="Consumo no Local")
    cbo_entrega = ttk.Combobox(container, textvariable=var_entrega, values=["Consumo no Local", "Retirada no Balcão", "Delivery (+R$ 5,00)"], state="readonly")
    cbo_entrega.pack(anchor="w", padx=25)

    def emitir_comprovante():
        taxa = 5.00 if "Delivery" in var_entrega.get() else 0.00
        total = subtotal + taxa

        # Modal do Comprovante
        comp = tk.Toplevel(janela)
        comp.title("Comprovante do Pedido - Açaízon")
        comp.geometry("380x480")
        comp.configure(bg="#FFF")

        tk.Label(comp, text="--- AÇAÍZON PDV ---", font=("Courier", 14, "bold"), bg="#FFF", fg="#000").pack(pady=(15, 5))
        tk.Label(comp, text="Comprovante de Compra", font=("Courier", 10), bg="#FFF", fg="#000").pack()
        tk.Label(comp, text="-----------------------------------", bg="#FFF", fg="#000").pack()

        for item in carrinho:
            tk.Label(comp, text=f"{item['nome']} - R$ {item['preco']:.2f}", font=("Courier", 9), bg="#FFF", fg="#000", anchor="w").pack(fill="x", padx=20)

        tk.Label(comp, text="-----------------------------------", bg="#FFF", fg="#000").pack()
        tk.Label(comp, text=f"Subtotal: R$ {subtotal:.2f}", font=("Courier", 9), bg="#FFF", fg="#000", anchor="w").pack(fill="x", padx=20)
        tk.Label(comp, text=f"Taxa Entrega: R$ {taxa:.2f}", font=("Courier", 9), bg="#FFF", fg="#000", anchor="w").pack(fill="x", padx=20)
        tk.Label(comp, text=f"TOTAL: R$ {total:.2f}", font=("Courier", 12, "bold"), bg="#FFF", fg="#000", anchor="w").pack(fill="x", padx=20, pady=5)
        
        tk.Label(comp, text=f"Forma Pagto: {var_pagto.get()}", font=("Courier", 9), bg="#FFF", fg="#000", anchor="w").pack(fill="x", padx=20)
        tk.Label(comp, text=f"Entrega: {var_entrega.get()}", font=("Courier", 9), bg="#FFF", fg="#000", anchor="w").pack(fill="x", padx=20)
        tk.Label(comp, text="Tempo Estimado: 15 a 25 min ⏱", font=("Courier", 10, "bold"), bg="#FFF", fg="#42A62A").pack(pady=15)

        # Salva o pedido no DB e limpa
        if cliente_logado:
            salvar_pedido(cliente_logado["id"], "Pedido PDV", "Vários", var_pagto.get(), var_entrega.get(), subtotal, taxa, total)

        carrinho.clear()
        atualizar_painel_direito()

        tk.Button(comp, text="Fechar / Imprimir", bg="#000", fg="#FFF", command=lambda: (comp.destroy(), mostrar_inicio())).pack(pady=10)

    tk.Button(container, text=" Confirmar & Emitir Comprovante", font=("Arial", 12, "bold"), bg=VERDE, fg=BRANCO, command=emitir_comprovante).pack(pady=30, ipadx=10, ipady=5)

# ============================================================
# LAYOUT BASE: CABEÇALHO, MENU LATERAL E PAINEL
# ============================================================
cabecalho = tk.Frame(janela, bg="#3A075C", height=90)
cabecalho.pack(side="top", fill="x")
cabecalho.pack_propagate(False)

tk.Label(cabecalho, text="Açaízon", font=("Arial", 28, "bold"), fg=BRANCO, bg="#3A075C").pack(side="left", padx=25)
tk.Label(cabecalho, text="Mais que Açaí, é energia pra você! ♡", font=("Arial", 10, "italic"), fg=BRANCO, bg="#3A075C").pack(side="left", padx=10)

corpo = tk.Frame(janela, bg=ROXO_ESCURO)
corpo.pack(fill="both", expand=True)

# Menu Lateral Esquerdo
menu_lateral = tk.Frame(corpo, bg="#21103D", width=220)
menu_lateral.pack(side="left", fill="y", padx=(10, 5), pady=10)
menu_lateral.pack_propagate(False)

def criar_btn_menu(txt, cmd):
    return tk.Button(menu_lateral, text=txt, font=("Arial", 11, "bold"), bg="#32134F", fg=BRANCO, activebackground=ROSA_CLARO, activeforeground=BRANCO, relief="flat", cursor="hand2", anchor="w", padx=15, command=cmd).pack(fill="x", padx=10, pady=5, ipady=6)

criar_btn_menu("🏠   Início", mostrar_inicio)
criar_btn_menu("🥣   Cardápio", mostrar_cardapio)
criar_btn_menu("💜   Clube Delírio Roxo", mostrar_clube_delirio)
criar_btn_menu("⚙   Configurações", mostrar_configuracoes)

# Área do Conteúdo Central
area_conteudo = tk.Frame(corpo, bg=ROXO_ESCURO)
area_conteudo.pack(side="left", fill="both", expand=True, padx=5, pady=10)

# Painel Lateral Direito Unificado
painel_direito = tk.Frame(corpo, bg="#21103D", width=300)
painel_direito.pack(side="right", fill="y", padx=(5, 10), pady=10)
painel_direito.pack_propagate(False)

# ============================================================
# INICIALIZAÇÃO DO APLICATIVO
# ============================================================
def iniciar_aplicacao():
    atualizar_painel_direito()
    mostrar_inicio()
    janela.mainloop()

if __name__ == "__main__":
    iniciar_aplicacao()