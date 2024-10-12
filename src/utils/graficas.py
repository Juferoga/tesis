import matplotlib.pyplot as plt

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