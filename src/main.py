# Compresión de texto
from src.compresion.comprimir import comprimir
from src.compresion.descomprimir import descomprimir

# Encriptado de texto
from src.encriptado.encriptar import xor_encriptado

# Esteganografía en señales de audio
from src.esteganografiado.esteganografiar import cargar_archivo_wav, guardar_archivo_wav, insertar_mensaje_segmento_lsb_sequential, insertar_mensaje_segmento_lsb_random
from src.esteganografiado.desesteganografiar import extraer_mensaje_segmento_lsb_sequential, extraer_mensaje_segmento_lsb_random

# Graficación de señales de audio y métricas
from src.utils.graficas import plot_audio_waveforms, plot_audio_histograms, plot_audio_spectrograms
from src.utils.metricas import mse_psnr, distorsion, invisibilidad, entropia, correlacion_cruzada, analisis_componentes

# Generar llave de encriptación
from src.utils.caos import generar_llave

# Enums configuraciones
from src.utils.chaos_mod_enum import ChaosMod

# Ataques
from src.utils.ataques import AudioAttacks

import numpy as np
import wave
import os
import sys

def cargar_audio(ruta_audio):
  return cargar_archivo_wav(ruta_audio)

def convertir_mensaje_a_bits(mensaje):
  mensaje_en_bytes = np.array([ord(char) for char in mensaje], dtype=np.uint8)
  longitud_de_llave = len(mensaje_en_bytes)
  llave = generar_llave(
    ChaosMod.X0.value, 
    ChaosMod.R.value, 
    ChaosMod.N_WARMUP.value, 
    longitud_de_llave)
  mensaje_encriptado = xor_encriptado(mensaje_en_bytes, llave)
  mensaje_para_paso = "".join([chr(b) for b in mensaje_encriptado])
  mensaje_bits = ''.join([format(ord(char), '08b') for char in str(mensaje_para_paso)])
  return mensaje_bits, llave

def insertar_mensaje_en_audio(arreglo_audio_original, mensaje_bits, audio_total = False, sequential = True):
  if audio_total:
    arreglo_segmento_original = arreglo_audio_original
    inicio_segmento = 0
    fin_segmento = len(arreglo_audio_original)
  else:
    punto_medio = len(arreglo_audio_original) // 2
    inicio_segmento = punto_medio - 22050
    fin_segmento = punto_medio + 22050
    arreglo_segmento_original = arreglo_audio_original[inicio_segmento:fin_segmento]

  try:
    if sequential:
      arreglo_segmento_modificado = insertar_mensaje_segmento_lsb_sequential(arreglo_segmento_original, mensaje_bits)
    else:
      arreglo_segmento_modificado = insertar_mensaje_segmento_lsb_random(arreglo_segmento_original, mensaje_bits)
  except ValueError as e:
    print(f"Error: {e}")
    sys.exit(1)

  arreglo_audio_modificado = np.concatenate((arreglo_audio_original[:inicio_segmento], arreglo_segmento_modificado, arreglo_audio_original[fin_segmento:]))
  return arreglo_audio_modificado, inicio_segmento, fin_segmento

def guardar_audio_modificado(ruta_audio_modificado, arreglo_audio_modificado, params):
  guardar_archivo_wav(ruta_audio_modificado, arreglo_audio_modificado, params)

def extraer_y_verificar_mensaje(arreglo_audio_modificado, inicio_segmento, fin_segmento, mensaje_bits, llave, sequential = True):
  arreglo_segmento_extraido = arreglo_audio_modificado[inicio_segmento:fin_segmento]
  if (sequential):
    bits_extraidos, mensaje_extraido = extraer_mensaje_segmento_lsb_sequential(arreglo_segmento_extraido, len(mensaje_bits))
  else:
    bits_extraidos, mensaje_extraido = extraer_mensaje_segmento_lsb_random(arreglo_segmento_extraido, len(mensaje_bits))
  
  extraccion_correcta = mensaje_bits == bits_extraidos
  

  if extraccion_correcta:
    mensaje_original_bytes = np.array([ord(c) for c in mensaje_extraido], dtype=np.uint8)
    mensaje_desencriptado_bytes = xor_encriptado(mensaje_original_bytes, llave)
    mensaje_desencriptado = "".join([chr(b) for b in mensaje_desencriptado_bytes])
    return mensaje_desencriptado
  else:
    return None

def main():
  # Ruta del archivo de audio
  ruta_audio = os.path.join(os.getcwd(), "data/audio_test.wav")
  arreglo_audio_original = cargar_audio(ruta_audio)

  # Obtener parámetros del archivo de audio original
  with wave.open(ruta_audio, 'rb') as wav_file:
    params = wav_file.getparams()

  # Mensaje a insertar
  mensaje = """
    In a quiet seaside town, Clara discovered a message in a bottle washed ashore.
    The note inside held a plea for help from a stranded sailor named Leo.
    Determined to assist, Clara gathered the townsfolk, and together they devised a plan.
    They repaired an old fishing boat and set out to rescue Leo.
    Upon reaching the deserted island mentioned in the note, they found Leo grateful and marooned for weeks.
    The island, though remote, was a treasure trove of beauty.
    Leo shared tales of survival, and the townsfolk shared laughter and camaraderie.
    When the rescued sailor and the townspeople returned, a newfound bond united them.
    The once quiet town transformed into a lively community, forever changed by a message in a bottle that bridged the gap between strangers.
  """

  # comprimir mensaje
  mensaje_comprimido = comprimir(mensaje)
  mensaje = mensaje_comprimido

  mensaje_bits, llave = convertir_mensaje_a_bits(mensaje)

  # Insertar mensaje en el audio
  arreglo_audio_modificado, inicio_segmento, fin_segmento = insertar_mensaje_en_audio(arreglo_audio_original, mensaje_bits, False, False)

  # Guardar el archivo de audio modificado
  ruta_audio_modificado = os.path.join(os.getcwd(), "data/audio_test_modificado.wav")
  guardar_audio_modificado(ruta_audio_modificado, arreglo_audio_modificado, params)

  # Extraer y verificar el mensaje
  mensaje_desencriptado = extraer_y_verificar_mensaje(arreglo_audio_modificado, inicio_segmento, fin_segmento, mensaje_bits, llave, False)
  if mensaje_desencriptado:
    print(f"Mensaje desencriptado: {mensaje_desencriptado}")
    mensaje_descomprimido = descomprimir(mensaje_comprimido)
    print(f"Mensaje descomprimido: {mensaje_descomprimido}")
  else:
    print("Error al extraer el mensaje.")

  # Imágenes
  #plot_audio_waveforms(arreglo_audio_original, arreglo_audio_modificado, 0, len(arreglo_audio_original))
  #plot_audio_histograms(arreglo_audio_original, arreglo_audio_modificado, 0, len(arreglo_audio_original))
  #plot_audio_spectrograms(ruta_audio, ruta_audio_modificado)
  
  # Métricas
  print("------------Métricas------------")
  mse_psnr(arreglo_audio_original, arreglo_audio_modificado)
  distorsion(arreglo_audio_original, arreglo_audio_modificado)
  invisibilidad(arreglo_audio_original, arreglo_audio_modificado)
  entropia(arreglo_audio_original, arreglo_audio_modificado)
  correlacion_cruzada(arreglo_audio_original, arreglo_audio_modificado)
  autocorrelacion(arreglo_audio_original, arreglo_audio_modificado)
  analisis_componentes(arreglo_audio_original, arreglo_audio_modificado)

  # Ataques 
  attacks = AudioAttacks(input_audio)
  

if __name__ == "__main__":
  main()