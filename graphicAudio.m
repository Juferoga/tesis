function graphicAudio = graphicAudio()
    % Supongamos que 'audioOriginal' y 'audioModificado' son tus señales de audio
    % y 'fs' es la frecuencia de muestreo
    [audioOriginal, fs] = audioread('archivo_sin_cambios.wav');
    [audioModificado, ~] = audioread('audio_modificado.wav');

    % Crear un vector de tiempo
    t = (0:length(audioOriginal)-1)/fs;

    % Graficar la señal de audio original
    subplot(2,1,1); % Crea el primer subgráfico
    plot(t, audioOriginal);
    title('Señal de Audio Original');
    xlabel('Tiempo (s)');
    ylabel('Amplitud');

    % Graficar la señal de audio modificado
    subplot(2,1,2); % Crea el segundo subgráfico
    plot(t, audioModificado);
    title('Señal de Audio Modificado');
    xlabel('Tiempo (s)');
    ylabel('Amplitud');
end