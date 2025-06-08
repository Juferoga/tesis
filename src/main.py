# Compresión de texto
from src.compresion.comprimir import comprimir
from src.compresion.descomprimir import descomprimir

# Encriptado de texto
from src.encriptado.encriptar import xor_encriptado

# Esteganografía en señales de audio
from src.esteganografiado.esteganografiar import cargar_archivo_wav, guardar_archivo_wav, insertar_mensaje_segmento_lsb_sequential, insertar_mensaje_segmento_lsb_random
from src.esteganografiado.desesteganografiar import extraer_mensaje_segmento_lsb_sequential, extraer_mensaje_segmento_lsb_random

# Graficación de señales de audio y métricas
from src.utils.graficas import (plot_audio_waveforms, plot_audio_histograms, plot_audio_spectrograms,
                               plot_audio_difference, plot_resource_usage, plot_execution_times,
                               plot_frequency_distribution, plot_audio_waveforms_librosa, 
                               plot_attack_results, plot_attack_spectrograms)
from src.utils.metricas import (mse_psnr, distorsion, invisibilidad, entropia, correlacion_cruzada, 
                               analisis_componentes, medir_recursos, TimerContextManager)

# Generar llave de encriptación
from src.utils.caos import generar_llave

# Enums configuraciones
from src.utils.chaos_mod_enum import ChaosMod

# Ataques
from src.utils.ataques import AudioAttacks

import numpy as np
import wave
import os
import sys
import time
import argparse

def cargar_audio(ruta_audio):
  return cargar_archivo_wav(ruta_audio)

def convertir_mensaje_a_bits(mensaje):
  mensaje_en_bytes = np.array([ord(char) for char in mensaje], dtype=np.uint8)
  longitud_de_llave = len(mensaje_en_bytes)
  llave = generar_llave(
    ChaosMod.X0.value, 
    ChaosMod.R.value, 
    ChaosMod.N_WARMUP.value, 
    longitud_de_llave)
  mensaje_encriptado = xor_encriptado(mensaje_en_bytes, llave)
  mensaje_para_paso = "".join([chr(b) for b in mensaje_encriptado])
  mensaje_bits = ''.join([format(ord(char), '08b') for char in str(mensaje_para_paso)])
  return mensaje_bits, llave

def insertar_mensaje_en_audio(arreglo_audio_original, mensaje_bits, audio_total = False, sequential = True):
  if audio_total:
    arreglo_segmento_original = arreglo_audio_original
    inicio_segmento = 0
    fin_segmento = len(arreglo_audio_original)
  else:
    punto_medio = len(arreglo_audio_original) // 2
    inicio_segmento = punto_medio - 22050
    fin_segmento = punto_medio + 22050
    arreglo_segmento_original = arreglo_audio_original[inicio_segmento:fin_segmento]

  try:
    if sequential:
      arreglo_segmento_modificado = insertar_mensaje_segmento_lsb_sequential(arreglo_segmento_original, mensaje_bits)
    else:
      arreglo_segmento_modificado = insertar_mensaje_segmento_lsb_random(arreglo_segmento_original, mensaje_bits)
  except ValueError as e:
    print(f"Error: {e}")
    sys.exit(1)

  arreglo_audio_modificado = np.concatenate((arreglo_audio_original[:inicio_segmento], arreglo_segmento_modificado, arreglo_audio_original[fin_segmento:]))
  return arreglo_audio_modificado, inicio_segmento, fin_segmento

def guardar_audio_modificado(ruta_audio_modificado, arreglo_audio_modificado, params):
  guardar_archivo_wav(ruta_audio_modificado, arreglo_audio_modificado, params)

def extraer_y_verificar_mensaje(arreglo_audio_modificado, inicio_segmento, fin_segmento, mensaje_bits, llave, sequential = True):
  arreglo_segmento_extraido = arreglo_audio_modificado[inicio_segmento:fin_segmento]
  if (sequential):
    bits_extraidos, mensaje_extraido = extraer_mensaje_segmento_lsb_sequential(arreglo_segmento_extraido, len(mensaje_bits))
  else:
    bits_extraidos, mensaje_extraido = extraer_mensaje_segmento_lsb_random(arreglo_segmento_extraido, len(mensaje_bits))
  
  extraccion_correcta = mensaje_bits == bits_extraidos
  
  if extraccion_correcta:
    return bits_extraidos, mensaje_extraido
  else:
    return None, None

