function saveOptimizationResults(results, params, filename)
    % Guardar los resultados de la optimización en un archivo .mat
    % INPUTS:
    %   results - estructura con los resultados de la optimización
    %   params - estructura con los parámetros de configuración
    %   filename - nombre del archivo para guardar los datos

    try
        saveData = struct('results', results, 'params', params);
        save(filename, '-struct', 'saveData');
        disp(['Resultados guardados exitosamente en ' filename]);
    catch ME
        disp(['Error al guardar los resultados: ' ME.message]);
    end
end
