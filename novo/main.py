import sys
import tkinter as tk
from tkinter import messagebox

from database.db import inicializar_banco, buscar_cliente_por_id, buscar_ultimo_pedido
from src.camera import reconhecer_cliente
import src.app as gui

def acionar_login_face_id():
    """Executa a verificação biométrica e sugere 'Peça o de sempre'."""
    resultado = reconhecer_cliente()

    if not resultado:
        return

    status = resultado.get("status")

    if status == "encontrado":
        cliente_id = resultado.get("id")
        dados_cliente = buscar_cliente_por_id(cliente_id)
        ultimo_pedido = buscar_ultimo_pedido(cliente_id)

        if dados_cliente:
            gui.cliente_logado = {
                "id": dados_cliente["id"],
                "nome": dados_cliente["nome"],
                "cpf": dados_cliente["cpf"],
                "telefone": dados_cliente["telefone"],
                "pontos": dados_cliente["pontos_fidelidade"]
            }
            gui.atualizar_painel_direito()

            if ultimo_pedido:
                msg = (
                    f"Bem-vindo(a) de volta, {dados_cliente['nome']}!\n\n"
                    f"Gosta de manter o padrão? Peça o de sempre!\n\n"
                    f"• Tamanho: {ultimo_pedido.get('tamanho')}\n"
                    f"• Acompanhamentos: {ultimo_pedido.get('toppings')}"
                )
                
                if messagebox.askyesno("✨ Peça o de Sempre", msg):
                    gui.carrinho.append({
                        "nome": f"Açaí Custom ({ultimo_pedido.get('tamanho')})",
                        "detalhes": ultimo_pedido.get('toppings', ''),
                        "preco": 20.00
                    })
                    gui.atualizar_painel_direito()
                    gui.mostrar_checkout()
                else:
                    gui.mostrar_cardapio()
            else:
                gui.mostrar_cardapio()

    elif status == "novo_cliente":
        if messagebox.askyesno("Cliente Não Encontrado", "Não encontramos seu rosto cadastrado.\nDeseja realizar seu cadastro agora?"):
            gui.abrir_modal_cadastro()

    elif status == "cancelado":
        messagebox.showinfo("Açaízon", "Reconhecimento cancelado.")

if __name__ == "__main__":
    inicializar_banco()
    gui.main_ref = sys.modules[__name__]
    gui.iniciar_aplicacao()