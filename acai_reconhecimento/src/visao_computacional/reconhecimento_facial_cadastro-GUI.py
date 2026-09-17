import sqlite3
import json
import os
import tkinter as tk
from tkinter import messagebox

DB_NAME = 'acaiteria.db'
CONFIG_FILE = 'config_acaiteria.json'

class AppDelirioRoxoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Delírio Roxo - Seu Açaí vale mais!")
        self.root.geometry("450x450")
        self.root.config(bg="#4A148C") # Roxo Açaí
        
        self.carregar_configuracoes()
        self.criar_tela_entrada()

    def carregar_configuracoes(self):
        """Lê as configurações do JSON caso exista."""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {"nome_loja": "Açaíteria Delírio Roxo"}

    def limpar_tela(self):
        """Remove os widgets antigos para transição de telas."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def criar_tela_entrada(self):
        """Identidade de Usuário: Entrar ou Cadastrar-se"""
        self.root.config(bg="#4A148C")
        
        lbl_titulo = tk.Label(self.root, text=f"💜 {self.config.get('nome_loja', 'Delírio Roxo')} 💜", font=("Arial", 18, "bold"), bg="#4A148C", fg="white")
        lbl_titulo.pack(pady=25)
        
        lbl_sub = tk.Label(self.root, text="Faça login facial ou cadastre-se!", font=("Arial", 11), bg="#4A148C", fg="#E1BEE7")
        lbl_sub.pack(pady=10)
        
        # Botão de Entrar (Reconhecimento Facial)
        btn_entrar = tk.Button(self.root, text="📸 Entrar (Reconhecimento Facial)", font=("Arial", 11, "bold"), 
                               bg="#FFC107", fg="black", width=32, height=2, command=self.login_facial)
        btn_entrar.pack(pady=15)
        
        # Botão de Cadastrar-se
        btn_cadastrar = tk.Button(self.root, text="📝 Cadastrar-se (Novo Cliente)", font=("Arial", 11), 
                                  bg="#7B1FA2", fg="white", width=32, height=2, command=self.ir_para_cadastro)
        btn_cadastrar.pack(pady=10)

    def login_facial(self):
        """Busca no SQLite para validar o Face ID e sugerir o açaí padrão."""
        if not os.path.exists(DB_NAME):
            messagebox.showwarning("Aviso", "Banco de dados vazio! Use o script CLI para gerar dados de teste.")
            return

        conexao = sqlite3.connect(DB_NAME)
        cursor = conexao.cursor()
        cursor.execute("SELECT nome, acai_preferido FROM clientes ORDER BY RANDOM() LIMIT 1;")
        resultado = cursor.fetchone()
        conexao.close()
        
        if resultado:
            nome, acai = resultado
            resposta = messagebox.askyesno(
                "Rosto Reconhecido! 🎉", 
                f"Olá, {nome}!\nAcesso liberado via Face ID.\n\nGosta de manter o padrão?\nPeça o de sempre: {acai}?"
            )
            if resposta:
                messagebox.showinfo("Cardápio & Pagamento", "Açaí padrão confirmado! Redirecionando para o pagamento...")
        else:
            messagebox.showwarning("Não Reconhecido", "Rosto não encontrado no BD. Redirecionando para o cadastro.")
            self.ir_para_cadastro()

    def ir_para_cadastro(self):
        """Tela de Cadastro (Coleta dados e concede cupom de 10% do Delírio Roxo)"""
        self.limpar_tela()
        
        lbl = tk.Label(self.root, text="Cadastro - Delírio Roxo", font=("Arial", 14, "bold"), bg="#4A148C", fg="white")
        lbl.pack(pady=15)
        
        tk.Label(self.root, text="Nome Completo:", bg="#4A148C", fg="white").pack()
        self.e_nome = tk.Entry(self.root, width=30)
        self.e_nome.pack(pady=3)
        
        tk.Label(self.root, text="Açaí Preferido (com adicionais):", bg="#4A148C", fg="white").pack()
        self.e_acai = tk.Entry(self.root, width=30)
        self.e_acai.pack(pady=3)
        
        btn_salvar = tk.Button(self.root, text="Salvar e Ganhar Cupom de 10%", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.salvar_usuario)
        btn_salvar.pack(pady=20)
        
        btn_voltar = tk.Button(self.root, text="⬅ Voltar", bg="#CCCCCC", width=15, command=self.criar_tela_entrada)
        btn_voltar.pack(pady=5)

    def salvar_usuario(self):
        nome = self.e_nome.get().strip()
        acai = self.e_acai.get().strip()
        
        if not nome or not acai:
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
            return
            
        conexao = sqlite3.connect(DB_NAME)
        cursor = conexao.cursor()
        cursor.execute("INSERT INTO clientes (nome, acai_preferido) VALUES (?, ?)", (nome, acai))
        conexao.commit()
        conexao.close()
        
        messagebox.showinfo("Sucesso!", f"Parabéns, {nome}!\nVocê entrou no clube Delírio Roxo e ganhou 10% de desconto!")
        self.criar_tela_entrada()

if __name__ == "__main__":
    root = tk.Tk()
    app = AppDelirioRoxoGUI(root)
    root.mainloop()