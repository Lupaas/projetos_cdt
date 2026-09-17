from database.db import inicializar_banco, cadastrar_cliente, salvar_pedido
from src.app import IniciarAplicacao # Supondo que a Pessoa 3 criou essa função/classe

# Importe a IA da Pessoa 1 (Lari)


# Importe a Interface da Pessoa 3 (Yas)


if __name__ == "__main__":
    # 1. Garante que as tabelas e o banco de dados existam antes de abrir a tela
    inicializar_banco()
    
    # 2. Inicia a interface gráfica
    IniciarAplicacao()