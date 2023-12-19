function objective = objectiveFunction(position)
    
    global audio_modificado
    global audio
    
    audio_modificado = audio;
    
    hide();
    
    % Ubicación, como parametro  
    
    audio = int16(audio);
    audio_modificado = int16(audio_modificado);

    % Calcula MSE
    mse = calculateMSE(audio, audio_modificado);

    % Calcula PSNR
    psnrValue = psnr(audio, audio_modificado);

    % Calcula SSIM
    ssimValue = ssim(audio, audio_modificado);

    % Calcula Entropía
    audio_modificado_double = double(audio_modificado);
    entropyValue = entropy(audio_modificado_double);

    % Función objetivo (puede necesitar ajuste en función de cómo desees equilibrar las métricas)
    objective = mse / (psnrValue * ssimValue);

    % Crear figuras en tiempo real
    figure(1);
    clf;
    
    subplot(2,3,1);
    plot(mse);
    title('MSE');

    subplot(2,3,2);
    plot(psnrValue);
    title('PSNR');

    subplot(2,3,3);
    plot(ssimValue);
    title('SSIM');

    subplot(2,3,4);
    plot(entropyValue);
    title('Entropía');
    
    subplot(2,3,5);
    plot(objective);
    title('FO');

    drawnow; % Actualizar las figuras
end
