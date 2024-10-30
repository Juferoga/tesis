# Compresión de texto
#from compresion.comprimir import comprimir
#from compresion.descomprimir import descomprimir

# Encriptado de texto
from src.encriptado.encriptar import xor_encriptado
# from src.encriptado.desencriptar import desencriptar

# Esteganografía en señales de audio
from src.esteganografiado.esteganografiar import cargar_archivo_wav, guardar_archivo_wav, insertar_mensaje_segmento_lsb
from src.esteganografiado.desesteganografiar import extraer_mensaje_segmento_lsb

# Graficación de señales de audio
from src.utils.graficas import plot_audio_waveforms

# Generar llave de encriptación
from src.utils.utils import generate_key

# Enums configuraciones
from src.utils.chaos_mod_enum import ChaosMod

import numpy as np
import wave
import os

# Cargar archivo de audio
# ruta actual usando os.getcwd()
ruta_audio = os.path.join(os.getcwd(), "data/UnoPorEllas.wav")
arreglo_audio_original = cargar_archivo_wav(ruta_audio)

# Obtener parámetros del archivo de audio original
with wave.open(ruta_audio, 'rb') as wav_file:
  params = wav_file.getparams()
  print(params)

# Convertir mensaje a cadena de bits
mensaje = "Juferoga"
## Compresión del mensaje


# Encriptando el mensaje
mensaje_en_bytes = np.array([ord(char) for char in mensaje], dtype=np.uint8)
longitud_de_llave = len(mensaje_en_bytes)
llave = generate_key(
  ChaosMod.X0.value, 
  ChaosMod.R.value, 
  ChaosMod.N_WARMUP.value, 
  longitud_de_llave)
mensaje_encriptado = xor_encriptado(mensaje_en_bytes, llave)
print("TIPO MENSAJE ENCRIPTADO",type(mensaje_encriptado))
print(f"Mensaje encriptado: {mensaje_encriptado}")

mensaje_para_paso = "".join([chr(b) for b in mensaje_encriptado])
print(f"MENSAJE PARA PASO: {mensaje_para_paso}")

mensaje_bits = ''.join([format(ord(char), '08b') for char in str(mensaje_para_paso)])
print(f"Mensaje en bits: {mensaje_bits}")

# Calcular el punto medio del audio en número de muestras
punto_medio = len(arreglo_audio_original) // 2

# Tomar un segmento al rededor del punto medio
inicio_segmento = punto_medio - 22050
fin_segmento = punto_medio + 22050
arreglo_segmento_original = arreglo_audio_original[inicio_segmento:fin_segmento]

# Insertar mensaje en el segmento en el bit menos significativo dentro del audio
arreglo_segmento_modificado = insertar_mensaje_segmento_lsb(arreglo_segmento_original, mensaje_bits)

# Reemplazando el segmento original con el segmento modificado
arreglo_segmento_modificado = np.concatenate((arreglo_audio_original[:inicio_segmento], arreglo_segmento_modificado, arreglo_audio_original[fin_segmento:]))

# Guardando el archivo de audio modificado
ruta_audio_modificado = os.path.join(os.getcwd(), "data/UnoPorEllas_modificado.wav")
guardar_archivo_wav(ruta_audio_modificado, arreglo_segmento_modificado, params)

## Cargar el archivo de audio modificado
arreglo_audio_modificado = cargar_archivo_wav(ruta_audio_modificado)

# Extraer mensaje del segmento modificado
arreglo_segmento_extraido = arreglo_audio_modificado[inicio_segmento:fin_segmento]

# Extraer mensaje del segmento modificado
bits_extraidos, mensaje_extraido = extraer_mensaje_segmento_lsb(arreglo_segmento_extraido, len(mensaje_bits))

# Verificar si los bits extraídos son iguales a los bits del mensaje original
extraccion_correcta = mensaje_bits == bits_extraidos
print(f"Extracción correcta: {extraccion_correcta} \n Mensaje extraído: {mensaje_extraido}")

if (extraccion_correcta):
  # Desencriptar mensaje
  print("Mensaje encriptado: ", mensaje_extraido)
  mensaje_original_bytes = np.array([ord(c) for c in mensaje_para_paso], dtype=np.uint8)
  print("Mensaje original en bytes:", mensaje_original_bytes)
  mensaje_desencriptado_bytes = xor_encriptado(mensaje_original_bytes, llave)
  mensaje_desencriptado = "".join([chr(b) for b in mensaje_desencriptado_bytes])
  print(f"Mensaje desencriptado: {mensaje_desencriptado}")  

# Imágenes
#plot_audio_waveforms(arreglo_segmento_original, arreglo_segmento_modificado, 0, len(arreglo_segmento_original))
