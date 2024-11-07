import numpy as np

def xor_encriptado(mensaje, llave):
  """Encriptar un mensaje utilizando una llave mediante una operación XOR entre cada byte del mensaje y la llave.

  Args:
      mensaje (list): Mensaje a encriptar (arreglo de bytes)
      llave (list): Llave para encriptar el mensaje (arreglo de bytes)

  Returns:
      array: Arreglo de bytes de numpy con el mensaje encriptado
  """
  return np.array([m ^ k for m, k in zip(mensaje, llave)], dtype=np.uint8)