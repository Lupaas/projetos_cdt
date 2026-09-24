import os
import sys
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
sys.path.append(PROJECT_ROOT)

from database.db import cadastrar_cliente, buscar_ultimo_pedido, salvar_pedido
from src.camera import capturar_foto_cadastro

LARGURA, ALTURA = 1200, 700
ROXO_ESCURO = "#17062F"
ROXO_MEDIO = "#5A1B91"
ROSA, ROSA_CLARO = "#E91E83", "#F52B91"
AMARELO, BRANCO, CINZA, VERDE = "#FFD21C", "#FFFFFF", "#B9AFC8", "#42A62A"

cliente_logado = None 
carrinho = [] 
desconto_fidelidade = 0.0

janela = tk.Tk()
janela.title("Açaízon - Sistema PDV")
janela.geometry(f"{LARGURA}x{ALTURA}")
janela.configure(bg=ROXO_ESCURO)

# Cardápio nas 4 Categorias Solicitadas
PRODUTOS = [
    {
        "id": 1,
        "nome": "Monte o seu Açaí",
        "descricao": "Escolha o tamanho e selecione os acompanhamentos/toppings que você mais gosta!",
        "preco_300ml": 14.00, "preco_500ml": 20.00, "preco_700ml": 26.00,
        "emoji": "🛠️"
    },
    {
        "id": 2,
        "nome": "Açaí Tradicional",
        "descricao": "Açaí puro e cremoso, batido com xarope de guaraná tradicional da casa.",
        "preco_300ml": 12.00, "preco_500ml": 17.00, "preco_700ml": 22.00,
        "emoji": "🥣"
    },
    {
        "id": 3,
        "nome": "Açaí Premium",
        "descricao": "Açaí cremoso acompanhado de camadas generosas de Nutella, Leite Ninho e Morango.",
        "preco_300ml": 18.00, "preco_500ml": 24.00, "preco_700ml": 30.00,
        "emoji": "✨"
    },
    {
        "id": 4,
        "nome": "Delírio Roxo Especial",
        "descricao": "Nossa receita secreta especial! Açaí com Banana, Kiwi, Paçoca, Mel e Calda Extra.",
        "preco_300ml": 20.00, "preco_500ml": 27.00, "preco_700ml": 34.00,
        "emoji": "🍧"
    }
]

ACOMPANHAMENTOS = [
    "Leite em Pó", "Granola", "Paçoca", "Leite Condensado",
    "Morango", "Banana", "Nutella", "Kiwi", "Mel", "Confete"
]

def limpar_conteudo():
    for widget in area_conteudo.winfo_children():
        widget.destroy()

def mascarar_dado(texto, visiveis=3):
    if not texto: return "-"
    if len(texto) <= visiveis: return "*" * len(texto)
    return "*" * (len(texto) - visiveis) + texto[-visiveis:]

