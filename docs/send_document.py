import sys
import requests
import os

print("Definiendo variables")

# Token del bot y ID del grupo desde variables de entorno
group_id  = "-1002073647780"
bot_token = "6764398994:AAFKMbF5Quvm-arhMPerSiuBMye-xK1vhG8"

url=f'https://api.telegram.org/bot{bot_token}/sendMessage'
send_gif=True
# Chats IDS :
chat_id = f"{group_id}"

if len(sys.argv) > 1:
    artifact_url = sys.argv[1]
else:
    artifact_url = " URL del artefacto no proporcionada "

# Mensaje a enviar con enlace para descargar el artefacto
json_data={
    "chat_id":chat_id,
    "parse_mode": "HTML",
    "disable_web_page_preview": "true",
    "text": f"<b>Action completada 🎉🎉</b> \n\nÚltima versión compilada correctamente \n{artifact_url} \n Repo URL: https://github.com/Juferoga/tesis/actions"
}

r = requests.post(url,json_data)

if (send_gif):
    json_data_s={
        "chat_id":chat_id,
        "animation": "https://c.tenor.com/8ZDLU43omvcAAAAM/kid-thumbs-up.gif"
    }
    r = requests.post(f'https://api.telegram.org/bot{bot_token}/sendAnimation',json_data_s)
    

