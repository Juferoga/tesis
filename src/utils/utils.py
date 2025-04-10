import numpy as np

def get_least_significant_bits(segment_array, num_bits=1):
  """Obtener los bits menos significativos de un arreglo de segmentos de audio, retornar una lista de cadenas de bits.

  Args:
      segment_array (array): Arreglo de segmentos de audio
      num_bits (int, optional): Número de bits menos significativos a obtener. Defaults to 1.

  Returns:
      list: Lista de cadenas de bits (str) con los bits menos significativos de cada segmento de audio.
  """
  try:
    # Verificar si es un array multidimensional
    if len(segment_array.shape) > 1:
      # Si el array es bidimensional (estéreo), trabajar solo con el canal izquierdo
      if segment_array.shape[1] == 2:
        segment_array = segment_array[:,0]
      
    # Asegurarse de que todos los elementos sean enteros positivos para format
    segment_array = np.abs(segment_array).astype(np.int64)
    
    # Obtener los bits menos significativos
    least_significant_bits = []
    for sample in segment_array:
      try:
        binary = format(sample, 'b')
        if len(binary) >= num_bits:
          least_significant_bits.append(binary[-num_bits:])
        else:
          # Si el número no tiene suficientes bits, rellenar con ceros
          least_significant_bits.append(binary.zfill(num_bits)[-num_bits:])
      except Exception as e:
        print(f"Error al procesar muestra {sample}: {e}")
        least_significant_bits.append('0' * num_bits)
        
    return least_significant_bits
  except Exception as e:
    print(f"Error en get_least_significant_bits: {e}")
    # Devolver un array vacío o de ceros en caso de error
    return ['0' * num_bits for _ in range(len(segment_array))]

def bytes_to_bits(byte_array):
  """Convertir un arreglo de bytes a una cadena de bits

  Args:
      byte_array (array): Arreglo de bytes

  Returns:
      str: Cadena de bits
  """
  return ''.join([format(byte, '08b') for byte in byte_array])