import numpy as np
from utils.caos import generar_secuencia_caotica

def desencriptar(mensaje_encriptado):
  """
  Desencripta un mensaje utilizando una secuencia caótica generada por un mapa logístico.
    
    :param mensaje_encriptado: Mensaje encriptado a desencriptar.
    :return: Mensaje desencriptado.
  """
  mensaje_bytes = np.frombuffer(mensaje_encriptado, dtype=np.uint8)
  longitud = len(mensaje_bytes)
  secuencia_caotica = generar_secuencia_caotica(longitud)
  
  # Ambos arrays del tipo np.uint8 :v
  mensaje_bytes = mensaje_bytes.astype(np.uint8)
  secuencia_caotica = secuencia_caotica.astype(np.uint8)
  
  mensaje_desencriptado = np.bitwise_xor(mensaje_bytes, secuencia_caotica)
  return mensaje_desencriptado.tobytes().decode('utf-8')