def atualizar_painel_direito():
    for widget in painel_direito.winfo_children():
        widget.destroy()

    tk.Label(painel_direito, text="👤 Painel do Cliente", font=("Arial", 11, "bold"), fg=BRANCO, bg="#21103D").pack(pady=(15, 10))

    if cliente_logado:
        info = tk.Frame(painel_direito, bg="#261044", highlightbackground=ROXO_MEDIO, highlightthickness=1)
        info.pack(fill="x", padx=15, pady=5)

        tk.Label(info, text=f"Olá, {cliente_logado.get('nome')}!", font=("Arial", 10, "bold"), fg=AMARELO, bg="#261044").pack(anchor="w", padx=10, pady=(8, 2))
        tk.Label(info, text=f"CPF: ***.***.{mascarar_dado(cliente_logado.get('cpf'), 3)}", font=("Arial", 8), fg=BRANCO, bg="#261044").pack(anchor="w", padx=10)
        
        pts = cliente_logado.get('pontos', 0)
        tk.Label(info, text=f"Pontos: {pts} pts 💜", font=("Arial", 9, "bold"), fg=ROSA_CLARO, bg="#261044").pack(anchor="w", padx=10, pady=(2, 8))

        tk.Button(painel_direito, text="Sair da Conta", font=("Arial", 9, "bold"), bg=ROSA, fg=BRANCO, relief="flat", cursor="hand2", command=deslogar_cliente).pack(fill="x", padx=15, pady=5)
    else:
        tk.Label(painel_direito, text="Olá!\nCadastre-se para acumular pontos!", font=("Arial", 9), fg=CINZA, bg="#21103D", justify="center").pack(pady=5)
        
        tk.Button(painel_direito, text="🔑 Entrar (Face ID)", font=("Arial", 9, "bold"), bg=ROXO_MEDIO, fg=BRANCO, relief="flat", cursor="hand2", command=lambda: main_ref.acionar_login_face_id() if main_ref else messagebox.showwarning("Atenção", "Execute o sistema através do main.py") if main_ref else None).pack(fill="x", padx=15, pady=3)
        tk.Button(painel_direito, text="👤 Cadastrar Cliente + Face ID", font=("Arial", 10, "bold"), bg=AMARELO, fg="#3B2600", relief="flat", cursor="hand2", command=abrir_modal_cadastro).pack(fill="x", padx=15, pady=5)

    tk.Label(painel_direito, text="🛒 Seu Carrinho", font=("Arial", 10, "bold"), fg=VERDE, bg="#21103D").pack(anchor="w", padx=15, pady=(15, 5))
    f_pedidos = tk.Frame(painel_direito, bg="#261044", highlightbackground=ROXO_MEDIO, highlightthickness=1)
    f_pedidos.pack(fill="x", padx=15)

    if carrinho:
        subtotal = sum(i['preco'] for i in carrinho)
        for item in carrinho:
            tk.Label(f_pedidos, text=f"• {item['nome']} - R$ {item['preco']:.2f}", font=("Arial", 8, "bold"), fg=BRANCO, bg="#261044", anchor="w").pack(fill="x", padx=8, pady=(4, 0))
            if item.get("detalhes"):
                tk.Label(f_pedidos, text=f"  ({item['detalhes']})", font=("Arial", 7), fg=CINZA, bg="#261044", anchor="w").pack(fill="x", padx=8)

        tk.Label(f_pedidos, text=f"Subtotal: R$ {subtotal:.2f}", font=("Arial", 10, "bold"), fg=AMARELO, bg="#261044").pack(pady=8)
        tk.Button(f_pedidos, text="Finalizar Pedido", font=("Arial", 9, "bold"), bg=VERDE, fg=BRANCO, relief="flat", cursor="hand2", command=mostrar_checkout).pack(fill="x", padx=10, pady=(0, 10))
    else:
        tk.Label(f_pedidos, text="Nenhum item selecionado", font=("Arial", 9), fg=CINZA, bg="#261044").pack(pady=15)

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

    tk.Label(win, text="Novo Cadastro", font=("Arial", 14, "bold"), fg=BRANCO, bg=ROXO_ESCURO).pack(pady=10)

    campos = [("Nome Completo:", "nome"), ("Apelido:", "apelido"), ("E-mail:", "email"), 
              ("Telefone:", "telefone"), ("Endereço:", "endereco"), ("Idade:", "idade"), ("CPF:", "cpf")]
    
    entries = {}
    for label, key in campos:
        f = tk.Frame(win, bg=ROXO_ESCURO)
        f.pack(fill="x", padx=20, pady=2)
        tk.Label(f, text=label, font=("Arial", 8, "bold"), fg=CINZA, bg=ROXO_ESCURO, width=12, anchor="w").pack(side="left")
        e = tk.Entry(f)
        e.pack(side="right", fill="x", expand=True)
        entries[key] = e

    foto_path_var = tk.StringVar(value="")

    def tirar_foto():
        cpf_val = entries["cpf"].get().strip()
        if not cpf_val:
            messagebox.showwarning("Atenção", "Preencha o CPF antes do Face ID.")
            return
        sucesso, res = capturar_foto_cadastro(cpf_val)
        if sucesso:
            foto_path_var.set(res)
            messagebox.showinfo("Face ID", "Foto capturada com sucesso!")
        else:
            messagebox.showerror("Erro", res)

    tk.Button(win, text="📷 Capturar Face ID (Câmera)", font=("Arial", 9, "bold"), bg=ROXO_MEDIO, fg=BRANCO, command=tirar_foto).pack(pady=10)

    def salvar():
        global cliente_logado
        nome = entries["nome"].get()
        cpf = entries["cpf"].get()
        
        if not nome or not cpf:
            messagebox.showwarning("Atenção", "Preencha pelo menos Nome e CPF.")
            return

        ok, cid = cadastrar_cliente(nome, cpf, entries["telefone"].get(), foto_path_var.get())
        if ok:
            cliente_logado = {
                "id": cid, "nome": nome, "apelido": entries["apelido"].get(),
                "email": entries["email"].get(), "cpf": cpf,
                "telefone": entries["telefone"].get(), "endereco": entries["endereco"].get(), "pontos": 50
            }
            atualizar_painel_direito()
            win.destroy()
            messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
        else:
            messagebox.showerror("Erro", str(cid))

    tk.Button(win, text="Salvar Cadastro", font=("Arial", 10, "bold"), bg=AMARELO, fg="#3B2600", command=salvar).pack(pady=10)

