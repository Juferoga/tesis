from src.utils.utils import get_least_significant_bits

def extraer_mensaje_segmento_lsb(segment_array, message_length, num_least_significant_bits=1):
  """Extraer un mensaje de los bits menos significativos de un arreglo de segmentos de audio. 
      Para extraer el mensaje, se obtienen los bits menos significativos de cada segmento de audio 
      y se concatenan en una cadena de bits. 
      Luego, se convierte la cadena de bits a una cadena de caracteres (mensaje).

  Args:
      segment_array (numpy.array): Arreglo de segmentos de audio con el mensaje esteganografiado
      message_length (int): Longitud del mensaje a extraer (número de caracteres)
      num_least_significant_bits (int, optional): Número de bits menos significativos a extraer de cada segmento de audio. Defaults to 1.

  Returns:
      tuple: Tupla con los bits extraídos y el mensaje extraído
  """
  # Extraer un mensaje de los bits menos significativos de un arreglo de segmentos de audio
  least_significant_bits = get_least_significant_bits(segment_array, num_least_significant_bits)
  # Obtener los bits menos significativos de cada segmento de audio y concatenarlos en una cadena de bits
  extracted_bits = ''.join(least_significant_bits[:message_length])
  # Convertir la cadena de bits a una cadena de caracteres (mensaje)
  extracted_message = ''.join([chr(int(extracted_bits[i:i+8], 2)) for i in range(0, len(extracted_bits), 8)])
  # Retornar los bits extraídos y el mensaje extraído
  return extracted_bits, extracted_message