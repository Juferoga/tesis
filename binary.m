function binaryImage = binary(img_file)
    % Leer la imagen
    img = imread(img_file);
    % Convertirla a escala de grises para simplificar la binarización
    grayImage = rgb2gray(img);
    % Convertir la imagen a un vector binario
    binaryImage = reshape(dec2bin(grayImage(:))', 1, []);
end