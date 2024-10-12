import numpy as np

def extraer_mensaje_segmento_lsb(segment_array, message_length, num_least_significant_bits=1):
  least_significant_bits = get_least_significant_bits(segment_array, num_least_significant_bits)
  extracted_bits = ''.join(least_significant_bits[:message_length])
  extracted_message = ''.join([chr(int(extracted_bits[i:i+8], 2)) for i in range(0, len(extracted_bits), 8)])
  return extracted_bits, extracted_message

def get_least_significant_bits(segment_array, num_bits=1):
  least_significant_bits = [format(sample, 'b')[-num_bits:] for sample in segment_array]
  return least_significant_bits