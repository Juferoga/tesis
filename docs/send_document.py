import requests
import os
import sys

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
bot_token = "6764398994:AAFKMbF5Quvm-arhMPerSiuBMye-xK1vhG8"
group_id  = "647870240"

# Obtener la URL del artefacto desde argumentos de línea de comandos
if len(sys.argv) > 1:
    artifact_url = sys.argv[1]
else:
    artifact_url = "URL del artefacto no proporcionada"

# Mensaje a enviar con enlace para descargar el artefacto
message = f"¡Hola, Grupo! Aquí está el documento: {artifact_url}"

# Enviar mensaje de texto
send_telegram_message(group_id, message, bot_token)
