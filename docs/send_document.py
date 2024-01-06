import requests

def send_telegram_message(chat_id, text, token):
    """Envía un mensaje de texto a un chat de Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, data=payload)
    return response.json()

def send_telegram_document(chat_id, document_path, token):
    """Envía un documento a un chat de Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    payload = {
        "chat_id": chat_id
    }
    files = {
        "document": open(document_path, "rb")
    }
    response = requests.post(url, data=payload, files=files)
    return response.json()

# Token del bot y ID del grupo
bot_token = "6764398994:AAFKMbF5Quvm-arhMPerSiuBMye-xK1vhG8"
group_id = "647870240"  # Reemplaza con el ID real de tu grupo

# Mensaje a enviar
message = "¡Hola, Grupo! Aquí está el documento."

# Enviar mensaje de texto
send_telegram_message(group_id, message, bot_token)

# Ruta al archivo PDF (ajusta esto según tu configuración)
pdf_path = "docs/main.pdf"

# Enviar documento PDF
send_telegram_document(group_id, pdf_path, bot_token)
