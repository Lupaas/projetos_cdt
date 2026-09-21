import sqlite3
import json
import os
import tkinter as tk
from tkinter import messagebox
from src.camera import reconhecer_cliente  # Importando a sua função real da câmera!

DB_NAME = 'acai_sistema.db'
CONFIG_FILE = 'config_acaiteria.json'

class AppDelirioRoxoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Delírio Roxo - Seu Açaí vale mais!")
        self.root.geometry("450x480")
        self.root.config(bg="#4A148C")
        
        self.carregar_configuracoes()
        self.criar_tela_entrada()

    def carregar_configuracoes(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {"nome_loja": "Açaíteria Delírio Roxo"}

    def limpar_tela(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def criar_tela_entrada(self):
        self.root.config(bg="#4A148C")
        
        lbl_titulo = tk.Label(self.root, text=f"💜 {self.config.get('nome_loja', 'Delírio Roxo')} 💜", font=("Arial", 18, "bold"), bg="#4A148C", fg="white")
        lbl_titulo.pack(pady=25)
        
        lbl_sub = tk.Label(self.root, text="Faça login facial ou cadastre-se!", font=("Arial", 11), bg="#4A148C", fg="#E1BEE7")
        lbl_sub.pack(pady=10)
        
        # Botão de Entrar aciona o Reconhecimento Facial real
        btn_entrar = tk.Button(self.root, text="📸 Entrar (Reconhecimento Facial)", font=("Arial", 11, "bold"), 
                               bg="#FFC107", fg="black", width=32, height=2, command=self.login_facial)
        btn_entrar.pack(pady=15)
        
        btn_cadastrar = tk.Button(self.root, text="📝 Cadastrar-se (Novo Cliente)", font=("Arial", 11), 
                                  bg="#7B1FA2", fg="white", width=32, height=2, command=self.ir_para_cadastro)
        btn_cadastrar.pack(pady=10)

    def login_facial(self):
        """Aciona a webcam real e valida o resultado retornado pelo camera.py"""
        if not os.path.exists(DB_NAME):
            messagebox.showwarning("Aviso", "Banco de dados vazio! Cadastre um cliente primeiro.")
            self.ir_para_cadastro()
            return

        resultado_camera = reconhecer_cliente()
        status = resultado_camera.get("status")
        
        if status == "encontrado":
            nome = resultado_camera.get("nome")
            acai = resultado_camera.get("acai_preferido")
            
            resposta = messagebox.askyesno(
                "Rosto Reconhecido! 🎉", 
                f"Olá, {nome}!\nAcesso liberado via Câmera.\n\nGosta de manter o padrão?\nPeça o de sempre: {acai}?"
            )
            if resposta:
                messagebox.showinfo("Cardápio & Pagamento", "Açaí padrão confirmado! Redirecionando para o pagamento...")
                
        elif status == "novo_cliente":
            messagebox.showinfo("Novo Cliente", "Rosto não cadastrado. Vamos realizar o seu cadastro!")
            self.ir_para_cadastro()
            
        else:
            messagebox.showinfo("Cancelado", "Operação de reconhecimento facial cancelada.")

    def ir_para_cadastro(self):
        self.limpar_tela()
        
        lbl = tk.Label(self.root, text="Cadastro - Delírio Roxo", font=("Arial", 14, "bold"), bg="#4A148C", fg="white")
        lbl.pack(pady=8)
        
        tk.Label(self.root, text="Nome Completo:", bg="#4A148C", fg="white", font=("Arial", 10)).pack()
        self.e_nome = tk.Entry(self.root, width=30, font=("Arial", 10))
        self.e_nome.pack(pady=2)
        
        tk.Label(self.root, text="CPF:", bg="#4A148C", fg="white", font=("Arial", 10)).pack()
        self.e_cpf = tk.Entry(self.root, width=30, font=("Arial", 10))
        self.e_cpf.pack(pady=2)
        
        tk.Label(self.root, text="Data de Nascimento (DD/MM/AAAA):", bg="#4A148C", fg="white", font=("Arial", 10)).pack()
        self.e_nascimento = tk.Entry(self.root, width=30, font=("Arial", 10))
        self.e_nascimento.pack(pady=2)
        
        tk.Label(self.root, text="Açaí Preferido (com adicionais):", bg="#4A148C", fg="white", font=("Arial", 10)).pack()
        self.e_acai = tk.Entry(self.root, width=30, font=("Arial", 10))
        self.e_acai.pack(pady=2)
        
        # Atalho de Enter em qualquer campo para salvar
        self.e_nome.bind("<Return>", lambda event: self.salvar_usuario())
        self.e_cpf.bind("<Return>", lambda event: self.salvar_usuario())
        self.e_nascimento.bind("<Return>", lambda event: self.salvar_usuario())
        self.e_acai.bind("<Return>", lambda event: self.salvar_usuario())
        
        btn_salvar = tk.Button(self.root, text="Salvar e Ganhar Cupom de 10%", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.salvar_usuario)
        btn_salvar.pack(pady=10)
        
        btn_voltar = tk.Button(self.root, text="⬅ Voltar", bg="#CCCCCC", width=15, command=self.criar_tela_entrada)
        btn_voltar.pack(pady=2)

    def salvar_usuario(self):
        nome = self.e_nome.get().strip()
        cpf = self.e_cpf.get().strip()
        nascimento = self.e_nascimento.get().strip()
        acai = self.e_acai.get().strip()
        
        if not nome or not cpf or not acai:
            messagebox.showerror("Erro", "Preencha os campos obrigatórios (Nome, CPF e Açaí)!")
            return
            
        conexao = sqlite3.connect(DB_NAME)
        cursor = conexao.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT,
                data_nascimento TEXT,
                acai_preferido TEXT NOT NULL
            )
        ''')
        
        cursor.execute(
            "INSERT INTO clientes (nome, cpf, data_nascimento, acai_preferido) VALUES (?, ?, ?, ?)", 
            (nome, cpf, nascimento, acai)
        )
        conexao.commit()
        conexao.close()
        
        messagebox.showinfo("Sucesso!", f"Parabéns, {nome}!\nVocê entrou no clube Delírio Roxo e ganhou 10% de desconto!")
        self.criar_tela_entrada()

if __name__ == "__main__":
    root = tk.Tk()
    app = AppDelirioRoxoGUI(root)
    root.mainloop()