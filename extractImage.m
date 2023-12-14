function extractedImage = extractImage(audio, key, imageSize)
    % Extrae los datos de la imagen del audio esteganografiado
    % 'key' es la clave utilizada para la incrustación
    % 'imageSize' es el tamaño de la imagen original en bits

    extractedBits = zeros(1, imageSize);
    for i = 1:imageSize
        pos = mod(key(i), length(audio)) + 1;
        extractedBits(i) = bitget(audio(pos), 1) + '0';
    end

    % Convertir los bits extraídos de nuevo a formato de imagen
    extractedImage = reshape(uint8(bin2dec(reshape(char(extractedBits), 8, []))), [], []);
end