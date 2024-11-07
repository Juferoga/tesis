import numpy as np

def get_least_significant_bits(segment_array, num_bits=1):
  """Obtener los bits menos significativos de un arreglo de segmentos de audio, retornar una lista de cadenas de bits.

  Args:
      segment_array (array): Arreglo de segmentos de audio
      num_bits (int, optional): Número de bits menos significativos a obtener. Defaults to 1.

  Returns:
      list: Lista de cadenas de bits (str) con los bits menos significativos de cada segmento de audio.
  """
  least_significant_bits = [format(sample, 'b')[-num_bits:] for sample in segment_array]
  return least_significant_bits

def bytes_to_bits(byte_array):
  """Convertir un arreglo de bytes a una cadena de bits

  Args:
      byte_array (array): Arreglo de bytes

  Returns:
      str: Cadena de bits
  """
  return ''.join([format(byte, '08b') for byte in byte_array])