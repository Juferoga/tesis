import numpy as np

def generar_secuencia_caotica(longitud, semilla=0.5, r=3.99):
  """
  Función para generar una secuencia caótica haciendo uso de mapas logísticos. << https://www.youtube.com/watch?v=xGKDwJ-zj7k&t=935s >>
    :param longitud: Longitud de la secuencia a generar.
    :param semilla: Valor inicial para el mapa logístico.
    :param r: Parámetro de control del mapa logístico.
    :return: Secuencia caótica generada.
  """
  secuencia = np.zeros(longitud)
  secuencia[0] = semilla
  for i in range(1, longitud):
    secuencia[i] = r * secuencia[i - 1] * (1 - secuencia[i - 1])
  return secuencia