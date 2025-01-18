import numpy as np
from scipy.stats import chisquare, ks_2samp, mannwhitneyu
from math import log, e

# TODO: Implementar tiempos
# !13 de enero retomamos el proyecto

# función métrica MSE - PSNR de dos audios
def mse_psnr(audio_original, audio_modificado):
  """Calcular la relación señal-ruido de pico (PSNR) entre dos audios.
  docs: https://www.youtube.com/watch?v=XmPfXt9E3VI

  Args:
      audio_original (numpy.array): Arreglo de audio original
      audio_modificado (numpy.array): Arreglo de audio modificado

  Returns:
      float: Valor de la relación señal-ruido de pico (PSNR) entre los dos audios
  """
  # Calcular el error cuadrático medio (MSE)
  mse = np.mean((audio_original - audio_modificado) ** 2)
  # Calcular el valor máximo de los datos
  max_val = np.max(audio_original)
  # Calcular el PSNR
  psnr = 10 * np.log10(max_val ** 2 / mse)
  # MSE : Es el promedio de los errores al cuadrado 
  #   entre los valores originales y los valores predichos.
  # PSNR : Aplicado al audio es una medida de la 
  #   calidad de la señal de audio, que se mide en decibelios (dB).
  print(f"MSE: {mse:.2f}, PSNR: {psnr:.2f} dB")
  
  return mse, psnr

# Función calculo de distorsión de audio original y audio modificado
def distorsion(audio_original, audio_modificado):
  """Calcular la distorsión entre dos audios.

  Args:
      audio_original (numpy.array): Arreglo de audio original
      audio_modificado (numpy.array): Arreglo de audio modificado

  Returns:
      float: Valor de la distorsión entre los dos audios
  """
  # Calcular la distorsión
  dist = np.mean(np.abs(audio_original - audio_modificado))
  # Distorsión : Es la diferencia entre la señal original 
  #   y la señal de salida de un sistema de procesamiento de señales.
  print(f"Distorsión: {dist:.2f}")
  
  return dist

# función para determinar la invisibilidad del mensaje en el audio original y el audio modificado usando pruebas estadisticas (Test de chi-cuadrado y komolgorov-smirnov)
def invisibilidad(audio_original, audio_modificado):
    """Determinar la invisibilidad del mensaje en el audio original y el audio modificado utilizando pruebas estadísticas.

    Args:
        audio_original (numpy.array): Arreglo de audio original
        audio_modificado (numpy.array): Arreglo de audio modificado

    Returns:
        float: Valor de la invisibilidad del mensaje en el audio modificado
    """
    # Verificar si hay ceros en audio_modificado y reemplazarlos con un valor pequeño
    audio_modificado = np.where(audio_modificado == 0, 1e-10, audio_modificado)
    
    # Prueba de chi-cuadrado
    #  Compara dos distribuciones de frecuencias para ver si son estadísticamente diferentes. 
    #  En este caso, está comparando la distribución de valores en audio_original con la de audio_modificado.
    #? formula chi-cuadrado = sum((observed-expected)^2 / expected)
    chi2_stat, chi2_p = chisquare(audio_original, audio_modificado)
    # Prueba de Kolmogorov-Smirnov
    #  También compara dos distribuciones, pero es más sensible a diferencias en 
    #  la forma de las distribuciones, no solo en las frecuencias.
    #? formula ks = max(abs(F1(x) - F2(x)))
    ks_stat, ks_p = ks_2samp(audio_original, audio_modificado)
    # Prueba Mann-Whitney U
    #  Prueba no paramétrica que compara dos muestras independientes para determinar
    #  si una muestra proviene de una población con valores significativamente más altos
    #  que la otra muestra.
    #? formula U = n1 * n2 + (n1 * (n1 + 1)) / 2 - R1
    #? formula R1 = sum(rank1)
    #? formula rank1 = sum(i=1, n1) rank(i)
    #? formula rank(i) = 1 + sum(j=1, i-1) sign(x_i - x_j)
    #? formula sign(x) = 1 si x > 0, 0 si x = 0, -1 si x < 0
    U1, p = mannwhitneyu(audio_original, audio_modificado)
    
    print(f"Chi-cuadrado: estadístico={chi2_stat:.2f}, p-valor={chi2_p:.2f}")
    #? chi2_stat: Es el estadístico de la prueba de chi-cuadrado. 
    #   Indica cuán grande es la diferencia entre las dos distribuciones. 
    #   Un valor alto sugiere que las distribuciones son muy diferentes.
    #? chi2_p: Es el valor p de la prueba. 
    #   Indica la probabilidad de obtener un estadístico de chi-cuadrado 
    #   tan grande o más grande, asumiendo que las dos distribuciones son iguales. 
    #   Un valor p bajo (por ejemplo, menor a 0.05) sugiere que es muy improbable 
    #   que las dos distribuciones sean iguales, por lo que rechazamos la hipótesis 
    #   nula de que las distribuciones son iguales.
    print(f"Kolmogorov-Smirnov: estadístico={ks_stat:.2f}, p-valor={ks_p:.2f}")
    #? ks_stat: Es el estadístico de la prueba de Kolmogorov-Smirnov.
    #   Indica la máxima diferencia entre las funciones de distribución acumulada de las dos muestras.
    #? ks_p: Es el valor p de la prueba. 
    #   Similar al chi2_p, indica la probabilidad de obtener un estadístico de Kolmogorov-Smirnov 
    #   tan grande o más grande, asumiendo que las dos distribuciones son iguales. 
    #   Un valor p bajo sugiere que las distribuciones son diferentes.
    print(f"Mann-Whitney U: estadístico={U1:.2f}, p-valor={p:.2f}")
    #? U1: Es el estadístico de la prueba de Mann-Whitney U.
    #   Indica cuán diferente son las dos muestras.
    #? p: Es el valor p de la prueba.
    #   Similar a chi2_p y ks_p, indica la probabilidad de obtener un estadístico de Mann-Whitney U
    
    return chi2_stat, chi2_p, ks_stat, ks_p, U1, p

