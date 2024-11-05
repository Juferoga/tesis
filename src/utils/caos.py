import numpy as np

def mapa_logistico(x, r):
  # Mapa logístico: x_{n+1} = r * x_n * (1 - x_n)
  # x: Valor actual
  # r: Parámetro de caos
  # Retornar el valor siguiente
  return r * x * (1 - x)

def generar_llave(length, x0=0.123456, r=3.999952, n_warmup=100):
  # Generar una llave aleatoria utilizando el mapa logístico
  key_bits = []
  # Inicializar el valor inicial
  x = x0
  # Calentar el sistema, descartar los primeros valores para 
  # que el sistema alcance el estado de equilibrio (caos)
  for _ in range(n_warmup):
      x = mapa_logistico(x, r)
  # Generar la llave aleatoria
  for _ in range(length * 8):  # *8 to get length in bytes
    # Calcular el siguiente valor del mapa logístico
    x = mapa_logistico(x, r)
    # Convertir el valor del mapa logístico a un bit (0 o 1)
    bit = int(x > 0.5)
    # Agregar el bit a la llave
    key_bits.append(bit)
  # Convertir los bits a bytes (para XOR con los bytes del mensaje)
  # packbits: Convierte una matriz de bits en una matriz de bytes (8 bits) (uint8)
  key = np.packbits(key_bits)[:length]
  return key