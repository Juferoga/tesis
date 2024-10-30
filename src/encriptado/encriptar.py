import numpy as np

def xor_encriptado(mensaje, llave):
  print("TIPO MENSAJE",type(mensaje))
  print("TIPO LLAVE",type(llave))
  return np.array([m ^ k for m, k in zip(mensaje, llave)], dtype=np.uint8)