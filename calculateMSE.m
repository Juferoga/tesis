function mse = calculateMSE(signal1, signal2)
    % Asegúrate de que las señales tengan la misma longitud
    if length(signal1) ~= length(signal2)
        error('Las señales deben tener la misma longitud');
    end

    % Calcula el Mean Squared Error
    mse = mean((signal1 - signal2).^2);
end
