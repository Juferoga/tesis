# Compresión de texto
#from compresion.comprimir import comprimir
#from compresion.descomprimir import descomprimir

# Encriptado de texto
from src.encriptado.encriptar import xor_encriptado

# Esteganografía en señales de audio
from src.esteganografiado.esteganografiar import cargar_archivo_wav, guardar_archivo_wav, insertar_mensaje_segmento_lsb
from src.esteganografiado.desesteganografiar import extraer_mensaje_segmento_lsb

# Graficación de señales de audio
from src.utils.graficas import plot_audio_waveforms

# Generar llave de encriptación
from src.utils.utils import generate_key

# Enums configuraciones
from src.utils.chaos_mod_enum import ChaosMod

import numpy as np
import wave
import os

# Cargar archivo de audio
# ruta actual usando os.getcwd()
ruta_audio = os.path.join(os.getcwd(), "data/audio_test.wav")
arreglo_audio_original = cargar_archivo_wav(ruta_audio)

# Obtener parámetros del archivo de audio original
with wave.open(ruta_audio, 'rb') as wav_file:
  params = wav_file.getparams()

# Convertir mensaje a cadena de bits
mensaje = "Juferoga"
mensaje = """ Juferoga
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam in leo ac sapien accumsan pretium non congue dolor. Nullam vitae nulla tempor, consectetur lorem viverra, bibendum neque. Nullam congue diam at ex rutrum congue. Sed nec cursus nibh. Sed finibus enim eget urna sagittis, quis sagittis urna aliquet. Vivamus hendrerit mi ut ultrices consectetur. Mauris lorem turpis, fermentum ac vestibulum quis, ornare a arcu. Sed laoreet elit ut ex faucibus interdum.

Vestibulum mauris ipsum, suscipit efficitur odio ac, pharetra interdum nibh. Donec sit amet nulla non diam convallis tincidunt ut vel urna. Maecenas commodo sollicitudin convallis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Morbi a eleifend lorem. Nam et tortor sed sem dapibus laoreet eget id ante. Nulla a ligula sit amet lorem rutrum elementum. Vestibulum pulvinar elit velit, quis hendrerit est fringilla in. Cras viverra efficitur ultricies. Vivamus porttitor hendrerit eros. Fusce ac magna tellus. Vivamus a tempus odio. Nulla facilisi. Donec dictum volutpat tellus, nec rhoncus mauris maximus et. Quisque eu urna fringilla, rutrum dui a, suscipit ex.

Aliquam posuere non metus dictum varius. Nullam at est non neque auctor tincidunt. Praesent ac consectetur elit, at hendrerit risus. In fringilla imperdiet libero. Proin at ligula tellus. Cras ipsum augue, ullamcorper nec dapibus in, auctor vel ipsum. Vestibulum euismod purus ut lacinia sodales. Ut molestie vehicula enim sit amet auctor. Vivamus felis eros, suscipit vel maximus vel, tempus a odio. Donec at libero efficitur, rutrum odio in, porta velit. Mauris vitae massa eu lorem placerat pharetra ac vitae nisi. Donec at nunc felis. Ut enim odio, luctus quis magna et, suscipit convallis purus. Duis ac consequat leo, dignissim blandit lacus. Aliquam ultricies aliquet augue. Morbi sed sapien magna.

Pellentesque lobortis euismod felis et varius. Mauris maximus eleifend vulputate. Duis interdum tincidunt mi mattis pretium. Sed ut nisl interdum, rhoncus dui sit amet, mollis dui. Aenean tempor consectetur ipsum sit amet interdum. Morbi tincidunt velit sed vestibulum pharetra. Vestibulum aliquam, enim ac elementum dictum, nulla urna dictum arcu, ac scelerisque nunc mi sit amet odio. Aenean velit justo, ullamcorper et pulvinar venenatis, ultrices vel augue. Suspendisse tempus, sem ac faucibus pellentesque, quam eros rutrum mauris, pharetra ultrices magna nisl vitae sem. In sit amet placerat metus, non finibus ante. Sed luctus, ante eu iaculis euismod, turpis metus porttitor augue, sed vehicula massa ex at ante. Morbi diam est, dapibus non imperdiet sit amet, accumsan nec arcu. Integer iaculis odio quis faucibus condimentum. Proin vitae tortor iaculis, sodales risus id, pharetra velit.

Sed venenatis sapien nec mi fermentum faucibus. Nam augue odio, cursus eget rutrum ac, consectetur vitae arcu. Sed in justo egestas, tempus quam sed, egestas tortor. Integer at lectus at quam iaculis suscipit. Nulla et molestie tortor. Duis quis augue ac tortor fringilla luctus. Nulla viverra rutrum ante. Nullam a posuere felis, eu suscipit leo.

Etiam a iaculis risus. Etiam aliquet, lectus non rutrum convallis, nisi nisl sodales diam, id lobortis ligula turpis nec ligula. Vivamus id nulla sed eros pulvinar maximus. Etiam tempor consectetur aliquam. Aenean blandit eget tortor et sodales. Curabitur consectetur blandit elit et ullamcorper. Donec sit amet dolor et est congue blandit. Sed aliquam blandit tortor nec vestibulum. Donec interdum tortor id magna ornare, ac ullamcorper ligula congue. Curabitur non elit elit. Maecenas non arcu et lectus fermentum ullamcorper at eu quam. Juferoga"""
## Compresión del mensaje


