function extractedImage = extractImage(audio, positionsFile, imageSize)
    % Extrae los datos de la imagen del audio esteganografiado
    % 'positionsFile' es el nombre del archivo que contiene las posiciones modificadas
    % 'imageSize' es el tamaño de la imagen original en bits

    % Leer las posiciones del archivo
    fileID = fopen(positionsFile, 'r');
    positions = fscanf(fileID, '%d');
    fclose(fileID);

    % Verificar que el tamaño de 'positions' coincida con 'imageSize'
    if length(positions) ~= imageSize
        error('El tamaño de la imagen no coincide con el número de posiciones almacenadas.');
    end

    % Extraer los bits de la imagen
    extractedBits = zeros(1, imageSize);
    for i = 1:imageSize
        pos = positions(i);
        extractedBits(i) = bitget(audio(pos), 1) + '0';
    end

    % Convertir los bits extraídos de nuevo a formato de imagen
    extractedImage = reshape(uint8(bin2dec(reshape(char(extractedBits), 8, []))), [], []);
end