# función para la medición de la entropia en el audio original y el audio modificado
def entropia(audio_original, audio_modificado):
    """Calcular la entropía de dos audios.
    formula entropia = -sum(p(x) * log2(p(x)))
    
    La entropia minima es 0 y la maxima es log2(2^16) = 16
    
    basado en https://stackoverflow.com/questions/15450192/fastest-way-to-compute-entropy-in-python :)

    Args:
        audio_original (numpy.array): Arreglo de audio original
        audio_modificado (numpy.array): Arreglo de audio modificado

    Returns:
        float: Valor de la entropía de los dos audios
    """
    
    # LABELS
    n_labels_original = len(audio_original)
    n_labels_modificado = len(audio_modificado)
    
    # SESGO 
    if n_labels_original <= 1:
        return 0
    if n_labels_modificado <= 1:
        return 0
    
    # Asegúrate de que 'base_original' y 'base_mod' estén definidas antes de usarlas
    if 'base_original' not in locals():
        base_original = None
    if 'base_mod' not in locals():
        base_mod = None
    
    # RECUPERAR PROBABILIDADES
    value_original, counts_original = np.unique(audio_original, return_counts=True)
    probs_original = counts_original / n_labels_original
    n_clases_original = np.count_nonzero(probs_original)
    
    value_modificado, counts_modificado = np.unique(audio_modificado, return_counts=True)
    probs_modificado = counts_modificado / n_labels_modificado
    n_clases_modificado = np.count_nonzero(probs_modificado)
    
    # SESGO CLASES
    if n_clases_original <= 1:
        entropia_original = 0
    if n_clases_modificado <= 1:
        entropia_modificado = 0
    
    ent_original = 0
    ent_modificado = 0
    
    # CALCULAR ENTROPIA
    if base_original is None:
        base_original = e
    for i in probs_original:
        ent_original -= i * log(i, base_original)
    
    if base_mod is None:
        base_mod = e
    for i in probs_modificado:
        ent_modificado -= i * log(i, base_mod)
    
    print(f"Entropía audio original   [0,16]: {ent_original}")
    print(f"Entropía audio modificado [0,16]: {ent_modificado}")
    
    return ent_original, ent_modificado

# función para la medición de la correlación cruzada en el audio original y el audio modificado
def correlacion_cruzada(audio_original, audio_modificado):
    """Calcular la correlación cruzada entre dos audios.
    formula correlacion_cruzada = sum((x[n] - media_x) * (y[n] - media_y)) / (sqrt(sum((x[n] - media_x)^2) * sqrt(sum((y[n] - media_y)^2)))

    Args:
        audio_original (numpy.array): Arreglo de audio original
        audio_modificado (numpy.array): Arreglo de audio modificado

    Returns:
        float: Valor de la correlación cruzada entre los dos audios
    """
    # Calcular la media de los audios
    media_original = np.mean(audio_original)
    media_modificado = np.mean(audio_modificado)
    
    # Calcular la correlación cruzada
    correlacion_cruzada = np.sum((audio_original - media_original) * (audio_modificado - media_modificado)) / np.sqrt(np.sum((audio_original - media_original) ** 2) * np.sqrt(np.sum((audio_modificado - media_modificado) ** 2)))
    
    print(f"Correlación cruzada: {correlacion_cruzada:.2f}")
    
    return correlacion_cruzada

# función para determinar la autocorrelación en el audio original y el audio modificado
def autocorrelacion(audio_original, audio_modificado):
    """Calcular la autocorrelación de dos audios.

    Args:
        audio_original (numpy.array): Arreglo de audio original
        audio_modificado (numpy.array): Arreglo de audio modificado
    """
    # Calcular la autocorrelación
    autocorrelacion_original = np.correlate(audio_original, audio_original, mode='full')
    autocorrelacion_modificado = np.correlate(audio_modificado, audio_modificado, mode='full')
    
    print(f"Autocorrelación audio original: {autocorrelacion_original}")
    print(f"Autocorrelación audio modificado: {autocorrelacion_modificado}")

# función para el analisis de componentes del audio original y el audio modificado
def analisis_componentes(audio_original, audio_modificado):
    """Realizar un análisis de componentes en dos audios.

    Args:
        audio_original (numpy.array): Arreglo de audio original
        audio_modificado (numpy.array): Arreglo de audio modificado
    """
    # Calcular la media y la desviación estándar de los audios
    media_original = np.mean(audio_original)
    media_modificado = np.mean(audio_modificado)
    std_original = np.std(audio_original)
    std_modificado = np.std(audio_modificado)
    
    print(f"Media audio original: {media_original:.2f}")
    print(f"Media audio modificado: {media_modificado:.2f}")
    print(f"Desviación estándar audio original: {std_original:.2f}")
    print(f"Desviación estándar audio modificado: {std_modificado:.2f}")
