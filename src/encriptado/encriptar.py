import numpy as np

def xor_encriptado(mensaje, llave):
  # Realiza una operación XOR entre cada byte del mensaje y la llave
  # Devuelve un array de numpy con el resultado de la operación XOR
  return np.array([m ^ k for m, k in zip(mensaje, llave)], dtype=np.uint8)