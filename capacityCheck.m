function isCapable = capacityCheck(aud_file_path, img_file_path)
    
    disp(aud_file_path)
    disp(img_file_path)
    
    % Capacidad máxima que se permite para la imagen como porcentaje del tamaño del audio
    maxCapacityRatio = 1;

    % Obtener información del archivo de audio
    audioInfo = audioinfo(aud_file_path);
    audioSize = audioInfo.TotalSamples * audioInfo.BitsPerSample / 8; % Tamaño en bytes

    % Obtener información del archivo de imagen
    imgInfo = imfinfo(img_file_path);
    imageSize = imgInfo.FileSize; % Tamaño en bytes

    % Verificar si el tamaño de la imagen es menor que el porcentaje permitido del tamaño del audio
    isCapable = (imageSize <= maxCapacityRatio * audioSize);
    
end