# Encriptando el mensaje
mensaje_en_bytes = np.array([ord(char) for char in mensaje], dtype=np.uint8)
longitud_de_llave = len(mensaje_en_bytes)
llave = generate_key(
  ChaosMod.X0.value, 
  ChaosMod.R.value, 
  ChaosMod.N_WARMUP.value, 
  longitud_de_llave)
mensaje_encriptado = xor_encriptado(mensaje_en_bytes, llave)

mensaje_para_paso = "".join([chr(b) for b in mensaje_encriptado])

print(f"Mensaje ENCRIPTADO: {mensaje_para_paso}")

mensaje_bits = ''.join([format(ord(char), '08b') for char in str(mensaje_para_paso)])

# Calcular el punto medio del audio en número de muestras
punto_medio = len(arreglo_audio_original) // 2

# Tomar un segmento al rededor del punto medio
inicio_segmento = punto_medio - 22050
fin_segmento = punto_medio + 22050
arreglo_segmento_original = arreglo_audio_original[inicio_segmento:fin_segmento]

# Insertar mensaje en el segmento en el bit menos significativo dentro del audio
arreglo_segmento_modificado = insertar_mensaje_segmento_lsb(arreglo_segmento_original, mensaje_bits)

# Reemplazando el segmento original con el segmento modificado
arreglo_segmento_modificado = np.concatenate((arreglo_audio_original[:inicio_segmento], arreglo_segmento_modificado, arreglo_audio_original[fin_segmento:]))

# Guardando el archivo de audio modificado
ruta_audio_modificado = os.path.join(os.getcwd(), "data/audio_test_modificado.wav")
guardar_archivo_wav(ruta_audio_modificado, arreglo_segmento_modificado, params)

## Cargar el archivo de audio modificado
arreglo_audio_modificado = cargar_archivo_wav(ruta_audio_modificado)

# Extraer mensaje del segmento modificado
arreglo_segmento_extraido = arreglo_audio_modificado[inicio_segmento:fin_segmento]

# Extraer mensaje del segmento modificado
bits_extraidos, mensaje_extraido = extraer_mensaje_segmento_lsb(arreglo_segmento_extraido, len(mensaje_bits))

# Verificar si los bits extraídos son iguales a los bits del mensaje original
extraccion_correcta = mensaje_bits == bits_extraidos

if (extraccion_correcta):
  # Desencriptar mensaje
  mensaje_original_bytes = np.array([ord(c) for c in mensaje_para_paso], dtype=np.uint8)
  mensaje_desencriptado_bytes = xor_encriptado(mensaje_original_bytes, llave)
  mensaje_desencriptado = "".join([chr(b) for b in mensaje_desencriptado_bytes])
  print(f"Mensaje desencriptado: {mensaje_desencriptado}")  

# Imágenes
#plot_audio_waveforms(arreglo_segmento_original, arreglo_segmento_modificado, 0, len(arreglo_segmento_original))
