import requests
import os

def send_telegram_message(chat_id, text, token):
    """Envía un mensaje de texto a un chat de Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, data=payload)
    return response.json()

# Token del bot y ID del grupo desde variables de entorno
bot_token = os.getenv('TELEGRAM_API_TOKEN')
group_id = os.getenv('TELEGRAM_GROUP_ID')

# Mensaje a enviar con enlace para descargar el artefacto
artifact_url = os.getenv('ARTIFACT_URL')  # Necesitas configurar esto en GitHub Actions
message = f"¡Hola, Grupo! Aquí está el documento: {artifact_url}"

# Enviar mensaje de texto
send_telegram_message(group_id, message, bot_token)
