from enum import Enum

class ChaosMod(Enum):
  # Punto inicial
  X0 = 0.123456
  # Parámetro de caos
  R = 3.999952
  # Número de iteraciones para 'calentar' el sistema, 
  # descartar los primeros valores para que el sistema 
  # alcance el estado de equilibrio (caos)
  N_WARMUP = 100
  