def desencriptar_mensaje(mensaje_extraido, llave):
  """Desencripta el mensaje extraído del audio"""
  mensaje_original_bytes = np.array([ord(c) for c in mensaje_extraido], dtype=np.uint8)
  mensaje_desencriptado_bytes = xor_encriptado(mensaje_original_bytes, llave)
  mensaje_desencriptado = "".join([chr(b) for b in mensaje_desencriptado_bytes])
  return mensaje_desencriptado

def ejecutar_ataques(ruta_audio_modificado, inicio_segmento, fin_segmento, mensaje_bits_length, sequential=False):
  """Ejecutar la batería de ataques sobre el audio esteganografiado y evaluar su robustez
  
  Args:
      ruta_audio_modificado (str): Ruta del archivo de audio esteganografiado
      inicio_segmento (int): Inicio del segmento donde está oculto el mensaje 
      fin_segmento (int): Fin del segmento donde está oculto el mensaje
      mensaje_bits_length (int): Longitud en bits del mensaje oculto
      sequential (bool): Si el mensaje fue insertado secuencialmente o no
      
  Returns:
      dict: Resultados de los ataques
  """
  print("\n==============================================")
  print("INICIANDO MÓDULO DE EVALUACIÓN DE ATAQUES")
  print("==============================================")
  
  # Crear directorio para los resultados de los ataques
  output_dir = os.path.join(os.getcwd(), "attacks_output")
  
  # Inicializar el módulo de ataques
  with TimerContextManager("Inicialización módulo de ataques") as timer:
    attacks = AudioAttacks(ruta_audio_modificado, output_dir)
  
  # Ejecutar todos los ataques
  with TimerContextManager("Ejecución de ataques") as timer:
    resultados = attacks.run_all_attacks(inicio_segmento, fin_segmento, mensaje_bits_length, sequential)
  
  print("\n--- Resumen de resultados de ataques ---")
  ataques_exitosos = sum(1 for resultado in resultados.values() if resultado["exito"])
  total_ataques = len(resultados)
  print(f"Ataques superados: {ataques_exitosos} de {total_ataques} ({ataques_exitosos/total_ataques*100:.1f}%)")
  
  # Generar gráficas de resultados
  plot_attack_results(resultados)
  
  # Generar gráficas de espectrogramas para algunos ataques seleccionados
  attacked_audios = {
    "ruido_0.01": attacks.add_noise(0.01)[1],
    "mp3_64kbps": attacks.compress_decompress("mp3", 64)[1],
    "filtrado_3000Hz": attacks.low_pass_filter(3000)[1]
  }
  plot_attack_spectrograms(attacks.original_audio, attacked_audios, attacks.sr)
  
  return resultados

