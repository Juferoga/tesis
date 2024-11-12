import numpy as np

def mapa_logistico(x=8, r=3.99):
  """Mapa logístico para generar una secuencia de números pseudoaleatorios en el rango [0, 1] utilizando un valor inicial y un parámetro de caos.
    Función utilizada: x_{n+1} = r * x_n * (1 - x_n)

  Args:
      x (int, optional): valor actual. Defaults to 8.
      r (float, optional): parámetro de caos. Defaults to 3.99.

  Returns:
      float: valor siguiente en la secuencia de números pseudoaleatorios
  """
  return r * x * (1 - x)

def generar_secuencia_aleatoria(x0, r, n_warmup, lim_inf, lim_sup):
  """Generar una secuencia aleatoria en un rango determinado sin repeticiones utilizando el mapa logístico

  Args:
      x0 (float): valor inicial del mapa logístico (rango: [0, 1])
      r (float): parámetro de caos del mapa logístico (rango: [3.57, 4])
      n_warmup (float): Número de iteraciones para calentar el sistema (alcanzar el estado de equilibrio)
      lim_inf (int): Límite inferior del rango de valores aleatorios
      lim_sup (int): Límite superior del rango de valores aleatorios

  Returns:
      array: Arreglo de valores aleatorios en el rango [lim_inf, lim_sup]
  """
  secuencia_aleatoria = []
  x = x0
  # Calentar el sistema, descartar los primeros valores para que el sistema alcance el estado de equilibrio (caos)
  for _ in range(n_warmup):
    # Calcular el siguiente valor del mapa logístico
    x = mapa_logistico(x, r)
  # Generar la secuencia aleatoria
  for _ in range(lim_inf, lim_sup):
    # Calcular el siguiente valor del mapa logístico
    x = mapa_logistico(x, r)
    # Convertir el valor del mapa logístico al rango [lim_inf, lim_sup]
    valor = lim_inf + (x * (lim_sup - lim_inf))
    # Agregar el valor a la secuencia
    secuencia_aleatoria.append(valor)
  return secuencia_aleatoria

def generar_llave(x0, r, n_warmup, length):
  """Generar una llave aleatoria utilizando el mapa logístico

  Args:
      x0 (float): valor inicial del mapa logístico (rango: [0, 1])
      r (float): parámetro de caos del mapa logístico (rango: [3.57, 4])
      n_warmup (float): Número de iteraciones para calentar el sistema (alcanzar el estado de equilibrio)
      length (int): Longitud de la llave en bytes

  Returns:
      array: Arreglo de bytes con la llave aleatoria generada por el mapa logístico.
  """
  key_bits = []
  x = x0
  # Calentar el sistema, descartar los primeros valores para que el sistema alcance el estado de equilibrio (caos)
  for _ in range(n_warmup):
    # Calcular el siguiente valor del mapa logístico
    x = mapa_logistico(x, r)
  # Generar la llave aleatoria
  for _ in range(length * 8):
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