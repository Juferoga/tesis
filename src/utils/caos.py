import numpy as np

def mapa_logistico(x, r):
  return r * x * (1 - x)

def generar_llave(length, x0=0.123456, r=3.999952, n_warmup=100):
  key_bits = []
  x = x0
  # Warm up to potentially avoid initial transient
  for _ in range(n_warmup):
      x = mapa_logistico(x, r)
  # Generate key
  for _ in range(length * 8):  # *8 to get length in bytes
      x = mapa_logistico(x, r)
      # Convert to bit
      bit = int(x > 0.5)
      key_bits.append(bit)
  # Convert bits to bytes (for XOR with message bytes)
  key = np.packbits(key_bits)[:length]
  return key