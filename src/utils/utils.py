import numpy as np

def get_least_significant_bits(segment_array, num_bits=1):
  # Obtener los bits menos significativos de un arreglo de segmentos de audio,
  # retornar una lista de cadenas de bits
  # segment_array: Arreglo de segmentos de audio
  # num_bits: Número de bits menos significativos a obtener
  least_significant_bits = [format(sample, 'b')[-num_bits:] for sample in segment_array]
  return least_significant_bits

def bytes_to_bits(byte_array):
  # Convertir un arreglo de bytes a una cadena de bits
  return ''.join([format(byte, '08b') for byte in byte_array])

def logistic_map(x=8, r=3.99):
  # Logistic map: x_{n+1} = r * x_n * (1 - x_n)
  # x: valor actual
  # r: parámetro de caos
  # Retornar el valor siguiente
  return r * x * (1 - x)

def generate_key(x0, r, n_warmup, length):
  # Generar una llave aleatoria utilizando el mapa logístico
  key_bits = []
  # Inicializar el valor inicial
  x = x0
  # Calentar el sistema, descartar los primeros valores para que el sistema alcance el estado de equilibrio (caos)
  for _ in range(n_warmup):
    # Calcular el siguiente valor del mapa logístico
    x = logistic_map(x, r)
  # Generar la llave aleatoria
  for _ in range(length * 8):
    # Calcular el siguiente valor del mapa logístico
    x = logistic_map(x, r)
    # Convertir el valor del mapa logístico a un bit (0 o 1)
    bit = int(x > 0.5)
    # Agregar el bit a la llave
    key_bits.append(bit)
  # Convertir los bits a bytes (para XOR con los bytes del mensaje)
  # packbits: Convierte una matriz de bits en una matriz de bytes (8 bits) (uint8)
  key = np.packbits(key_bits)[:length]
  return key