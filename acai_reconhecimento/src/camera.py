import cv2
import sys
import os

# Adiciona a pasta raiz ao PATH para conseguir importar o modulo database.db
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa as funções oficiais do seu Back-end (db.py)
from database.db import buscar_cliente_por_id, buscar_ultimo_pedido, conectar

def obter_ultimo_cliente_db():
    """
    Busca o cliente mais recente no SQLite via ID.
    """
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, apelido FROM clientes ORDER BY id DESC LIMIT 1;")
    cliente = cursor.fetchone()
    conn.close()
    return cliente

def reconhecer_cliente():
    """
    Função da Pessoa 1 (Visão Computacional - Modo Simulação):
    - Abre a webcam em tempo real usando OpenCV.
    - Pressionar ESPAÇO simula a leitura biométrica com sucesso.
    - Retorna o dicionário padronizado para o Front-end (Pessoa 3).
    """
    print("[IA] Iniciando captura de vídeo (Webcam) com OpenCV...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[ERRO] Não foi possível acessar a webcam.")
        return {"status": "erro", "mensagem": "Câmera indisponível"}

    cliente_encontrado = None
    print("[IA] Olhe para a câmera. Pressione 'ESPAÇO' para simular a leitura biométrica ou 'ESC' para sair.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERRO] Falha ao capturar o frame da câmera.")
            break
            
        # Elementos visuais guia (Quadrado verde e texto da loja)
        altura, largura, _ = frame.shape
        cv2.rectangle(frame, (largura//3, altura//4), (2*largura//3, 3*altura//4), (0, 255, 0), 2)
        cv2.putText(frame, "Delirio Roxo - Posicione o rosto", (40, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow('Delirio Roxo - Reconhecimento Facial', frame)
        tecla = cv2.waitKey(1) & 0xFF
        
        # Pressionar ESPAÇO (código 32) simula a validação biométrica
        if tecla == 32:
            print("[IA] Processando leitura biométrica...")
            cliente_db = obter_ultimo_cliente_db()
            
            if cliente_db:
                cliente_id = cliente_db[0]
                nome = cliente_db[1]
                apelido = cliente_db[2]
                
                # Busca o histórico do último açaí pedido por esse cliente
                ultimo_pedido = buscar_ultimo_pedido(cliente_id)

                cliente_encontrado = {
                    "status": "encontrado",
                    "id": cliente_id,
                    "nome": nome,
                    "apelido": apelido,
                    "ultimo_pedido": ultimo_pedido
                }
                print(f"[SUCESSO] Cliente reconhecido: {nome}")
            else:
                print("[INFO] Nenhum cliente cadastrado no banco. Tratando como novo cliente.")
                cliente_encontrado = {"status": "novo_cliente"}
            break
            
        # Pressionar ESC (código 27) para cancelar
        elif tecla == 27:
            cliente_encontrado = {"status": "cancelado"}
            break

    cap.release()
    cv2.destroyAllWindows()
    return cliente_encontrado

if __name__ == "__main__":
    resultado = reconhecer_cliente()
    print("Resultado do reconhecimento:", resultado)