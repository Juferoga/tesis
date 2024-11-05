from src.utils.utils import get_least_significant_bits

# Descripción: Funciones para desesteganografiar un mensaje.
def extraer_mensaje_segmento_lsb(segment_array, message_length, num_least_significant_bits=1):
  # Extraer un mensaje de los bits menos significativos de un arreglo de segmentos de audio
  least_significant_bits = get_least_significant_bits(segment_array, num_least_significant_bits)
  # Obtener los bits menos significativos de cada segmento de audio y concatenarlos en una cadena de bits
  extracted_bits = ''.join(least_significant_bits[:message_length])
  # Convertir la cadena de bits a una cadena de caracteres (mensaje)
  extracted_message = ''.join([chr(int(extracted_bits[i:i+8], 2)) for i in range(0, len(extracted_bits), 8)])
  # Retornar los bits extraídos y el mensaje extraído
  return extracted_bits, extracted_message