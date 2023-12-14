addpath('libs\CODO');

clc;
clear;

% 1. Solicitar el archivo de audio para el proceso esteganográfico
[audio_file_name, path_audio] = uigetfile('*.wav', 'Seleccione el archivo de audio');
if isequal(audio_file_name, 0)
    disp('No se seleccionó ningún archivo de audio.');
    return;
end
global audio
[audio, fs] = audioread(fullfile(path_audio, audio_file_name)); 
disp(['Frecuencia de muestreo del audio: ', num2str(fs)]);

audiowrite('archivo_sin_cambios.wav', audio, fs);

% Conversión a audio mono
if size(audio, 2) > 1
    audio = mean(audio, 2);
    disp('El audio se ha convertido a formato mono.');
end

% 2. Solicitar el archivo de imagen para el proceso esteganográfico
[image_file_name, path_image] = uigetfile({'*.png'; '*.jpg'}, 'Seleccione una imagen');
if isequal(image_file_name, 0)
    disp('No se seleccionó ninguna imagen.');
    return;
end

% Concatenar y ejecutar
full_audio_path = fullfile(path_audio, audio_file_name);
full_image_path = fullfile(path_image, image_file_name);

Embed_Optimize(audio, full_audio_path, image_file_name, full_image_path);

% Definición de la función Embed_Optimize
function Temp_aud = Embed_Optimize(audio, path_audio, image, path_img)

    % Verificar la capacidad del archivo de audio para contener la imagen
    if ~capacityCheck(path_audio, path_img)
        error('Capacidad insuficiente para incrustar la imagen en el audio.');
    else
        disp('Capacidad suficiente para realizar el proceso')
    end
    
    % Conversión de la imagen a formato binario
    global Temp_img;
    
    Temp_img = binary(path_img);
    
    disp('Imagen en binario (parte)')
    disp(Temp_img)

    % Inicialización de variables para SITO
    %options = SitoOptimset(...
    %    'PopulationType', 'bitstring',...
    %    'SocietySize', 3,...
    %    'Variant', 'Osito',...
    %    'MaxIteration', 6);
    
    %disp('Opciones inicialización SITO')
    %disp(options)
    
    % Número de variables igual a la longitud de la imagen binaria
    %nvars = length(Temp_img); 

    % Uso de la función Sito para la optimización
    
    %[key, fVal] = Sito(@objectiveFunction, nvars, options);
    
    addpath('libs\CODO');

clc;
clear;

% 1. Solicitar el archivo de audio para el proceso esteganográfico
[audio_file_name, path_audio] = uigetfile('*.wav', 'Seleccione el archivo de audio');
if isequal(audio_file_name, 0)
    disp('No se seleccionó ningún archivo de audio.');
    return;
end
global audio
[audio, fs] = audioread(fullfile(path_audio, audio_file_name)); 
disp(['Frecuencia de muestreo del audio: ', num2str(fs)]);

audiowrite('archivo_sin_cambios.wav', audio, fs);

% Conversión a audio mono
if size(audio, 2) > 1
    audio = mean(audio, 2);
    disp('El audio se ha convertido a formato mono.');
end

% 2. Solicitar el archivo de imagen para el proceso esteganográfico
[image_file_name, path_image] = uigetfile({'*.png'; '*.jpg'}, 'Seleccione una imagen');
if isequal(image_file_name, 0)
    disp('No se seleccionó ninguna imagen.');
    return;
end

% Concatenar y ejecutar
full_audio_path = fullfile(path_audio, audio_file_name);
full_image_path = fullfile(path_image, image_file_name);

Embed_Optimize(audio, full_audio_path, image_file_name, full_image_path);

% Definición de la función Embed_Optimize
function Temp_aud = Embed_Optimize(audio, path_audio, image, path_img)

    % Verificar la capacidad del archivo de audio para contener la imagen
    if ~capacityCheck(path_audio, path_img)
        error('Capacidad insuficiente para incrustar la imagen en el audio.');
    else
        disp('Capacidad suficiente para realizar el proceso')
    end
    
    % Conversión de la imagen a formato binario
    global Temp_img;
    
    Temp_img = binary(path_img);
    
    disp('Imagen en binario (parte)')
    disp(Temp_img)

        % Inicialización de variables para Quasi-Newton
    options = optimoptions('fminunc', ...
        'Algorithm', 'quasi-newton', ...
        'Display', 'iter', ...
        'MaxFunctionEvaluations', 1000);

    disp('Opciones de inicialización para Quasi-Newton')
    disp(options)

    % Número de variables igual a la longitud de la imagen binaria
    nvars = length(Temp_img);

    % Punto de inicio para la optimización
    startPoint = rand(1, nvars);

    % Uso de la función fminunc para la optimización
    [key, fVal] = fminunc(@objectiveFunction, startPoint, options);

    
    % Guardar las variables en un archivo .mat
    save('resultadoSito.mat', 'key', 'fVal');

    Temp_aud = audio;
    % Guardar el audio modificado
    audiowrite('audio_modificado.wav', Temp_aud,  44100);
    disp('Audio guardado');
    
    graphicAudio();
    
    %extractedImage = extractImage(audio, key, length(Temp_img));
    % Mostrar la imagen recuperada
    %imshow(extractedImage);
    
    %title('Imagen Recuperada');
    % Guardar los resultados
    %filename = 'resultadosCODO.mat';
    %saveOptimizationResults(resultadoOptimizacion, parametrosConfiguracion, filename);
    
end
    
    % Guardar las variables en un archivo .mat
    save('resultadoSito.mat', 'key', 'fVal');

    Temp_aud = audio;
    % Guardar el audio modificado
    audiowrite('audio_modificado.wav', Temp_aud,  44100);
    disp('Audio guardado');
    
    graphicAudio();
    
    %extractedImage = extractImage(audio, key, length(Temp_img));
    % Mostrar la imagen recuperada
    %imshow(extractedImage);
    
    %title('Imagen Recuperada');
    % Guardar los resultados
    %filename = 'resultadosCODO.mat';
    %saveOptimizationResults(resultadoOptimizacion, parametrosConfiguracion, filename);
    
end