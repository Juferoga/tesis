import wave
import numpy as np
from src.utils.utils import get_least_significant_bits
from src.utils.caos import mapa_logistico

def cargar_archivo_wav(filename):
  """Cargar un archivo de audio en formato WAV y retornar un arreglo de numpy con los datos de audio.

  Args:
      filename (str): Ruta del archivo de audio en formato WAV a cargar

  Returns:
      numpy.array: Arreglo de numpy con los datos de audio del archivo WAV
  """
  with wave.open(filename, 'rb') as wav_file:
    # Obtener los parámetros del archivo de audio WAV
    n_frames = wav_file.getnframes()
    # Leer los datos de audio del archivo WAV
    audio_data = wav_file.readframes(n_frames)
    # Convertir los datos de audio a un arreglo de numpy con valores enteros de 16 bits
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
  return audio_array

def guardar_archivo_wav(filename, audio_array, params):
  """Guardar un arreglo de numpy con los datos de audio en un archivo WAV.

  Args:
      filename (str): Ruta del archivo WAV a guardar los datos de audio
      audio_array (numpy.array): Arreglo de numpy con los datos de audio a guardar
      params (any): Parámetros del archivo WAV (número de canales, frecuencia de muestreo, profundidad de bits, etc.)
  """
  with wave.open(filename, 'wb') as wav_file:
    # Establecer los parámetros del archivo WAV (número de canales, frecuencia de muestreo, profundidad de bits, etc.)
    wav_file.setparams(params)
    # Escribir los datos de audio en el archivo WAV (convertir el arreglo de numpy a bytes)
    wav_file.writeframes(audio_array.tobytes())

def insertar_mensaje_segmento_lsb_sequential(segment_array, message_bits, num_least_significant_bits=1):
  """Insertar un mensaje en los bits menos significativos de un arreglo de segmentos de audio.

  Args:
      segment_array (numpy.array): Arreglo de segmentos de audio en formato de 16 bits (int16)
      message_bits (str): Cadena de bits con el mensaje a insertar en los segmentos de audio
      num_least_significant_bits (int, optional): Número de bits menos significativos a utilizar para insertar el mensaje. Defaults to 1.

  Returns:
      numpy.array: Arreglo de segmentos de audio con el mensaje esteganografiado
  
  Raises:
      ValueError: Si el mensaje es muy largo para ser insertado en el audio
  """
  modified_segment_array = np.copy(segment_array)
  # Obtener los bits menos significativos de cada segmento de audio
  least_significant_bits = get_least_significant_bits(segment_array, num_least_significant_bits)
  print(f"Tamaño arreglo bits menos significantes: {len(least_significant_bits)}")
  print(f"Tamaño mensaje: {len(message_bits)}")
  
  if len(least_significant_bits) < len(message_bits):
    raise ValueError("El mensaje es muy largo para ser insertado en el audio")
  
  for i in range(len(message_bits)):
    # Obtener el i-ésimo segmento de audio y convertirlo a binario de 16 bits
    sample_bin = format(segment_array[i], 'b').zfill(16)
    # Obtener los bits menos significativos del i-ésimo segmento de audio
    lsb = least_significant_bits[i]
    # Reemplazar el bit menos significativo del i-ésimo segmento de audio por el i-ésimo bit del mensaje    
    modified_sample_bin = sample_bin[:-len(lsb)] + message_bits[i]
    # Convertir el i-ésimo segmento de audio modificado a entero
    modified_sample = int(modified_sample_bin, 2)
    # Actualizar el i-ésimo segmento de audio en el arreglo de segmentos de audio modificados
    modified_segment_array[i] = modified_sample
  return modified_segment_array

def insertar_mensaje_segmento_lsb_random(segment_array, message_bits, num_least_significant_bits=1):
  """Insertar un mensaje en los bits menos significativos de un arreglo de segmentos de audio.

  Args:
      segment_array (numpy.array): Arreglo de segmentos de audio en formato de 16 bits (int16)
      message_bits (str): Cadena de bits con el mensaje a insertar en los segmentos de audio
      num_least_significant_bits (int, optional): Número de bits menos significativos a utilizar para insertar el mensaje. Defaults to 1.

  Returns:
      numpy.array: Arreglo de segmentos de audio con el mensaje esteganografiado
  
  Raises:
      ValueError: Si el mensaje es muy largo para ser insertado en el audio
  """
  modified_segment_array = np.copy(segment_array)
  # Obtener los bits menos significativos de cada segmento de audio
  least_significant_bits = get_least_significant_bits(segment_array, num_least_significant_bits)
  print(f"Tamaño arreglo bits menos significantes: {len(least_significant_bits)}")
  print(f"Tamaño mensaje: {len(message_bits)}")
  
  if len(least_significant_bits) < len(message_bits):
    raise ValueError("El mensaje es muy largo para ser insertado en el audio")
  
  #  Print del mapa logístico adaptado al tamaño de bits menos significativos, permitiendo una aleatoriedad en la inserción sin repetir
  #  los valores del mapa logístico
  for i in range(len(message_bits)):
    # Posición aleatoria dada por el mapa logístico
    pos = int(mapa_logistico() * len(least_significant_bits))
    print(f"Posición: {pos}")
    # Obtener el i-ésimo segmento de audio y convertirlo a binario de 16 bits
    sample_bin = format(segment_array[pos], 'b').zfill(16)
    # Obtener los bits menos significativos del i-ésimo segmento de audio
    lsb = least_significant_bits[pos]
    # Reemplazar el bit menos significativo del i-ésimo segmento de audio por el i-ésimo bit del mensaje
    modified_sample_bin = sample_bin[:-len(lsb)] + message_bits[i]
    # Convertir el i-ésimo segmento de audio modificado a entero
    modified_sample = int(modified_sample_bin, 2)
    # Actualizar el i-ésimo segmento de audio en el arreglo de segmentos de audio modificados
    modified_segment_array[pos] = modified_sample
  return modified_segment_array