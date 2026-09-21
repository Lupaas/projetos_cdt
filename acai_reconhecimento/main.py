# Importa o inicializador do Banco de Dados (Pessoa 2 - Lu)
from database.db import inicializar_banco

# Importa a Interface Gráfica da Pessoa 3 (Yas)
from src.app import iniciar_aplicacao

if __name__ == "__main__":
    # 1. Cria a estrutura do banco de dados (tabelas) se ainda não existirem
    inicializar_banco()
    
    # 2. Inicia o sistema completo (Interface + IA integrados)
    iniciar_aplicacao()