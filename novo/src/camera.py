import cv2
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
sys.path.append(PROJECT_ROOT)

from database.db import buscar_ultimo_cliente, buscar_ultimo_pedido

# Tenta carregar o classificador de rostos com tratamento de exceção
try:
    CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
except AttributeError:
    face_cascade = None

def capturar_foto_cadastro(cpf_cliente):
    """Abre a webcam para capturar e salvar a foto de Face ID do cliente."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return False, "Câmera indisponível"

    foto_salva_path = ""
    sucesso = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detecta o rosto se o classificador estiver disponível
        if face_cascade is not None and not face_cascade.empty():
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.putText(frame, "Pressione ESPACO para Tirar a Foto ou ESC para Cancelar", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow("Acaizon - Cadastro de Face ID", frame)
        tecla = cv2.waitKey(1) & 0xFF

        if tecla == 32:  # Barra de Espaço
            pastas_faces = os.path.join(PROJECT_ROOT, "assets", "faces")
            os.makedirs(pastas_faces, exist_ok=True)
            foto_salva_path = os.path.join(pastas_faces, f"face_{cpf_cliente}.jpg")
            
            cv2.imwrite(foto_salva_path, frame)
            sucesso = True
            break
        elif tecla == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

    if sucesso:
        return True, foto_salva_path
    return False, "Captura cancelada."

def reconhecer_cliente():
    """Abre a webcam para reconhecer o cliente e simular a leitura do Face ID."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return {"status": "erro", "mensagem": "Câmera indisponível"}

    cliente_encontrado = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Desenha retângulo no rosto
        if face_cascade is not None and not face_cascade.empty():
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, "Rosto Detectado!", (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.putText(frame, "ESPACO = Validar Face ID | ESC = Cancelar", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow("Acaizon - Reconhecimento Facial", frame)
        tecla = cv2.waitKey(1) & 0xFF

        if tecla == 32:  # ESPAÇO
            cliente_db = buscar_ultimo_cliente()

            if cliente_db:
                ultimo_pedido = buscar_ultimo_pedido(cliente_db["id"])
                cliente_encontrado = {
                    "status": "encontrado",
                    "id": cliente_db["id"],
                    "nome": cliente_db["nome"],
                    "cpf": cliente_db["cpf"],
                    "telefone": cliente_db["telefone"],
                    "pontos": cliente_db["pontos_fidelidade"],
                    "ultimo_pedido": ultimo_pedido
                }
            else:
                cliente_encontrado = {"status": "novo_cliente"}
            break

        elif tecla == 27:  # ESC
            cliente_encontrado = {"status": "cancelado"}
            break

    cap.release()
    cv2.destroyAllWindows()
    return cliente_encontrado