def abrir_modal_personalizar(produto):
    win = tk.Toplevel(janela)
    win.title(f"Personalizar {produto['nome']}")
    win.geometry("400x500")
    win.configure(bg=ROXO_ESCURO)

    tk.Label(win, text=f"{produto['emoji']} {produto['nome']}", font=("Arial", 14, "bold"), fg=BRANCO, bg=ROXO_ESCURO).pack(pady=10)

    # Escolha do Tamanho
    tk.Label(win, text="Escolha o Tamanho:", font=("Arial", 10, "bold"), fg=AMARELO, bg=ROXO_ESCURO).pack(anchor="w", padx=20, pady=(5, 2))
    tamanho_var = tk.StringVar(value="500ml")

    f_tamanhos = tk.Frame(win, bg=ROXO_ESCURO)
    f_tamanhos.pack(fill="x", padx=20)

    r1 = tk.Radiobutton(f_tamanhos, text=f"300ml (R$ {produto['preco_300ml']:.2f})", variable=tamanho_var, value="300ml", bg=ROXO_ESCURO, fg=BRANCO, selectcolor="#21103D", activebackground=ROXO_ESCURO)
    r2 = tk.Radiobutton(f_tamanhos, text=f"500ml (R$ {produto['preco_500ml']:.2f})", variable=tamanho_var, value="500ml", bg=ROXO_ESCURO, fg=BRANCO, selectcolor="#21103D", activebackground=ROXO_ESCURO)
    r3 = tk.Radiobutton(f_tamanhos, text=f"700ml (R$ {produto['preco_700ml']:.2f})", variable=tamanho_var, value="700ml", bg=ROXO_ESCURO, fg=BRANCO, selectcolor="#21103D", activebackground=ROXO_ESCURO)
    r1.pack(anchor="w"); r2.pack(anchor="w"); r3.pack(anchor="w")

    # Acompanhamentos
    tk.Label(win, text="Escolha os Acompanhamentos:", font=("Arial", 10, "bold"), fg=AMARELO, bg=ROXO_ESCURO).pack(anchor="w", padx=20, pady=(15, 2))
    
    f_toppings = tk.Frame(win, bg="#21103D", highlightbackground=ROXO_MEDIO, highlightthickness=1)
    f_toppings.pack(fill="both", expand=True, padx=20, pady=5)

    checks = {}
    for top in ACOMPANHAMENTOS:
        var = tk.BooleanVar()
        cb = tk.Checkbutton(f_toppings, text=top, variable=var, bg="#21103D", fg=BRANCO, selectcolor=ROXO_ESCURO, activebackground="#21103D")
        cb.pack(anchor="w", padx=10, pady=1)
        checks[top] = var

    def adicionar():
        tam = tamanho_var.get()
        preco = produto[f'preco_{tam}']
        selecionados = [top for top, var in checks.items() if var.get()]
        detalhes_str = f"{tam} | " + (", ".join(selecionados) if selecionados else "Sem extras")

        carrinho.append({
            "nome": produto["nome"],
            "tamanho": tam,
            "toppings": ", ".join(selecionados),
            "detalhes": detalhes_str,
            "preco": preco
        })
        atualizar_painel_direito()
        win.destroy()
        messagebox.showinfo("Açaízon", f"{produto['nome']} adicionado ao carrinho!")

    tk.Button(win, text="Adicionar ao Carrinho 🛒", font=("Arial", 11, "bold"), bg=ROSA, fg=BRANCO, relief="flat", command=adicionar).pack(pady=15)

