import numpy as np
from utils.caos import generar_secuencia_caotica

def encriptar(mensaje):
  """
  Encripta un mensaje utilizando una secuencia caótica generada por un mapa logístico.
    
    :param mensaje: Mensaje a encriptar.
    :return: Mensaje encriptado.
  """
  mensaje_bytes = np.frombuffer(mensaje.encode(), dtype=np.uint8)
  secuencia_caotica = generar_secuencia_caotica(len(mensaje_bytes))
  
  # Aseguramos la conversión de los datos a enteros de 8 bits :v
  mensaje_bytes = mensaje_bytes.astype(np.uint8)
  secuencia_caotica = secuencia_caotica.astype(np.uint8)
    
  mensaje_encriptado = np.bitwise_xor(mensaje_bytes, secuencia_caotica)
  return mensaje_encriptado.tobytes()
  