import numpy as np
import scipy.io.wavfile as wav
import librosa
import librosa.display
import soundfile as sf
from pydub import AudioSegment
from scipy.signal import butter, lfilter

class AudioAttacks:
    def __init__(self, input_file):
        self.input_file = input_file
        self.sr, self.audio = wav.read(input_file)
    
    def add_noise(self, noise_level=0.005):
        print("Aplicando ataque de ruido...")
        noise = np.random.normal(0, noise_level, self.audio.shape)
        noisy_audio = self.audio + noise
        noisy_audio = np.clip(noisy_audio, -32768, 32767).astype(np.int16)
        output_file = "noisy_audio.wav"
        wav.write(output_file, self.sr, noisy_audio)
        return output_file
    
    def compress_decompress(self, output_format="mp3"):
        print("Aplicando ataque de compresión...")
        compressed_file = "compressed_audio.mp3"
        decompressed_file = "decompressed_audio.wav"
        
        audio = AudioSegment.from_wav(self.input_file)
        audio.export(compressed_file, format=output_format)
        
        decompressed_audio = AudioSegment.from_file(compressed_file, format=output_format)
        decompressed_audio.export(decompressed_file, format="wav")
        return decompressed_file
    
    def low_pass_filter(self, cutoff=3000, order=5):
        print("Aplicando ataque de filtrado...")
        nyquist = 0.5 * self.sr
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        filtered_audio = lfilter(b, a, self.audio)
        
        filtered_audio = np.clip(filtered_audio, -32768, 32767).astype(np.int16)
        output_file = "filtered_audio.wav"
        wav.write(output_file, self.sr, filtered_audio)
        return output_file