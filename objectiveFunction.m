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

    % Función objetivo
    objective = mse / (psnrValue * ssimValue);

    % Crear figuras en tiempo real
    figure(1);
    clf;
    subplot(2,2,1);
    plot(mse);
    title('MSE');

    subplot(2,2,2);
    plot(psnrValue);
    title('PSNR');

    subplot(2,2,3);
    plot(ssimValue);
    title('SSIM');

    subplot(2,2,4);
    plot(objective);
    title('Función Objetivo');

    drawnow; % Actualizar las figuras
end