def main():
  # Parsear argumentos de línea de comandos
  parser = argparse.ArgumentParser(description='Esteganografía en audio con evaluación de robustez.')
  parser.add_argument('--attacks', action='store_true', help='Ejecutar módulo de ataques para evaluar la robustez')
  parser.add_argument('--sequential', action='store_true', help='Usar esteganografía secuencial (por defecto usa aleatoria)')
  args = parser.parse_args()
  
  # Variables para medir rendimiento
  section_names = []
  execution_times = []
  global_start_time = time.time()
  cpu_values = []
  memory_values = []
  timestamps = []

  # Ruta del archivo de audio
  ruta_audio = os.path.join(os.getcwd(), "data/audio_test.wav")
  
  # Registrar el uso inicial de recursos
  print("\n--- Recursos iniciales ---")
  recursos = medir_recursos()
  cpu_values.append(recursos["cpu_percent"])
  memory_values.append(recursos["memory_mb"])
  timestamps.append(0)
  
  # Cargar el audio con medición de tiempo
  with TimerContextManager("Carga de audio") as timer:
    arreglo_audio_original = cargar_audio(ruta_audio)
  section_names.append("Carga de audio")
  execution_times.append(timer.elapsed)
  
  # Registrar recursos después de cargar el audio
  recursos = medir_recursos()
  cpu_values.append(recursos["cpu_percent"])
  memory_values.append(recursos["memory_mb"])
  timestamps.append(time.time() - global_start_time)

  # Obtener parámetros del archivo de audio original
  with wave.open(ruta_audio, 'rb') as wav_file:
    params = wav_file.getparams()
    sample_rate = wav_file.getframerate()

  # Mensaje a insertar
  mensaje = """
    El día en que lo iban a matar, Santiago Nasar se levantó a las 5.30 de la mañana para esperar el buque en que llegaba el obispo. 
    Había soñado que atravesaba un bosque de higuerones donde caía una llovizna tierna, 
    y por un instante fue feliz en el sueño, 
    pero al despertar se sintió por completo salpicado de cagada de pájaros. 
    «Siempre soñaba con árboles», me dijo Plácida Linero, su madre, 
    evocando 27 años después los pormenores de aquel lunes ingrato. 
    «La semana anterior había soñado que iba solo en un avión de papel de estaño que volaba sin tropezar por entre los almendros», me dijo. 
    Tenía una reputación muy bien ganada de interprete certera de los sueños ajenos, 
    siempre que se los contaran en ayunas, pero no había advertido ningún augurio aciago en esos dos sueños de su hijo, 
    ni en los otros sueños con árboles que él le había contado en las mañanas que precedieron a su muerte.
  """

  # Comprimir mensaje con medición de tiempo
  with TimerContextManager("Compresión de texto") as timer:
    mensaje_comprimido = comprimir(mensaje)
    mensaje = mensaje_comprimido
  section_names.append("Compresión de texto")
  execution_times.append(timer.elapsed)
  
  # Registrar recursos después de compresión
  recursos = medir_recursos()
  cpu_values.append(recursos["cpu_percent"])
  memory_values.append(recursos["memory_mb"])
  timestamps.append(time.time() - global_start_time)

  # Convertir mensaje a bits y encriptar con medición de tiempo
  with TimerContextManager("Encriptación") as timer:
    mensaje_bits, llave = convertir_mensaje_a_bits(mensaje)
  section_names.append("Encriptación")
  execution_times.append(timer.elapsed)
  
  # Registrar recursos después de encriptación
  recursos = medir_recursos()
  cpu_values.append(recursos["cpu_percent"])
  memory_values.append(recursos["memory_mb"])
  timestamps.append(time.time() - global_start_time)

  # Determinar el método de esteganografía
  sequential = args.sequential
  metodo = "secuencial" if sequential else "aleatorio"
  print(f"\nUtilizando método de esteganografía: {metodo}")

  # Insertar mensaje en el audio con medición de tiempo
  with TimerContextManager("Esteganografía") as timer:
    arreglo_audio_modificado, inicio_segmento, fin_segmento = insertar_mensaje_en_audio(arreglo_audio_original, mensaje_bits, False, sequential)
  section_names.append("Esteganografía")
  execution_times.append(timer.elapsed)
  
  # Registrar recursos después de esteganografía
  recursos = medir_recursos()
  cpu_values.append(recursos["cpu_percent"])
  memory_values.append(recursos["memory_mb"])
  timestamps.append(time.time() - global_start_time)

  # Guardar el archivo de audio modificado con medición de tiempo
  ruta_audio_modificado = os.path.join(os.getcwd(), "data/audio_test_modificado.wav")
  with TimerContextManager("Guardar audio") as timer:
    guardar_audio_modificado(ruta_audio_modificado, arreglo_audio_modificado, params)
  section_names.append("Guardar audio")
  execution_times.append(timer.elapsed)
  
  # Registrar recursos después de guardar audio
  recursos = medir_recursos()
  cpu_values.append(recursos["cpu_percent"])
  memory_values.append(recursos["memory_mb"])
  timestamps.append(time.time() - global_start_time)

  # Extraer y verificar el mensaje con medición de tiempo
  with TimerContextManager("Extracción mensaje") as timer:
    bits_extraidos, mensaje_extraido = extraer_y_verificar_mensaje(arreglo_audio_modificado, inicio_segmento, fin_segmento, mensaje_bits, llave, sequential)
  section_names.append("Extracción mensaje")
  execution_times.append(timer.elapsed)
  
  # Registrar recursos después de extraer mensaje
  recursos = medir_recursos()
  cpu_values.append(recursos["cpu_percent"])
  memory_values.append(recursos["memory_mb"])
  timestamps.append(time.time() - global_start_time)
  
  if bits_extraidos is not None and mensaje_extraido is not None:
    # Desencriptar mensaje con medición de tiempo
    with TimerContextManager("Desencriptación") as timer:
      mensaje_desencriptado = desencriptar_mensaje(mensaje_extraido, llave)
    section_names.append("Desencriptación")
    execution_times.append(timer.elapsed)
    
    # Registrar recursos después de desencriptación
    recursos = medir_recursos()
    cpu_values.append(recursos["cpu_percent"])
    memory_values.append(recursos["memory_mb"])
    timestamps.append(time.time() - global_start_time)
    
    #print(f"\nMensaje desencriptado: {mensaje_desencriptado}")
    with TimerContextManager("Descompresión") as timer:
      mensaje_descomprimido = descomprimir(mensaje_comprimido)
    section_names.append("Descompresión")
    execution_times.append(timer.elapsed)
    #print(f"Mensaje descomprimido: {mensaje_descomprimido}")
  else:
    print("Error al extraer el mensaje.")
  
  # Registrar recursos después de descompresión
  recursos = medir_recursos()
  cpu_values.append(recursos["cpu_percent"])
  memory_values.append(recursos["memory_mb"])
  timestamps.append(time.time() - global_start_time)

  # Tiempo de ejecución global
  global_execution_time = time.time() - global_start_time
  print(f"\nTiempo de ejecución global: {global_execution_time:.4f} segundos")

  # Métricas
  print("\n------------Métricas------------")
  mse_psnr(arreglo_audio_original, arreglo_audio_modificado)
  distorsion(arreglo_audio_original, arreglo_audio_modificado)
  invisibilidad(arreglo_audio_original, arreglo_audio_modificado)
  entropia(arreglo_audio_original, arreglo_audio_modificado)
  correlacion_cruzada(arreglo_audio_original, arreglo_audio_modificado)
  # autocorrelacion(arreglo_audio_original, arreglo_audio_modificado)
  analisis_componentes(arreglo_audio_original, arreglo_audio_modificado)

  # Imágenes (descomenta las que necesites)
  print("\n------------Visualizaciones------------")
  print("Generando gráficas...")
  
  # Visualizaciones originales
  plot_audio_waveforms(arreglo_audio_original, arreglo_audio_modificado, 0, len(arreglo_audio_original))
  plot_audio_histograms(arreglo_audio_original, arreglo_audio_modificado, 0, len(arreglo_audio_original))
  plot_audio_spectrograms(ruta_audio, ruta_audio_modificado)
  
  # Nuevas visualizaciones
  plot_audio_difference(arreglo_audio_original, arreglo_audio_modificado, 0, len(arreglo_audio_original))
  plot_resource_usage(cpu_values, memory_values, timestamps)
  plot_execution_times(section_names, execution_times)
  plot_frequency_distribution(arreglo_audio_original, arreglo_audio_modificado, sample_rate)
  plot_audio_waveforms_librosa(ruta_audio, ruta_audio_modificado)

  # Ejecutar ataques si se solicita
  if args.attacks:
    with TimerContextManager("Módulo de ataques") as timer:
      resultados_ataques = ejecutar_ataques(ruta_audio_modificado, inicio_segmento, fin_segmento, len(mensaje_bits), sequential)
    section_names.append("Módulo de ataques")
    execution_times.append(timer.elapsed)
    
  # INPRIMIR COMPILADO DE TIEMPOS DE EJECUCIÓN
  print("\n------------Tiempos de ejecución------------")
  for name, exec_time in zip(section_names, execution_times):
    print(f"{name}: {exec_time:.4f} segundos")
  print(f"Tiempo total: {global_execution_time:.4f} segundos")
  # Graficar tiempos de ejecución
  plot_execution_times(section_names, execution_times)
  print("\n------------Recursos utilizados------------")
  for i, timestamp in enumerate(timestamps):
    print(f"Tiempo {i}: {timestamp:.4f} segundos - CPU: {cpu_values[i]}% - Memoria: {memory_values[i]} MB")
  plot_resource_usage(cpu_values, memory_values, timestamps)
  print("\n------------Fin del programa------------")
if __name__ == "__main__":
  main()