def mostrar_inicio():
    limpar_conteudo()
    tk.Label(area_conteudo, text="Bem-vindo ao Açaízon!", font=("Arial", 24, "bold"), fg=BRANCO, bg=ROXO_ESCURO).pack(pady=(35, 10))
    tk.Label(area_conteudo, text="Mais que açaí, uma energia pra você!", font=("Arial", 12), fg=CINZA, bg=ROXO_ESCURO).pack()

def mostrar_cardapio():
    limpar_conteudo()
    tk.Label(area_conteudo, text="🥣 Nosso Cardápio Especial", font=("Arial", 20, "bold"), fg=BRANCO, bg=ROXO_ESCURO).pack(anchor="w", padx=20, pady=10)

    for prod in PRODUTOS:
        card = tk.Frame(area_conteudo, bg="#21103D", highlightbackground=ROXO_MEDIO, highlightthickness=1)
        card.pack(fill="x", padx=20, pady=8)

        tk.Label(card, text=prod["emoji"], font=("Arial", 24), bg="#21103D").pack(side="left", padx=15)

        info_frame = tk.Frame(card, bg="#21103D")
        info_frame.pack(side="left", fill="both", expand=True, pady=10)

        tk.Label(info_frame, text=prod["nome"], font=("Arial", 12, "bold"), fg=AMARELO, bg="#21103D").pack(anchor="w")
        tk.Label(info_frame, text=prod["descricao"], font=("Arial", 9), fg=CINZA, bg="#21103D", wraplength=450, justify="left").pack(anchor="w")
        tk.Label(info_frame, text=f"A partir de R$ {prod['preco_300ml']:.2f}", font=("Arial", 10, "bold"), fg=BRANCO, bg="#21103D").pack(anchor="w", pady=(2, 0))

        tk.Button(
            card, text="Personalizar e Pedir", font=("Arial", 9, "bold"),
            bg=ROSA, fg=BRANCO, relief="flat", cursor="hand2",
            command=lambda p=prod: abrir_modal_personalizar(p)
        ).pack(side="right", padx=15, pady=15)

def mostrar_fidelidade():
    limpar_conteudo()
    tk.Label(area_conteudo, text="💜 Clube Delírio Roxo", font=("Arial", 20, "bold"), fg=BRANCO, bg=ROXO_ESCURO).pack(anchor="w", padx=20, pady=10)

    box = tk.Frame(area_conteudo, bg="#21103D", highlightbackground=ROSA, highlightthickness=2)
    box.pack(fill="both", expand=True, padx=20, pady=10)

    tk.Label(box, text="Seu Açaí vale mais!", font=("Arial", 16, "bold"), fg=AMARELO, bg="#21103D").pack(pady=(20, 5))
    
    txt = "Quer aproveitar descontos incríveis e cashback nas suas compras?\nFaça parte do Delírio Roxo!"
    tk.Label(box, text=txt, font=("Arial", 11), fg=BRANCO, bg="#21103D", justify="center").pack(pady=10)

    def resgatar():
        global desconto_fidelidade
        desconto_fidelidade = 0.10
        atualizar_painel_direito()
        messagebox.showinfo("🎉 Clube Delírio Roxo", "Parabéns! Você ativou seu cupom de 10% de desconto no pedido!")

    tk.Button(box, text="🎁 Entrar no Clube e Ganhar 10% OFF", font=("Arial", 11, "bold"), bg=ROSA, fg=BRANCO, relief="flat", cursor="hand2", command=resgatar).pack(pady=20, ipadx=10, ipady=5)

