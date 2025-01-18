# Compresión de texto
#from compresion.comprimir import comprimir
#from compresion.descomprimir import descomprimir

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
  mensaje = "Juferoga"
  mensaje = """ Juferoga
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque pellentesque pulvinar urna id vestibulum. Nulla pharetra sagittis tempus. Aliquam et hendrerit leo, interdum posuere ipsum. Ut pellentesque tristique urna. Suspendisse potenti. Nullam id ex tincidunt, pellentesque arcu sed, bibendum lacus. Aliquam erat volutpat. Cras viverra eros eget sapien feugiat, in pulvinar eros maximus. In quam metus, faucibus id semper sit amet, tincidunt ac urna. Nam sodales massa sit amet magna interdum, id egestas orci lobortis. Cras vulputate imperdiet dui, sit amet hendrerit enim tempus id. Aliquam consequat elit eget ultricies malesuada. Nam nec accumsan justo, pellentesque ultrices libero. Quisque turpis quam, sagittis vitae egestas non, lacinia ac erat. Curabitur facilisis ultrices quam, ut mollis magna laoreet sed.

    Aenean sit amet auctor nulla. Integer efficitur ex congue, viverra magna non, sodales nibh. Etiam odio massa, sollicitudin pharetra lobortis eu, porta nec lectus. Nulla consectetur vel augue lacinia dignissim. In ac rutrum nibh. Sed convallis quam iaculis, dictum magna at, ullamcorper ipsum. Nullam pulvinar ultricies egestas. Vestibulum gravida lacus nec neque gravida porta. Duis quam tortor, congue vitae vehicula tempus, finibus vitae ligula. Interdum et malesuada fames ac ante ipsum primis in faucibus. Integer id rutrum nibh. Donec a ipsum in odio vestibulum mattis.

    Morbi tristique congue feugiat. Proin sit amet erat accumsan, suscipit nunc eu, efficitur nulla. Etiam at finibus dolor. Aliquam erat volutpat. Proin placerat ut dui non porttitor. Etiam quam risus, varius eu ultricies at, tempus posuere tellus. Praesent vulputate, dui ultrices suscipit vulputate, libero ipsum pretium mi, id sagittis nisi felis quis ipsum. Vivamus lobortis felis felis, id auctor sapien condimentum a. Ut vitae lorem ipsum. Proin tempus commodo elit sed maximus. Curabitur elementum quam eget sapien tincidunt, et cursus neque ornare. Proin augue libero, bibendum vitae pharetra nec, hendrerit sit amet urna.

    Donec consectetur sollicitudin tempus. Aliquam condimentum leo convallis, dictum nisl nec, commodo quam. Pellentesque lobortis sit amet nibh sed pulvinar. Etiam metus enim, auctor vitae orci eget, convallis congue ex. Nulla facilisi. Nulla rutrum tortor sapien, eu vulputate ligula fringilla dictum. Nunc euismod auctor mauris sit amet aliquet. Nulla vitae neque sit amet ipsum dignissim feugiat. In malesuada, magna at tempus porttitor, nulla erat varius nisi, a rhoncus turpis elit vitae lacus. Aliquam congue sagittis purus, nec volutpat tortor luctus non. Sed vestibulum tempor porta. Nulla volutpat ut tortor vitae dictum. Maecenas porttitor venenatis aliquet. Vivamus molestie arcu sed urna venenatis semper. Duis vitae mi et urna fermentum fringilla sed a lectus.

    Nulla luctus semper leo quis fringilla. Sed porta arcu eu dapibus interdum. Nulla sit amet mauris eu mi viverra volutpat. Mauris tortor orci, scelerisque et interdum et, tincidunt non elit. Curabitur ultrices tellus vitae tortor egestas venenatis. Aenean vitae rutrum nulla, ut pharetra neque. Sed nec tellus imperdiet, dapibus tortor a, porttitor ipsum. Etiam eget elementum est. Proin vel suscipit lacus. Cras id orci sit amet tellus consequat interdum. Morbi iaculis est quis nunc vestibulum, id venenatis quam vulputate. 
    Juferoga
  """
  mensaje_bits, llave = convertir_mensaje_a_bits(mensaje)

  # Insertar mensaje en el audio
  arreglo_audio_modificado, inicio_segmento, fin_segmento = insertar_mensaje_en_audio(arreglo_audio_original, mensaje_bits)#, False, False)

  # Guardar el archivo de audio modificado
  ruta_audio_modificado = os.path.join(os.getcwd(), "data/audio_test_modificado.wav")
  guardar_audio_modificado(ruta_audio_modificado, arreglo_audio_modificado, params)

  # Extraer y verificar el mensaje
  mensaje_desencriptado = extraer_y_verificar_mensaje(arreglo_audio_modificado, inicio_segmento, fin_segmento, mensaje_bits, llave)#, False)
  if mensaje_desencriptado:
    print(f"Mensaje desencriptado: {mensaje_desencriptado}")
  else:
    print("Error al extraer el mensaje.")

  # Imágenes
  # plot_audio_waveforms(arreglo_audio_original, arreglo_audio_modificado, 0, len(arreglo_audio_original))
  # plot_audio_histograms(arreglo_audio_original, arreglo_audio_modificado, 0, len(arreglo_audio_original))
  # plot_audio_spectrograms(ruta_audio, ruta_audio_modificado)
  
  # Métricas
  print("------------Métricas------------")
  # mse_psnr(arreglo_audio_original, arreglo_audio_modificado)
  # distorsion(arreglo_audio_original, arreglo_audio_modificado)
  invisibilidad(arreglo_audio_original, arreglo_audio_modificado)
  entropia(arreglo_audio_original, arreglo_audio_modificado)
  # correlacion_cruzada(arreglo_audio_original, arreglo_audio_modificado)
  #autocorrelacion(arreglo_audio_original, arreglo_audio_modificado)
  # analisis_componentes(arreglo_audio_original, arreglo_audio_modificado)
  

if __name__ == "__main__":
  main()