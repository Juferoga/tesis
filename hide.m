function modifiedAudio = hide()

    global audio;
    global Temp_img;
    
    % Longitud del audio y de la imagen binaria
    audioLength = numel(audio);
    imageLength = numel(Temp_img);

    % Generar la secuencia del atractor de Lorenz
    lorenzSequence = generateLorenzSequence(imageLength, audioLength);

    % Verificar si la secuencia de Lorenz excede los límites del audio
    if any(lorenzSequence < 1 | lorenzSequence > audioLength)
        error('La secuencia de Lorenz excede los límites del audio.');
    end

    % Incrustar la imagen en el audio por fragmentos
    modifiedAudio = int16(audio);
    imageBits = int16(Temp_img - '0'); % Convertir a int16

    % Tamaño del fragmento para procesar
    fragmentSize = 10000; %memoria disponible

    for i = 1:fragmentSize:imageLength
        % Calcular el final del fragmento actual
        endIdx = min(i + fragmentSize - 1, imageLength);

        % Extraer el fragmento actual de la secuencia de Lorenz y los bits de la imagen
        currentLorenz = lorenzSequence(i:endIdx);
        currentImageBits = imageBits(i:endIdx);

        % Asegurarse de que ambos arreglos tengan el mismo tamaño
        minSize = min(numel(currentLorenz), numel(currentImageBits));
        currentLorenz = currentLorenz(1:minSize);
        currentImageBits = currentImageBits(1:minSize);

        % Actualizar los bits del audio uno por uno
        for j = 1:minSize
            pos = currentLorenz(j);
            imageBit = currentImageBits(j);
            audioBit = bitget(modifiedAudio(pos), 1);
            modifiedAudio(pos) = bitset(modifiedAudio(pos), 1, bitxor(audioBit, imageBit));
        end
    end

end

function lorenzSequence = generateLorenzSequence(length, maxPos)
    % Parámetros del atractor de Lorenz
    sigma = 10;
    beta = 8/3;
    rho = 28;

    % Condiciones iniciales
    y0 = [1; 1; 1]; 

    % Resolver las ecuaciones de Lorenz
    [t,y] = ode45(@(t,y) [sigma*(y(2)-y(1)); y(1)*(rho-y(3))-y(2); y(1)*y(2)-beta*y(3)], [0, 0.1*length], y0);

    % Normalizar y escalar la secuencia
    lorenzSequence = mod(floor(mapminmax(y(:,1)', 1, maxPos)), maxPos) + 1;
end