def mostrar_checkout():
    limpar_conteudo()
    tk.Label(area_conteudo, text="🛒 Finalizar Pedido", font=("Arial", 20, "bold"), fg=BRANCO, bg=ROXO_ESCURO).pack(anchor="w", padx=20, pady=10)

    if not carrinho:
        tk.Label(area_conteudo, text="Seu carrinho está vazio!", font=("Arial", 12), fg=CINZA, bg=ROXO_ESCURO).pack(pady=30)
        return

    subtotal = sum(i['preco'] for i in carrinho)
    valor_desconto = subtotal * desconto_fidelidade
    taxa_entrega = 5.00
    total = (subtotal - valor_desconto) + taxa_entrega
    
    f_checkout = tk.Frame(area_conteudo, bg="#21103D", highlightbackground=ROXO_MEDIO, highlightthickness=1)
    f_checkout.pack(fill="both", expand=True, padx=20, pady=10)

    tk.Label(f_checkout, text="Forma de Pagamento:", font=("Arial", 11, "bold"), fg=AMARELO, bg="#21103D").pack(anchor="w", padx=20, pady=(15, 5))
    pag_var = tk.StringVar(value="Pix")
    for opt in ["Débito", "Pix", "Crédito", "Boleto", "VR"]:
        tk.Radiobutton(f_checkout, text=opt, variable=pag_var, value=opt, bg="#21103D", fg=BRANCO, selectcolor=ROXO_ESCURO, activebackground="#21103D").pack(anchor="w", padx=30)

    tk.Label(f_checkout, text="Opção de Entrega:", font=("Arial", 11, "bold"), fg=AMARELO, bg="#21103D").pack(anchor="w", padx=20, pady=(15, 5))
    entrega_var = tk.StringVar(value="Delivery")
    for opt in ["Retirar na loja", "Delivery"]:
        tk.Radiobutton(f_checkout, text=opt, variable=entrega_var, value=opt, bg="#21103D", fg=BRANCO, selectcolor=ROXO_ESCURO, activebackground="#21103D").pack(anchor="w", padx=30)

    resumo = f"Subtotal: R$ {subtotal:.2f} | Desconto: R$ {valor_desconto:.2f} | Total: R$ {total:.2f}"
    tk.Label(f_checkout, text=resumo, font=("Arial", 11, "bold"), fg=VERDE, bg="#21103D").pack(pady=15)

    def concluir():
        if cliente_logado:
            item = carrinho[0]
            salvar_pedido(cliente_logado["id"], item.get("tamanho", "500ml"), item.get("toppings", "Padrão"), pag_var.get(), entrega_var.get(), subtotal, taxa_entrega, total)
        
        mostrar_comprovante_e_status(pag_var.get(), entrega_var.get(), subtotal, taxa_entrega, total)

    tk.Button(f_checkout, text="Confirmar Pedido 🚀", font=("Arial", 12, "bold"), bg=VERDE, fg=BRANCO, relief="flat", cursor="hand2", command=concluir).pack(pady=15)

