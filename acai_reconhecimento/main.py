from database.db import inicializar_banco
from src.app import IniciarAplicacao # Supondo que a Pessoa 3 criou essa função/classe

if __name__ == "__main__":
    # 1. Garante que as tabelas e o banco de dados existam antes de abrir a tela
    inicializar_banco()
    
    # 2. Inicia a interface gráfica
    IniciarAplicacao()