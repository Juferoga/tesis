import numpy as np

def get_least_significant_bits(segment_array, num_bits=1):
  least_significant_bits = [format(sample, 'b')[-num_bits:] for sample in segment_array]
  return least_significant_bits

def bytes_to_bits(byte_array):
  return ''.join([format(byte, '08b') for byte in byte_array])

def logistic_map(x=8, r=3.99):
  return r * x * (1 - x)

def generate_key(x0, r, n_warmup, length):
  key_bits = []
  x = x0
  for _ in range(n_warmup):
    x = logistic_map(x, r)
  for _ in range(length * 8):
    x = logistic_map(x, r)
    bit = int(x > 0.5)
    key_bits.append(bit)
  key = np.packbits(key_bits)[:length]
  return key