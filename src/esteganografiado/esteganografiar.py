import wave
import numpy as np
from src.utils.utils import get_least_significant_bits
from src.utils.caos import mapa_logistico

def cargar_archivo_wav(filename):
  # Cargar archivo de audio en formato WAV y retornar un arreglo de numpy con los datos de audio
  with wave.open(filename, 'rb') as wav_file:
    # Obtener los parámetros del archivo de audio WAV
    n_frames = wav_file.getnframes()
    # Leer los datos de audio del archivo WAV
    audio_data = wav_file.readframes(n_frames)
    # Convertir los datos de audio a un arreglo de numpy con valores enteros de 16 bits
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
  return audio_array

def guardar_archivo_wav(filename, audio_array, params):
  # Guardar un arreglo de numpy con los datos de audio en un archivo WAV
  with wave.open(filename, 'wb') as wav_file:
    # Establecer los parámetros del archivo WAV (número de canales, frecuencia de muestreo, profundidad de bits, etc.)
    wav_file.setparams(params)
    # Escribir los datos de audio en el archivo WAV (convertir el arreglo de numpy a bytes)
    wav_file.writeframes(audio_array.tobytes())

def insertar_mensaje_segmento_lsb(segment_array, message_bits, num_least_significant_bits=1):
  # Insertar un mensaje en los bits menos significativos de un arreglo de segmentos de audio
  modified_segment_array = np.copy(segment_array)
  # Obtener los bits menos significativos de cada segmento de audio
  least_significant_bits = get_least_significant_bits(segment_array, num_least_significant_bits)
  for i in range(len(message_bits)):
    # Obtener el i-ésimo segmento de audio y convertirlo a binario de 16 bits
    sample_bin = format(segment_array[i], 'b').zfill(16)
    # Obtener los bits menos significativos del i-ésimo segmento de audio
    lsb = least_significant_bits[i]
    # Reemplazar el bit menos significativo del i-ésimo segmento de audio por el i-ésimo bit del mensaje
    # TODO: Por hacer
    # TODO: Agregar aleatoriedad en el guardado con base en posiciónes aleatorias en el mensaje 
    # TODO: y esa posición aleatoria del mensaje se guarda en el audio
    # TODO: La misma pero con una condición inicial diferente en el mapa logístico
    modified_sample_bin = sample_bin[:-len(lsb)] + message_bits[i]
    # Convertir el i-ésimo segmento de audio modificado a entero
    modified_sample = int(modified_sample_bin, 2)
    # Actualizar el i-ésimo segmento de audio en el arreglo de segmentos de audio modificados
    modified_segment_array[i] = modified_sample
    # if segment_array[i] != modified_sample:
    #   print(f']-----------------[{i}]------------------[')
    #   print(f"org_sample_bin: {sample_bin}")
    #   print(f"mod_sample_bin: {modified_sample_bin}")
      # print(']---------------------------------------[')
      # print(f"segment_array[i]: {segment_array[i]}")
      # print(f"modified_sample: {modified_sample}")
  return modified_segment_array