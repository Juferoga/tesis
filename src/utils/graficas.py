import matplotlib.pyplot as plt
import librosa
import librosa.display
import numpy as np

# Función para realizar la gráfica del audio
def plot_audio_waveforms(original_audio, modified_audio, start_sample, end_sample):
    # Tamaño de la figura
    plt.figure(figsize=(15, 6))
    # Separación de figuras
    # Gráfica audio original
    plt.subplot(2, 1, 1)
    plt.title("Original Audio")
    plt.plot(original_audio[start_sample:end_sample])
    plt.xlabel("Sample")
    plt.ylabel("Amplitude")
    # Gráfica audio modificaado
    plt.subplot(2, 1, 2)
    plt.title("Modified Audio")
    plt.plot(modified_audio[start_sample:end_sample])
    plt.xlabel("Sample")
    plt.ylabel("Amplitude")
    # Mostrar la gráfica
    plt.tight_layout()
    plt.show()
    
# Función para realizar la gráfica de la señal de audio original y la señal de audio modificada en histogramas
def plot_audio_histograms(original_audio, modified_audio, start_sample, end_sample):
    # Tamaño de la figura
    plt.figure(figsize=(15, 6))
    # Separación de figuras
    # Histograma audio original
    plt.subplot(2, 1, 1)
    plt.title("Original Audio")
    plt.hist(original_audio[start_sample:end_sample], bins=100)
    plt.xlabel("Amplitude")
    plt.ylabel("Frequency")
    # Histograma audio modificado
    plt.subplot(2, 1, 2)
    plt.title("Modified Audio")
    plt.hist(modified_audio[start_sample:end_sample], bins=100)
    plt.xlabel("Amplitude")
    plt.ylabel("Frequency")
    # Mostrar la gráfica
    plt.tight_layout()
    plt.show()

# función para realizar la gráfica de la señal de audio original y la señal de audio modificada en espectrogramas
def plot_audio_spectrograms(original_audio_path, modified_audio_path):
    
    # Cargar los archivos de audio
    original_audio, o_sr = librosa.load(original_audio_path)
    modified_audio, m_sr = librosa.load(modified_audio_path)
    
    spectrogram_org = np.abs(librosa.stft(original_audio))
    spectrogram_mod = np.abs(librosa.stft(modified_audio))
    
    # Tamaño de la figura
    plt.figure(figsize=(15, 6))
    # Separación de figuras
    # Espectrograma audio original
    plt.subplot(2, 1, 1)
    plt.title("Original Audio")
    librosa.display.specshow(librosa.amplitude_to_db(spectrogram_org, ref=np.max), sr=o_sr, y_axis='log', x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.tight_layout()
    # Espectrograma audio modificado
    plt.subplot(2, 1, 2)
    plt.title("Modified Audio")
    librosa.display.specshow(librosa.amplitude_to_db(spectrogram_mod, ref=np.max), sr=m_sr, y_axis='log', x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.tight_layout()
    # Mostrar la gráfica
    plt.title("Spectrogram of Original and Modified Audio")
    plt.show()
    
# función para mostrar el audio original y modificado en formato de onda con librosa
def plot_audio_waveforms_librosa(original_audio_path, modified_audio_path):
    
    # Cargar los archivos de audio
    original_audio, o_sr = librosa.load(original_audio_path)
    modified_audio, m_sr = librosa.load(modified_audio_path)
    
    # Tamaño de la figura
    plt.figure(figsize=(15, 6))
    # Separación de figuras
    # Gráfica audio original
    plt.subplot(2, 1, 1)
    plt.title("Original Audio")
    librosa.display.waveshow(original_audio, sr=o_sr)
    plt.tight_layout()
    # Gráfica audio modificado
    plt.subplot(2, 1, 2)
    plt.title("Modified Audio")
    librosa.display.waveshow(modified_audio, sr=m_sr)
    plt.tight_layout()
    # Mostrar la gráfica
    plt.show()
