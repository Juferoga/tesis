def get_least_significant_bits(segment_array, num_bits=1):
  least_significant_bits = [format(sample, 'b')[-num_bits:] for sample in segment_array]
  return least_significant_bits

def bytes_to_bits(byte_array):
  return ''.join([format(byte, '08b') for byte in byte_array])