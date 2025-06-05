// JavaScript principal para la interfaz web de esteganografía de audio
document.addEventListener('DOMContentLoaded', function() {
    // Elementos del formulario de codificación
    const encodeForm = document.getElementById('encodeForm');
    const audioFileInput = document.getElementById('audioFile');
    const messageInput = document.getElementById('messageToHide');
    const sequentialEncodeCheckbox = document.getElementById('sequentialEncode');
    const encodeBtn = document.getElementById('encodeBtn');
    
    // Elementos del formulario de decodificación
    const decodeForm = document.getElementById('decodeForm');
    const audioFileWithMessageInput = document.getElementById('audioFileWithHiddenMessage');
    const keyIdInput = document.getElementById('keyId'); // Nuevo campo para ID de la llave
    const sequentialDecodeCheckbox = document.getElementById('sequentialDecode');
    const decodeBtn = document.getElementById('decodeBtn');
    
    // Áreas de resultados
    const processingIndicator = document.getElementById('processingIndicator');
    const resultArea = document.getElementById('resultArea');
    const messageResult = document.getElementById('messageResult');
    const extractedMessage = document.getElementById('extractedMessage');
    const errorArea = document.getElementById('errorArea');
    const errorMessage = document.getElementById('errorMessage');
    const errorDetail = document.getElementById('errorDetail');
    const errorTechnical = document.getElementById('errorTechnical');
    const errorLocation = document.getElementById('errorLocation');
    const toggleErrorDetails = document.getElementById('toggleErrorDetails');
    const downloadArea = document.getElementById('downloadArea');
    const downloadLink = document.getElementById('downloadLink');
    const downloadFilename = document.getElementById('downloadFilename');
    const playEncodedAudio = document.getElementById('playEncodedAudio');
    const audioPlayer = document.getElementById('audioPlayer');
    const metricsArea = document.getElementById('metricsArea');
    const metricsContent = document.getElementById('metricsContent');
    const timingArea = document.getElementById('timingArea');
    const sectionTimesContent = document.getElementById('sectionTimesContent');
    const resourceUsageContent = document.getElementById('resourceUsageContent');
    const plotsArea = document.getElementById('plotsArea');
    const plotsContent = document.getElementById('plotsContent');
    const closeResults = document.getElementById('closeResults');
    const processTimeEncode = document.getElementById('processTimeEncode');
    const processTimeTextEncode = document.getElementById('processTimeTextEncode');
    
    // Elementos para mostrar y copiar el ID de la llave
    const keyIdArea = document.getElementById('keyIdArea');
    const keyIdDisplay = document.getElementById('keyIdDisplay');
    const copyKeyIdBtn = document.getElementById('copyKeyId');
    
    // Tiempo máximo de espera para solicitudes (en milisegundos)
    const MAX_TIMEOUT = 300000; // 5 minutos
    
    // Mensaje de tiempo de espera cuando una operación tarda demasiado
    const TIMEOUT_MESSAGE = "La operación está tardando más de lo esperado pero sigue en proceso. Por favor, espere...";
    
    // Contador para actualizar el indicador de procesamiento
    let processingTimer;
    let processingStartTime;
    
    // Manejar envío del formulario de codificación
    encodeForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!audioFileInput.files.length) {
            showError('Debe seleccionar un archivo de audio.');
            return;
        }
        
        if (!messageInput.value.trim()) {
            showError('Debe ingresar un mensaje para ocultar.');
            return;
        }
        
        // Mostrar indicador de procesamiento
        showProcessingIndicator("Procesando audio y ocultando mensaje...");
        
        // Configurar nombre de archivo por defecto
        const currentDate = new Date();
        const defaultFilename = `audio_esteganografiado_${currentDate.getDate()}_${currentDate.getMonth()+1}_${currentDate.getFullYear()}.wav`;
        downloadFilename.value = defaultFilename;
        
        try {
            // Primero, subir el archivo de audio
            const audioFile = audioFileInput.files[0];
            const formData = new FormData();
            formData.append('file', audioFile);
            
            console.log("Enviando archivo al servidor...");
            
            let uploadResponse;
            try {
                uploadResponse = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
            } catch (fetchError) {
                console.error("Error de red al subir el archivo:", fetchError);
                throw new Error("Error de conexión al servidor. Verifique su conexión a internet.");
            }
            
            if (!uploadResponse.ok) {
                const errorData = await uploadResponse.json();
                console.error("Error en respuesta de subida:", errorData);
                throw new Error(errorData.error || errorData.detalle || 'Error al subir archivo');
            }
            
            const uploadData = await uploadResponse.json();
            console.log("Archivo subido correctamente:", uploadData);
            const fileId = uploadData.file_id;
            
            updateProcessingIndicator("Ocultando mensaje en el audio...");
            
            // Ahora codificar el mensaje en el audio
            const encodeFormData = new FormData();
            encodeFormData.append('file_id', fileId);
            encodeFormData.append('message', messageInput.value);
            encodeFormData.append('sequential', sequentialEncodeCheckbox.checked);
            
            console.log("Enviando solicitud de codificación...");
            
            let encodeResponse;
            try {
                encodeResponse = await fetch('/encode', {
                    method: 'POST',
                    body: encodeFormData
                });
            } catch (fetchError) {
                console.error("Error de red en codificación:", fetchError);
                throw new Error("Error de conexión al servidor durante la codificación. Verifique su conexión a internet.");
            }
            
            if (!encodeResponse.ok) {
                const errorData = await encodeResponse.json();
                console.error("Error en respuesta de codificación:", errorData);
                throw {
                    message: errorData.error || 'Error al codificar mensaje',
                    detail: errorData.detalle || 'Ocurrió un error al procesar el audio',
                    location: errorData.ubicacion || ''
                };
            }
            
            const encodeData = await encodeResponse.json();
            console.log("Codificación completada con éxito:", encodeData);
            
            // Mostrar resultados de éxito
            showEncodeResults(encodeData);
        } catch (error) {
            console.error("Error en proceso de codificación:", error);
            
            // Si es un error estructurado con detalles
            if (error.detail) {
                showDetailedError(error.message, error.detail, error.location);
            } else {
                showError(error.message || "Error desconocido durante el proceso");
            }
        } finally {
            // Ocultar el indicador de procesamiento
            hideProcessingIndicator();
        }
    });
    
    // Manejar envío del formulario de decodificación
    decodeForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!audioFileWithMessageInput.files.length) {
            showError('Debe seleccionar un archivo de audio.');
            return;
        }
        
        if (!keyIdInput.value.trim()) {
            showError('Debe ingresar el ID de la llave generada durante la codificación.');
            return;
        }
        
        // Mostrar indicador de procesamiento
        showProcessingIndicator("Extrayendo mensaje oculto del audio...");
        
        try {
            const audioFile = audioFileWithMessageInput.files[0];
            const formData = new FormData();
            formData.append('file', audioFile);
            formData.append('sequential', sequentialDecodeCheckbox.checked);
            formData.append('key_id', keyIdInput.value.trim()); // Añadir el ID de la llave al FormData
            
            console.log("Enviando archivo para decodificación...");
            
            let decodeResponse;
            try {
                decodeResponse = await fetch('/decode', {
                    method: 'POST',
                    body: formData
                });
            } catch (fetchError) {
                console.error("Error de red en decodificación:", fetchError);
                throw new Error("Error de conexión al servidor durante la decodificación. Verifique su conexión a internet.");
            }
            
            // Comprobar si la respuesta es un error
            if (!decodeResponse.ok) {
                const errorData = await decodeResponse.json();
                console.error("Error en respuesta de decodificación:", errorData);
                
                // Si la respuesta tiene estructura de detalles de error
                throw {
                    message: errorData.error || 'Error al extraer mensaje',
                    detail: errorData.detalle || 'Ocurrió un error al procesar el audio',
                    location: errorData.ubicacion || '',
                    intentos: errorData.intentos_fallidos || [],
                    processTime: errorData.processTime
                };
            }
            
            const decodeData = await decodeResponse.json();
            console.log("Decodificación completada con éxito:", decodeData);
            
            // Mostrar mensaje extraído
            showDecodeResults(decodeData);
        } catch (error) {
            console.error("Error en proceso de decodificación:", error);
            
            // Si es un error estructurado con detalles
            if (error.detail) {
                let detailMessage = error.detail;
                
                // Si hay intentos fallidos, los mostramos
                if (error.intentos && error.intentos.length > 0) {
                    detailMessage += "\n\nIntentos fallidos:";
                    error.intentos.forEach(intento => {
                        detailMessage += `\n- ${intento}`;
                    });
                }
                
                showDetailedError(error.message, detailMessage, error.location);
            } else {
                showError(error.message || "Error desconocido durante la extracción");
            }
        } finally {
            // Ocultar el indicador de procesamiento
            hideProcessingIndicator();
        }
    });
    
    // Reproducir audio codificado cuando se hace clic en el botón
    playEncodedAudio.addEventListener('click', function() {
        audioPlayer.classList.toggle('d-none');
        if (audioPlayer.classList.contains('d-none')) {
            audioPlayer.pause();
            playEncodedAudio.innerHTML = '<i class="fas fa-play me-2"></i>Reproducir Audio';
        } else {
            audioPlayer.play();
            playEncodedAudio.innerHTML = '<i class="fas fa-stop me-2"></i>Ocultar Reproductor';
        }
    });
    
    // Mostrar/ocultar detalles técnicos del error
    if (toggleErrorDetails) {
        toggleErrorDetails.addEventListener('click', function() {
            const errorLocationElement = document.getElementById('errorLocation');
            if (errorLocationElement.parentElement.classList.contains('d-none')) {
                errorLocationElement.parentElement.classList.remove('d-none');
                this.textContent = "Ocultar detalles técnicos";
            } else {
                errorLocationElement.parentElement.classList.add('d-none');
                this.textContent = "Mostrar detalles técnicos";
            }
        });
    }
    
    // Cerrar sección de resultados
    if (closeResults) {
        closeResults.addEventListener('click', function() {
            resultArea.style.display = 'none';
        });
    }
    
    // Actualizar el link de descarga cuando el usuario cambie el nombre del archivo
    if (downloadFilename) {
        downloadFilename.addEventListener('input', function() {
            const fileId = downloadLink.href.split('/').pop().split('?')[0];
            const filename = this.value.trim() || 'audio_esteganografiado.wav';
            
            // Asegurarse de que el archivo termine en .wav
            const finalFilename = filename.endsWith('.wav') ? filename : `${filename}.wav`;
            
            // Actualizar el nombre de archivo para descarga y el atributo download
            downloadLink.href = `/download/${fileId}?filename=${encodeURIComponent(finalFilename)}`;
            downloadLink.setAttribute('download', finalFilename);
        });
    }
    
    // Función para copiar el ID de la llave
    if (copyKeyIdBtn) {
        copyKeyIdBtn.addEventListener('click', function() {
            if (keyIdDisplay.value) {
                // Verificar si la API de portapapeles está disponible
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(keyIdDisplay.value)
                        .then(() => {
                            // Cambiar texto del botón temporalmente para mostrar éxito
                            const originalText = copyKeyIdBtn.innerHTML;
                            copyKeyIdBtn.innerHTML = '<i class="fas fa-check"></i> Copiado';
                            copyKeyIdBtn.classList.remove('btn-outline-secondary');
                            copyKeyIdBtn.classList.add('btn-success');
                            
                            setTimeout(() => {
                                copyKeyIdBtn.innerHTML = originalText;
                                copyKeyIdBtn.classList.remove('btn-success');
                                copyKeyIdBtn.classList.add('btn-outline-secondary');
                            }, 2000);
                        })
                        .catch(err => {
                            console.error('No se pudo copiar el texto: ', err);
                            fallbackCopy(keyIdDisplay.value);
                        });
                } else {
                    // Método alternativo si la API de clipboard no está disponible
                    fallbackCopy(keyIdDisplay.value);
                }
            }
        });
    }
    
    // Función alternativa para copiar texto cuando la API de clipboard no está disponible
    function fallbackCopy(text) {
        // Crear un área de texto temporal
        const textArea = document.createElement("textarea");
        textArea.value = text;
        
        // Asegurarse de que sea visible, pero fuera de la pantalla
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        textArea.style.top = "-999999px";
        document.body.appendChild(textArea);
        
        // Seleccionar y copiar
        textArea.focus();
        textArea.select();
        
        let successful = false;
        try {
            successful = document.execCommand('copy');
            
            if (successful) {
                // Cambiar texto del botón temporalmente para mostrar éxito
                const originalText = copyKeyIdBtn.innerHTML;
                copyKeyIdBtn.innerHTML = '<i class="fas fa-check"></i> Copiado';
                copyKeyIdBtn.classList.remove('btn-outline-secondary');
                copyKeyIdBtn.classList.add('btn-success');
                
                setTimeout(() => {
                    copyKeyIdBtn.innerHTML = originalText;
                    copyKeyIdBtn.classList.remove('btn-success');
                    copyKeyIdBtn.classList.add('btn-outline-secondary');
                }, 2000);
            } else {
                alert('No se pudo copiar el texto. Intente seleccionarlo manualmente.');
            }
        } catch (err) {
            console.error('No se pudo copiar el texto: ', err);
            alert('No se pudo copiar el texto. Intente seleccionarlo manualmente.');
        }
        
        // Limpiar
        document.body.removeChild(textArea);
    }
    
    // Función para mostrar el indicador de procesamiento
    function showProcessingIndicator(message = "Procesando, esto puede tomar varios segundos...") {
        // Guardar hora de inicio para seguimiento
        processingStartTime = Date.now();
        
        // Limpiar cualquier temporizador existente
        clearInterval(processingTimer);
        
        // Ocultar resultados anteriores durante el procesamiento
        resultArea.style.display = 'none';
        
        // Mostrar y actualizar el indicador de procesamiento
        processingIndicator.querySelector('p').textContent = message;
        processingIndicator.classList.remove('d-none');
        
        // Actualizar periódicamente el tiempo transcurrido (cada 1 segundo)
        let seconds = 0;
        processingTimer = setInterval(() => {
            seconds++;
            const timeText = seconds < 60 
                ? `${seconds} segundos...` 
                : `${Math.floor(seconds/60)} min ${seconds%60} seg...`;
            
            processingIndicator.querySelector('p').textContent = `${message} (${timeText})`;
        }, 1000);
        
        // Deshabilitar botones de formulario
        encodeBtn.disabled = true;
        decodeBtn.disabled = true;
    }
    
    // Función para actualizar el mensaje del indicador de procesamiento
    function updateProcessingIndicator(message) {
        if (!processingIndicator.classList.contains('d-none')) {
            const elapsedSeconds = Math.floor((Date.now() - processingStartTime) / 1000);
            const timeText = elapsedSeconds < 60 
                ? `${elapsedSeconds} segundos...` 
                : `${Math.floor(elapsedSeconds/60)} min ${elapsedSeconds%60} seg...`;
            
            processingIndicator.querySelector('p').textContent = `${message} (${timeText})`;
        }
    }
    
    // Función para ocultar el indicador de procesamiento
    function hideProcessingIndicator() {
        processingIndicator.classList.add('d-none');
        clearInterval(processingTimer);
        
        // Habilitar botones de formulario
        encodeBtn.disabled = false;
        decodeBtn.disabled = false;
    }
    
    // Función auxiliar para mostrar resultados de codificación
    function showEncodeResults(data) {
        // Limpiar resultados anteriores
        clearResults();
        
        // Hacer visible el área de resultados
        resultArea.style.display = 'block';
        
        // Mostrar y configurar el área del ID de la llave
        if (data.file_id) {
            keyIdArea.style.display = 'block';
            keyIdDisplay.value = data.file_id;
        } else {
            keyIdArea.style.display = 'none';
        }
        
        // Configurar enlace de descarga
        downloadArea.classList.remove('d-none');
        const filename = downloadFilename.value || `audio_esteganografiado.wav`;
        downloadLink.href = `/download/${data.file_id}?filename=${encodeURIComponent(filename)}`;
        downloadLink.setAttribute('download', filename);
        
        // Configurar reproductor de audio
        audioPlayer.src = `/download/${data.file_id}`;
        
        // Mostrar tiempo de procesamiento
        if (data.processTime) {
            processTimeEncode.classList.remove('d-none');
            const processTimeText = data.processTime >= 60 
                ? `El proceso tomó ${Math.floor(data.processTime/60)} min ${Math.round(data.processTime%60)} seg`
                : `El proceso tomó ${data.processTime} segundos`;
            processTimeTextEncode.textContent = processTimeText;
        }
        
        // Mostrar métricas
        if (data.metrics && !data.metrics.error) {
            metricsArea.classList.remove('d-none');
            displayMetrics(data.metrics);
        } else if (data.metrics && data.metrics.error) {
            const metricError = document.createElement('div');
            metricError.className = 'alert alert-warning';
            metricError.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>${data.metrics.error}`;
            metricsContent.appendChild(metricError);
            metricsArea.classList.remove('d-none');
        }

        // Mostrar información de timing y recursos
        if (data.section_times || data.resource_usage) {
            timingArea.classList.remove('d-none');
            if (data.section_times) {
                displaySectionTimes(data.section_times);
            }
            if (data.resource_usage) {
                displayResourceUsage(data.resource_usage);
            }
        }

        // Mostrar gráficas
        if (data.plots && data.plots.length > 0) {
            plotsArea.classList.remove('d-none');
            displayPlots(data.plots);
        }
        
        // Desplazar a los resultados
        resultArea.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Función auxiliar para mostrar resultados de decodificación
    function showDecodeResults(data) {
        // Limpiar resultados anteriores
        clearResults();
        
        // Hacer visible el área de resultados
        resultArea.style.display = 'block';
        messageResult.classList.remove('d-none');
        
        if (data.success) {
            extractedMessage.textContent = data.message;
            
            if (data.note) {
                const noteElem = document.createElement('div');
                noteElem.className = 'alert alert-warning mt-3';
                noteElem.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>${data.note}`;
                messageResult.appendChild(noteElem);
            }
            
            // Mostrar tiempo de procesamiento
            if (data.processTime) {
                const timeInfo = document.createElement('div');
                timeInfo.className = 'alert alert-info mt-3';
                const processTimeText = data.processTime >= 60 
                    ? `El mensaje fue extraído en ${Math.floor(data.processTime/60)} min ${Math.round(data.processTime%60)} seg`
                    : `El mensaje fue extraído en ${data.processTime} segundos`;
                timeInfo.innerHTML = `<i class="fas fa-info-circle me-2"></i>${processTimeText}`;
                messageResult.appendChild(timeInfo);
            }
        } else {
            extractedMessage.textContent = 'No se pudo extraer ningún mensaje.';
            extractedMessage.parentElement.className = 'alert alert-danger';
        }
        
        // Desplazar a los resultados
        resultArea.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Función auxiliar para mostrar métricas
    function displayMetrics(metrics) {
        metricsContent.innerHTML = '';
        
        // Crear un contenedor para métricas
        const container = document.createElement('div');
        
        // Añadir cada categoría de métrica
        for (const [category, values] of Object.entries(metrics)) {
            const metricCard = document.createElement('div');
            metricCard.className = 'metric-card';
            
            const title = document.createElement('div');
            title.className = 'metric-title';
            title.textContent = formatMetricName(category);
            metricCard.appendChild(title);
            
            const content = document.createElement('div');
            
            // Manejar diferentes formatos de métricas
            if (typeof values === 'object') {
                for (const [key, value] of Object.entries(values)) {
                    const metric = document.createElement('p');
                    metric.className = 'mb-1';
                    metric.innerHTML = `<strong>${formatMetricName(key)}:</strong> ${formatMetricValue(value)}`;
                    content.appendChild(metric);
                }
            } else {
                const metric = document.createElement('p');
                metric.className = 'mb-1';
                metric.innerHTML = `<strong>Valor:</strong> ${formatMetricValue(values)}`;
                content.appendChild(metric);
            }
            
            metricCard.appendChild(content);
            container.appendChild(metricCard);
        }
        
        metricsContent.appendChild(container);
    }
    
    // Función auxiliar para mostrar gráficas
    function displayPlots(plots) {
        plotsContent.innerHTML = '';
        
        plots.forEach(plot => {
            const col = document.createElement('div');
            col.className = 'col-md-6 plot-container';
            
            const img = document.createElement('img');
            img.src = `/plot/${plot}`;
            img.alt = formatPlotName(plot);
            img.className = 'plot-img img-fluid';
            
            const caption = document.createElement('p');
            caption.className = 'text-center';
            caption.textContent = formatPlotName(plot);
            
            col.appendChild(img);
            col.appendChild(caption);
            plotsContent.appendChild(col);
            
            // Hacer la imagen cliqueable para mostrar en tamaño completo
            img.addEventListener('click', function() {
                window.open(img.src, '_blank');
            });
        });
    }
    
    // Función auxiliar para formatear nombres de métricas
    function formatMetricName(name) {
        const translations = {
            'mse_psnr': 'MSE y PSNR',
            'distorsion': 'Distorsión',
            'invisibilidad': 'Invisibilidad',
            'entropia': 'Entropía',
            'correlacion': 'Correlación',
            'analisis': 'Análisis',
            'mse': 'Error Cuadrático Medio',
            'psnr': 'Relación Señal-Ruido Pico',
            'snr': 'Relación Señal-Ruido',
            'max_diff': 'Diferencia Máxima',
            'mean_diff': 'Diferencia Media',
            'ber': 'Tasa de Error de Bits',
            'entropy_orig': 'Entropía Original',
            'entropy_mod': 'Entropía Modificada',
            'cross_corr': 'Correlación Cruzada',
            'correlation': 'Correlación'
        };
        
        // Si existe una traducción directa, usarla
        if (translations[name.toLowerCase()]) {
            return translations[name.toLowerCase()];
        }
        
        // De lo contrario, formatear como título
        return name
            .replace(/_/g, ' ')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
    
    // Función auxiliar para formatear nombres de gráficas
    function formatPlotName(filename) {
        const translations = {
            'audio_waveforms.png': 'Formas de Onda',
            'audio_histograms.png': 'Histogramas',
            'audio_spectrograms.png': 'Espectrogramas',
            'audio_difference.png': 'Diferencia de Audio',
            'frequency_distribution.png': 'Distribución de Frecuencias',
            'audio_waveforms_librosa.png': 'Formas de Onda (Librosa)',
            'execution_times.png': 'Tiempos de Ejecución',
            'resource_usage.png': 'Uso de Recursos (CPU y Memoria)'
        };
        
        // Si existe una traducción directa, usarla
        if (translations[filename]) {
            return translations[filename];
        }
        
        // De lo contrario, formatear como título
        return filename
            .replace('.png', '')
            .replace(/_/g, ' ')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
    
    // Función auxiliar para formatear valores de métricas
    function formatMetricValue(value) {
        if (typeof value === 'number') {
            return Number.isInteger(value) ? value : value.toFixed(6);
        }
        return value;
    }
    
    // Función auxiliar para mostrar mensajes de error
    function showError(message) {
        // Limpiar resultados anteriores
        clearResults();
        
        // Hacer visible el área de resultados
        resultArea.style.display = 'block';
        errorArea.classList.remove('d-none');
        
        // Establecer mensaje de error y detalles
        errorMessage.textContent = message;
        errorDetail.textContent = '';
        errorLocation.textContent = '';
        errorTechnical.classList.add('d-none');
        
        // Desplazar a mensaje de error
        resultArea.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Función para mostrar errores detallados
    function showDetailedError(message, detail, location) {
        // Limpiar resultados anteriores
        clearResults();
        
        // Hacer visible el área de resultados
        resultArea.style.display = 'block';
        errorArea.classList.remove('d-none');
        
        // Establecer mensaje de error y detalles
        errorMessage.textContent = message;
        errorDetail.textContent = detail || '';
        
        if (location) {
            errorLocation.textContent = location;
            errorTechnical.classList.remove('d-none');
            toggleErrorDetails.textContent = "Mostrar detalles técnicos";
            errorLocation.parentElement.classList.add('d-none');
        } else {
            errorTechnical.classList.add('d-none');
        }
        
        // Desplazar a mensaje de error
        resultArea.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Función auxiliar para limpiar todas las áreas de resultados
    function clearResults() {
        // Ocultar todas las secciones de resultados
        messageResult.classList.add('d-none');
        errorArea.classList.add('d-none');
        downloadArea.classList.add('d-none');
        metricsArea.classList.add('d-none');
        timingArea.classList.add('d-none');
        plotsArea.classList.add('d-none');
        processTimeEncode.classList.add('d-none');
        
        // Resetear el área del ID de la llave
        keyIdArea.style.display = 'none';
        keyIdDisplay.value = '';
        
        // Limpiar secciones de contenido
        metricsContent.innerHTML = '';
        sectionTimesContent.innerHTML = '';
        resourceUsageContent.innerHTML = '';
        plotsContent.innerHTML = '';
        
        // Restablecer reproductor de audio
        audioPlayer.classList.add('d-none');
        audioPlayer.pause();
        audioPlayer.src = '';
        playEncodedAudio.innerHTML = '<i class="fas fa-play me-2"></i>Reproducir Audio';
    }
    
    // Función auxiliar para mostrar tiempos de ejecución por sección
    function displaySectionTimes(sectionTimes) {
        sectionTimesContent.innerHTML = '';
        
        // Crear tabla de tiempos
        const table = document.createElement('table');
        table.className = 'table table-sm table-striped';
        
        const tbody = document.createElement('tbody');
        
        // Agregar filas para cada sección
        Object.entries(sectionTimes).forEach(([sectionName, time]) => {
            const row = document.createElement('tr');
            
            const nameCell = document.createElement('td');
            nameCell.textContent = sectionName;
            nameCell.className = 'fw-medium';
            
            const timeCell = document.createElement('td');
            timeCell.textContent = `${time}s`;
            timeCell.className = 'text-end font-monospace';
            
            row.appendChild(nameCell);
            row.appendChild(timeCell);
            tbody.appendChild(row);
        });
        
        table.appendChild(tbody);
        sectionTimesContent.appendChild(table);
        
        // Calcular tiempo total
        const totalTime = Object.values(sectionTimes).reduce((sum, time) => sum + time, 0);
        const totalRow = document.createElement('div');
        totalRow.className = 'alert alert-info mt-2 mb-0';
        totalRow.innerHTML = `<strong>Tiempo Total: ${totalTime.toFixed(4)}s</strong>`;
        sectionTimesContent.appendChild(totalRow);
    }

    // Función auxiliar para mostrar uso de recursos
    function displayResourceUsage(resourceUsage) {
        resourceUsageContent.innerHTML = '';
        
        const { cpu_values, memory_values, timestamps } = resourceUsage;
        
        if (!cpu_values || !memory_values || !timestamps) {
            resourceUsageContent.innerHTML = '<p class="text-muted">No hay datos de recursos disponibles</p>';
            return;
        }
        
        // Estadísticas de CPU
        const avgCpu = (cpu_values.reduce((sum, val) => sum + val, 0) / cpu_values.length).toFixed(2);
        const maxCpu = Math.max(...cpu_values).toFixed(2);
        
        // Estadísticas de memoria
        const avgMemory = (memory_values.reduce((sum, val) => sum + val, 0) / memory_values.length).toFixed(2);
        const maxMemory = Math.max(...memory_values).toFixed(2);
        
        const statsHtml = `
            <div class="row g-2">
                <div class="col-6">
                    <div class="card bg-light">
                        <div class="card-body p-2">
                            <h6 class="card-title mb-1">CPU</h6>
                            <p class="card-text mb-0">
                                <small>Promedio: ${avgCpu}%</small><br>
                                <small>Máximo: ${maxCpu}%</small>
                            </p>
                        </div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="card bg-light">
                        <div class="card-body p-2">
                            <h6 class="card-title mb-1">Memoria</h6>
                            <p class="card-text mb-0">
                                <small>Promedio: ${avgMemory} MB</small><br>
                                <small>Máximo: ${maxMemory} MB</small>
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        resourceUsageContent.innerHTML = statsHtml;
    }
});