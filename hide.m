function modifiedAudio = hide()
    
    global Temp_img
    global audio_modificado
    
    % Longitud del audio y de la imagen binaria
    audioLength = numel(audio_modificado);
    imageLength = numel(Temp_img);

    % Generar la secuencia del atractor de Lorenz
    lorenzSequence = generateLorenzSequence(imageLength, audioLength);

    % Incrustar la imagen en el audio
    modifiedAudio = int16(audio_modificado);
    for i = 1:imageLength
        % Utilizar la secuencia de Lorenz para determinar la posición en el audio
        pos = lorenzSequence(i);

        % Modifica el audio en esa posición con la información de la imagen
        if pos >= 1 && pos <= audioLength
            % Aplica XOR entre el bit de la imagen y el bit del audio
            imageBit = Temp_img(i) - '0';
            audioBit = bitget(modifiedAudio(pos), 1);
            modifiedAudio(pos) = bitset(modifiedAudio(pos), 1, bitxor(audioBit, imageBit));
        else
            warning('Posición fuera de los límites del audio.');
        end
    end
end

function lorenzSequence = generateLorenzSequence(length, maxPos)
    % Parámetros del atractor de Lorenz
    sigma = 10;
    beta = 8/3;
    rho = 28;

    % Condiciones iniciales
    y0 = [1;1;1]; 

    % Resolver las ecuaciones de Lorenz
    [t,y] = ode45(@(t,y)[sigma*(y(2)-y(1)); y(1)*(rho-y(3))-y(2); y(1)*y(2)-beta*y(3)], [0 0.1*length], y0);

    % Normalizar y escalar la secuencia para que se ajuste a la longitud del audio
    lorenzSequence = mod(floor(mapminmax(y(:,1)', 1, maxPos)), maxPos) + 1;
end