def mostrar_comprovante_e_status(pagamento, entrega, subtotal, taxa, total):
    limpar_conteudo()
    tk.Label(area_conteudo, text="🧾 Comprovante do Pedido & Status", font=("Arial", 18, "bold"), fg=BRANCO, bg=ROXO_ESCURO).pack(anchor="w", padx=20, pady=10)

    card = tk.Frame(area_conteudo, bg="#21103D", highlightbackground=VERDE, highlightthickness=1)
    card.pack(fill="both", expand=True, padx=20, pady=5)

    nome_c = cliente_logado.get("nome", "Cliente") if cliente_logado else "Cliente Visitante"
    end_c = cliente_logado.get("endereco", "Balcão / Retirada") if cliente_logado else "Não informado"
    tel_c = cliente_logado.get("telefone", "-") if cliente_logado else "-"
    hora = datetime.datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

    itens_str = "\n".join([f"• {i['nome']} ({i.get('detalhes', 'Padrão')})" for i in carrinho])

    comp_txt = (
        f"--- COMPROVANTE AÇAÍZON ---\n"
        f"Cliente: {nome_c}\nEndereço: {end_c}\nTelefone: {tel_c}\n"
        f"Horário do Pedido: {hora}\n"
        f"----------------------------\n"
        f"Itens do Pedido:\n{itens_str}\n"
        f"----------------------------\n"
        f"Subtotal: R$ {subtotal:.2f}\nTaxa de Entrega: R$ {taxa:.2f}\nTotal do Pedido: R$ {total:.2f}\n"
        f"Pagamento: {pagamento} | Opção: {entrega}\n\n"
        f"🛵 Status da Entrega: Em preparação (Tempo estimado: 30-40 min)"
    )

    tk.Label(card, text=comp_txt, font=("Courier", 9), fg=BRANCO, bg="#21103D", justify="left").pack(anchor="w", padx=15, pady=15)

    def novo():
        carrinho.clear()
        atualizar_painel_direito()
        mostrar_inicio()

    tk.Button(card, text="Voltar ao Início", font=("Arial", 10, "bold"), bg=AMARELO, fg="#3B2600", command=novo).pack(pady=10)

# Layout Principal (Design e Estrutura Inicial Restaurados)
cabecalho = tk.Frame(janela, bg="#3A075C", height=80)
cabecalho.pack(side="top", fill="x")
tk.Label(cabecalho, text="🍇 Açaízon", font=("Arial", 24, "bold"), fg=BRANCO, bg="#3A075C").pack(side="left", padx=20)

corpo = tk.Frame(janela, bg=ROXO_ESCURO)
corpo.pack(fill="both", expand=True)

menu_lateral = tk.Frame(corpo, bg="#21103D", width=200)
menu_lateral.pack(side="left", fill="y", padx=5, pady=5)

botao_inicio = tk.Button(menu_lateral, text="🏠 Início", font=("Arial", 11, "bold"), bg="#32134F", fg=BRANCO, anchor="w", relief="flat", command=mostrar_inicio)
botao_inicio.pack(fill="x", padx=10, pady=5)

tk.Button(menu_lateral, text="🥣 Cardápio", font=("Arial", 11, "bold"), bg="#32134F", fg=BRANCO, anchor="w", relief="flat", command=mostrar_cardapio).pack(fill="x", padx=10, pady=5)
tk.Button(menu_lateral, text="💜 Clube Delírio Roxo", font=("Arial", 11, "bold"), bg="#32134F", fg=AMARELO, anchor="w", relief="flat", command=mostrar_fidelidade).pack(fill="x", padx=10, pady=5)

area_conteudo = tk.Frame(corpo, bg=ROXO_ESCURO)
area_conteudo.pack(side="left", fill="both", expand=True, padx=5, pady=5)

painel_direito = tk.Frame(corpo, bg="#21103D", width=280)
painel_direito.pack(side="right", fill="y", padx=5, pady=5)

main_ref = None

def iniciar_aplicacao():
    atualizar_painel_direito()
    mostrar_inicio()
    janela.mainloop()

if __name__ == "__main__":
    iniciar_aplicacao()