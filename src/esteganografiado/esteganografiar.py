import wave
import numpy as np
from src.utils.utils import get_least_significant_bits

def cargar_archivo_wav(filename):
  with wave.open(filename, 'rb') as wav_file:
    n_frames = wav_file.getnframes()
    audio_data = wav_file.readframes(n_frames)
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
  return audio_array

def guardar_archivo_wav(filename, audio_array, params):
  with wave.open(filename, 'wb') as wav_file:
    wav_file.setparams(params)
    wav_file.writeframes(audio_array.tobytes())

def insertar_mensaje_segmento_lsb(segment_array, message_bits, num_least_significant_bits=1):
  modified_segment_array = np.copy(segment_array)
  least_significant_bits = get_least_significant_bits(segment_array, num_least_significant_bits)
  for i in range(len(message_bits)):
    sample_bin = format(segment_array[i], 'b').zfill(16)
    lsb = least_significant_bits[i]
    modified_sample_bin = sample_bin[:-len(lsb)] + message_bits[i]
    modified_sample = int(modified_sample_bin, 2)
    modified_segment_array[i] = modified_sample
  return modified_segment_array