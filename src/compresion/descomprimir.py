from ollama import chat
from ollama import ChatResponse

def descomprimir(mensaje_comprimido):
  print("\n:::::MENSAJE:::::\n", mensaje_comprimido)

  response: ChatResponse = chat(
    model='gemma2:27b',
    messages=[
      {
        'role': 'user',
        'content': 'Give me the reconstruction of the following message, only the reconstruction: '+mensaje_comprimido,
      },
    ]
  )

  print("::::RESPUESTA::::\n",response['message']['content'])
  return response['message']['content']
