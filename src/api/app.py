from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import shutil
import uuid
import uvicorn
import numpy as np
from typing import Optional
import tempfile
import wave
import traceback
import logging
import time
from datetime import datetime


# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.getcwd(), 'api_errors.log'))
    ]
)
logger = logging.getLogger("audio_steganography_api")

from src.encriptado.encriptar import xor_encriptado

# Import application logic from parent modules
from src.main import (
    cargar_audio,
    convertir_mensaje_a_bits,
    insertar_mensaje_en_audio,
    guardar_audio_modificado,
    extraer_y_verificar_mensaje,
    comprimir,
    descomprimir
)

from src.utils.metricas import (
    mse_psnr, 
    distorsion, 
    invisibilidad, 
    entropia, 
    correlacion_cruzada, 
    analisis_componentes
)

from src.utils.graficas import (
    plot_audio_waveforms,
    plot_audio_histograms,
    plot_audio_spectrograms,
    plot_audio_difference,
    plot_frequency_distribution,
    plot_audio_waveforms_librosa
)

# Create FastAPI app
app = FastAPI(
    title="API de Esteganografía de Audio",
    description="API para ocultar y extraer mensajes en archivos de audio utilizando esteganografía",
    version="1.0.0"
)

# Agregar CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the absolute path of the current directory
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
TEMP_DIR = BASE_DIR / "temp"
PLOTS_DIR = Path(os.getcwd()) / "plots"

# Create temp directory if it doesn't exist
if not TEMP_DIR.exists():
    TEMP_DIR.mkdir()

# Mount static directory and templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Middleware para registrar tiempo de procesamiento
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Endpoint: {request.url.path} - Tiempo de procesamiento: {process_time:.4f} segundos")
    return response

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Renderiza la página principal con las herramientas de esteganografía"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Endpoint para manejar la subida de archivos de audio"""
    if not file.filename.endswith('.wav'):
        logger.warning(f"Intento de subir archivo no soportado: {file.filename}")
        return JSONResponse(
            status_code=400,
            content={
                "error": "Solo se admiten archivos WAV",
                "detalle": "El archivo seleccionado no tiene formato WAV. Por favor, suba un archivo de audio con extensión .wav"
            }
        )
    
    try:
        temp_file_id = str(uuid.uuid4())
        file_location = TEMP_DIR / f"{temp_file_id}.wav"
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"Archivo subido correctamente: {file.filename} (ID: {temp_file_id})")
        
        # Verificar que el archivo sea un WAV válido
        try:
            with wave.open(str(file_location), 'rb') as wav_file:
                params = wav_file.getparams()
                logger.debug(f"Parámetros del archivo: {params}")
        except Exception as e:
            os.unlink(file_location)
            logger.error(f"Archivo inválido: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Archivo WAV inválido",
                    "detalle": f"El archivo seleccionado no es un archivo WAV válido o está corrupto: {str(e)}"
                }
            )
        
        return {"filename": file.filename, "file_id": temp_file_id}
    
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.error(f"Error al subir archivo: {str(e)}\n{error_detail}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Error al procesar el archivo",
                "detalle": f"Ocurrió un error al procesar el archivo subido: {str(e)}",
                "ubicacion": error_detail
            }
        )

@app.post("/encode")
async def encode_message(
    file_id: str = Form(...),
    message: str = Form(...),
    sequential: bool = Form(False)
):
    """Endpoint para ocultar un mensaje en un archivo de audio usando esteganografía"""
    audio_path = TEMP_DIR / f"{file_id}.wav"
    
    if not audio_path.exists():
        logger.warning(f"Archivo no encontrado: {file_id}.wav")
        return JSONResponse(
            status_code=404,
            content={
                "error": "Archivo de audio no encontrado",
                "detalle": "El archivo de audio seleccionado no se encuentra en el servidor. Por favor, vuelva a subirlo."
            }
        )
    
    if not message:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Mensaje vacío",
                "detalle": "Debe ingresar un mensaje para ocultar"
            }
        )
    
    logger.info(f"Iniciando codificación de mensaje en archivo {file_id}.wav (Método: {'Secuencial' if sequential else 'Aleatorio'})")
    start_time = time.time()
    
    try:
        # Verificar que el archivo WAV sea adecuado
        try:
            arreglo_audio_original = cargar_audio(str(audio_path))
            logger.debug(f"Audio cargado correctamente: {len(arreglo_audio_original)} samples")
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.error(f"Error al cargar archivo de audio: {str(e)}\n{error_detail}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "El archivo de audio no puede ser procesado",
                    "detalle": f"No se pudo cargar el archivo de audio: {str(e)}",
                    "ubicacion": error_detail
                }
            )
        
        # Comprimir mensaje
        try:
            mensaje_comprimido = comprimir(message)
            logger.debug(f"Mensaje comprimido correctamente. Longitud original: {len(message)}, Comprimido: {len(mensaje_comprimido)}")
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.error(f"Error al comprimir mensaje: {str(e)}\n{error_detail}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Error al comprimir mensaje",
                    "detalle": f"No se pudo comprimir el mensaje: {str(e)}",
                    "ubicacion": error_detail
                }
            )
        
        # Convert message to bits and encrypt
        try:
            mensaje_bits, llave = convertir_mensaje_a_bits(mensaje_comprimido)
            logger.debug(f"Mensaje convertido a bits: {len(mensaje_bits)} bits")
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.error(f"Error al convertir mensaje a bits: {str(e)}\n{error_detail}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Error al convertir mensaje",
                    "detalle": f"No se pudo convertir el mensaje a bits: {str(e)}",
                    "ubicacion": error_detail
                }
            )
        
        # Insert message into audio
        try:
            arreglo_audio_modificado, inicio_segmento, fin_segmento = insertar_mensaje_en_audio(
                arreglo_audio_original, 
                mensaje_bits, 
                False, 
                sequential
            )
            logger.debug(f"Mensaje insertado correctamente. Segmento: {inicio_segmento}-{fin_segmento}")
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.error(f"Error al insertar mensaje en audio: {str(e)}\n{error_detail}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Error al insertar mensaje en audio",
                    "detalle": f"No se pudo ocultar el mensaje en el audio: {str(e)}",
                    "ubicacion": error_detail
                }
            )
        
        # Get original audio parameters
        with wave.open(str(audio_path), 'rb') as wav_file:
            params = wav_file.getparams()
        
        # Create a unique identifier for the encoded audio
        encoded_file_id = str(uuid.uuid4())
        output_path = TEMP_DIR / f"{encoded_file_id}.wav"
        
        # Save modified audio
        try:
            guardar_audio_modificado(str(output_path), arreglo_audio_modificado, params)
            logger.debug(f"Audio modificado guardado en: {output_path}")
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.error(f"Error al guardar audio modificado: {str(e)}\n{error_detail}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Error al guardar audio modificado",
                    "detalle": f"No se pudo guardar el audio con el mensaje oculto: {str(e)}",
                    "ubicacion": error_detail
                }
            )
        
        # Generate metrics
        try:
            metrics = {}
            
            # Handle mse_psnr which returns (mse, psnr)
            mse, psnr = mse_psnr(arreglo_audio_original, arreglo_audio_modificado)
            metrics["mse"] = mse
            metrics["psnr"] = psnr
            
            # Handle distorsion which returns a single float value
            metrics["distorsion"] = distorsion(arreglo_audio_original, arreglo_audio_modificado)
            
            # Handle invisibilidad which returns (chi2_stat, chi2_p, ks_stat, ks_p, U1, p)
            chi2_stat, chi2_p, ks_stat, ks_p, U1, p = invisibilidad(arreglo_audio_original, arreglo_audio_modificado)
            metrics["invisibilidad"] = {
                "chi2_stat": chi2_stat,
                "chi2_p": chi2_p,
                "ks_stat": ks_stat,
                "ks_p": ks_p,
                "mannwhitney_U": U1,
                "mannwhitney_p": p
            }
            
            # Handle entropia which returns (ent_original, ent_modificado)
            ent_original, ent_modificado = entropia(arreglo_audio_original, arreglo_audio_modificado)
            metrics["entropia"] = {
                "original": ent_original,
                "modificado": ent_modificado
            }
            
            # Handle correlacion_cruzada which returns a single float value
            metrics["correlacion"] = correlacion_cruzada(arreglo_audio_original, arreglo_audio_modificado)
            
            # Handle analisis_componentes which returns (media_original, media_modificado, std_original, std_modificado)
            media_original, media_modificado, std_original, std_modificado = analisis_componentes(arreglo_audio_original, arreglo_audio_modificado)
            metrics["analisis"] = {
                "media_original": media_original,
                "media_modificado": media_modificado,
                "std_original": std_original,
                "std_modificado": std_modificado
            }
            
            logger.debug("Métricas generadas correctamente")
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.warning(f"Error al generar métricas: {str(e)}\n{error_detail}")
            metrics = {"error": f"No se pudieron generar algunas métricas: {str(e)}"}
        
        # Generate visualization plots
        plots = []
        try:
            # Limpiamos las gráficas anteriores
            for plot_file in PLOTS_DIR.glob("*.png"):
                try:
                    plot_file.unlink()
                except:
                    pass
            
            try:
                plot_audio_waveforms(arreglo_audio_original, arreglo_audio_modificado, 0, len(arreglo_audio_original))
                plots.append("audio_waveforms.png")
            except Exception as e:
                logger.warning(f"Error al generar gráfica de forma de onda: {str(e)}")
            
            try:
                plot_audio_histograms(arreglo_audio_original, arreglo_audio_modificado, 0, len(arreglo_audio_original))
                plots.append("audio_histograms.png")
            except Exception as e:
                logger.warning(f"Error al generar histogramas: {str(e)}")
            
            try:
                plot_audio_spectrograms(str(audio_path), str(output_path))
                plots.append("audio_spectrograms.png")
            except Exception as e:
                logger.warning(f"Error al generar espectrogramas: {str(e)}")
            
            try:
                plot_audio_difference(arreglo_audio_original, arreglo_audio_modificado, 0, len(arreglo_audio_original))
                plots.append("audio_difference.png")
            except Exception as e:
                logger.warning(f"Error al generar gráfica de diferencia: {str(e)}")
            
            try:
                plot_frequency_distribution(arreglo_audio_original, arreglo_audio_modificado, params.framerate)
                plots.append("frequency_distribution.png")
            except Exception as e:
                logger.warning(f"Error al generar distribución de frecuencias: {str(e)}")
            
            try:
                plot_audio_waveforms_librosa(str(audio_path), str(output_path))
                plots.append("audio_waveforms_librosa.png")
            except Exception as e:
                logger.warning(f"Error al generar formas de onda librosa: {str(e)}")
                
            logger.debug(f"Gráficas generadas correctamente: {plots}")
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.warning(f"Error al generar visualizaciones: {str(e)}\n{error_detail}")
        
        # Save metadata for later extraction
        try:
            metadata_path = TEMP_DIR / f"{encoded_file_id}_metadata.txt"
            with open(metadata_path, "w") as f:
                f.write(f"{inicio_segmento}\n{fin_segmento}\n{len(mensaje_bits)}\n{sequential}")
            
            # Save key for later decryption
            key_path = TEMP_DIR / f"{encoded_file_id}_key.txt"
            np.save(key_path, llave)
            logger.debug(f"Metadatos guardados correctamente")
        except Exception as e:
            logger.warning(f"Error al guardar metadatos: {str(e)}")
        
        process_time = time.time() - start_time
        logger.info(f"Codificación completada en {process_time:.2f} segundos. ID de archivo: {encoded_file_id}")
        
        return {
            "success": True,
            "file_id": encoded_file_id,
            "metrics": metrics,
            "plots": plots,
            "sequential": sequential,
            "processTime": round(process_time, 2),
            "original_filename": os.path.basename(audio_path),
            "encoded_filename": f"audio_esteganografiado_{datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.wav"
        }
    
    except Exception as e:
        error_detail = traceback.format_exc()
        logger.error(f"Error general en proceso de codificación: {str(e)}\n{error_detail}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Error en el proceso de esteganografía",
                "detalle": f"Ocurrió un error al procesar el audio: {str(e)}",
                "ubicacion": error_detail
            }
        )

@app.get("/plot/{plot_name}")
async def get_plot(plot_name: str):
    """Devuelve una imagen de gráfica desde el directorio de plots"""
    plot_path = PLOTS_DIR / plot_name
    if not plot_path.exists():
        logger.warning(f"Gráfica no encontrada: {plot_name}")
        return JSONResponse(
            status_code=404,
            content={"error": "Gráfica no encontrada"}
        )
    logger.debug(f"Enviando gráfica: {plot_name}")
    return FileResponse(str(plot_path))

@app.get("/download/{file_id}")
async def download_file(file_id: str, filename: str = None):
    """Descarga el archivo de audio codificado"""
    file_path = TEMP_DIR / f"{file_id}.wav"
    if not file_path.exists():
        logger.warning(f"Archivo no encontrado: {file_id}.wav")
        return JSONResponse(
            status_code=404,
            content={"error": "Archivo no encontrado"}
        )
    
    download_filename = filename or f"audio_esteganografiado_{datetime.now().strftime('%d_%m_%Y_%H_%M_%S')}.wav"
    logger.debug(f"Enviando archivo para descarga: {file_id}.wav como {download_filename}")
    
    return FileResponse(
        path=str(file_path), 
        filename=download_filename, 
        media_type="audio/wav"
    )

@app.post("/decode")
async def decode_message(
    file: UploadFile = File(...),
    key_id: str = Form(...),
    sequential: bool = Form(False)
):
    """Endpoint para extraer un mensaje oculto de un archivo de audio"""
    logger.info(f"[DECODE] Iniciando decodificación para archivo={file.filename}, key_id={key_id}, sequential={sequential}")
    
    if not file.filename.endswith('.wav'):
        logger.warning(f"[DECODE] Rechazando archivo no soportado: {file.filename}")
        return JSONResponse(
            status_code=400,
            content={
                "error": "Solo se admiten archivos WAV",
                "detalle": "El archivo seleccionado no tiene formato WAV. Por favor, suba un archivo de audio con extensión .wav"
            }
        )
    
    # Verificar que existan los archivos de llave y metadatos
    metadata_path = TEMP_DIR / f"{key_id}_metadata.txt"
    key_path = TEMP_DIR / f"{key_id}_key.txt.npy"
    
    logger.debug(f"[DECODE] Verificando existencia de metadatos: {metadata_path}")
    logger.debug(f"[DECODE] Verificando existencia de llave: {key_path}")
    
    if not metadata_path.exists() or not key_path.exists():
        logger.warning(f"[DECODE] Llave o metadatos no encontrados para ID: {key_id}")
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": "Llave o metadatos no encontrados",
                "detalle": "No se encontraron los archivos de llave o metadatos para el ID proporcionado. Asegúrese de usar el ID correcto generado durante el proceso de codificación."
            }
        )
    
    start_time = time.time()
    
    try:
        # Cargar la llave para la decodificación
        logger.debug(f"[DECODE] Iniciando carga de llave desde {key_path}")
        try:
            stage_start = time.time()
            llave = np.load(key_path)
            logger.debug(f"[DECODE] Llave cargada correctamente desde {key_path}, shape: {llave.shape}, dtype: {llave.dtype} ({time.time() - stage_start:.4f}s)")
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.error(f"[DECODE] Error al cargar la llave: {str(e)}\n{error_detail}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Error al cargar la llave",
                    "detalle": f"No se pudo cargar la llave para la decodificación: {str(e)}",
                    "ubicacion": error_detail
                }
            )
        
        # Cargar los metadatos
        logger.debug(f"[DECODE] Iniciando carga de metadatos desde {metadata_path}")
        try:
            stage_start = time.time()
            with open(metadata_path, "r") as f:
                lines = f.readlines()
                inicio_segmento = int(lines[0].strip())
                fin_segmento = int(lines[1].strip())
                longitud_mensaje = int(lines[2].strip())
                secuencial_metadata = lines[3].strip().lower() == "true"
                
                # Usar el modo secuencial del metadata si es diferente del proporcionado
                if secuencial_metadata != sequential:
                    logger.warning(f"[DECODE] Modo secuencial proporcionado ({sequential}) es diferente al almacenado en metadatos ({secuencial_metadata}). Usando el valor de los metadatos.")
                    sequential = secuencial_metadata
                
                logger.debug(f"[DECODE] Metadatos cargados correctamente ({time.time() - stage_start:.4f}s): Segmento: {inicio_segmento}-{fin_segmento}, Longitud: {longitud_mensaje}, Secuencial: {sequential}")
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.error(f"[DECODE] Error al cargar los metadatos: {str(e)}\n{error_detail}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Error al cargar los metadatos",
                    "detalle": f"No se pudo cargar los metadatos para la decodificación: {str(e)}",
                    "ubicacion": error_detail
                }
            )
        
        # Guardar el archivo subido temporalmente
        temp_file_path = TEMP_DIR / f"decode_{uuid.uuid4()}.wav"
        logger.debug(f"[DECODE] Guardando archivo temporal en {temp_file_path}")
        stage_start = time.time()
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.debug(f"[DECODE] Archivo temporal guardado ({time.time() - stage_start:.4f}s)")
        
        # Cargar el archivo de audio
        logger.debug(f"[DECODE] Iniciando carga del audio desde {temp_file_path}")
        try:
            stage_start = time.time()
            arreglo_audio_modificado = cargar_audio(str(temp_file_path))
            logger.debug(f"[DECODE] Audio cargado correctamente ({time.time() - stage_start:.4f}s): {len(arreglo_audio_modificado)} samples")
        except Exception as e:
            error_detail = traceback.format_exc()
            logger.error(f"[DECODE] Error al cargar archivo de audio para decodificar: {str(e)}\n{error_detail}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "El archivo de audio no puede ser procesado",
                    "detalle": f"No se pudo cargar el archivo de audio: {str(e)}",
                    "ubicacion": error_detail
                }
            )
        
        # Validar que el archivo tenga suficientes muestras
        if len(arreglo_audio_modificado) < fin_segmento:
            logger.warning(f"[DECODE] El archivo de audio es demasiado corto para extraer el mensaje. Se esperaba al menos {fin_segmento} muestras, pero tiene {len(arreglo_audio_modificado)}")
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Archivo de audio incompatible",
                    "detalle": f"El archivo de audio es demasiado corto para extraer el mensaje (se esperaba al menos {fin_segmento} muestras, pero tiene {len(arreglo_audio_modificado)})"
                }
            )
        
        # Crear una cadena temporal de bits para la extracción
        # En main.py se pasa mensaje_bits directamente, aquí generamos una cadena de la longitud correcta
        temp_message_bits = "0" * longitud_mensaje
        logger.debug(f"[DECODE] Preparada cadena temporal de bits de longitud {longitud_mensaje}")
        
        # Extraer el mensaje usando los parámetros correctos
        logger.debug(f"[DECODE] Iniciando extracción del mensaje - modo {'secuencial' if sequential else 'aleatorio'}")
        try:
            stage_start = time.time()
            logger.debug(f"[DECODE] Parámetros de extracción: inicio={inicio_segmento}, fin={fin_segmento}, secuencial={sequential}")
            
            # Extraer segmento del audio donde se encuentra el mensaje
            arreglo_segmento_extraido = arreglo_audio_modificado[inicio_segmento:fin_segmento]
            logger.debug(f"[DECODE] Segmento extraído: {len(arreglo_segmento_extraido)} samples ({inicio_segmento}-{fin_segmento})")
            
            # Log antes de la extracción que puede ser lenta
            logger.debug(f"[DECODE] Inicia proceso de extracción y verificación...")
            
            # Extraer el mensaje directamente, similar a como se hace en main.py
            if sequential:
                from src.esteganografiado.desesteganografiar import extraer_mensaje_segmento_lsb_sequential
                bits_extraidos, mensaje_extraido = extraer_mensaje_segmento_lsb_sequential(arreglo_segmento_extraido, longitud_mensaje)
                logger.debug(f"[DECODE] Método secuencial usado para extraer {longitud_mensaje} bits")
            else:
                from src.esteganografiado.desesteganografiar import extraer_mensaje_segmento_lsb_random
                bits_extraidos, mensaje_extraido = extraer_mensaje_segmento_lsb_random(arreglo_segmento_extraido, longitud_mensaje)
                logger.debug(f"[DECODE] Método aleatorio usado para extraer {longitud_mensaje} bits")
            
            logger.debug(f"[DECODE] Bits extraídos: {len(bits_extraidos)} bits")
            
            # Verificar si la extracción fue correcta
            if not mensaje_extraido:
                logger.warning(f"[DECODE] No se pudo extraer mensaje del audio (mensaje_extraido es None)")
                process_time = time.time() - start_time
                return JSONResponse(
                    status_code=404,
                    content={
                        "success": False,
                        "error": "No se pudo extraer el mensaje",
                        "detalle": "No se pudo extraer ningún mensaje válido con los parámetros proporcionados",
                        "processTime": round(process_time, 2)
                    }
                )
            
            # Desencriptar el mensaje
            logger.debug(f"[DECODE] Mensaje extraído, procediendo a desencriptar")
            mensaje_original_bytes = np.array([ord(c) for c in mensaje_extraido], dtype=np.uint8)
            mensaje_desencriptado_bytes = xor_encriptado(mensaje_original_bytes, llave)
            mensaje_desencriptado = "".join([chr(b) for b in mensaje_desencriptado_bytes])
            logger.debug(f"[DECODE] Mensaje desencriptado correctamente, longitud: {len(mensaje_desencriptado)}")
            
            logger.debug(f"[DECODE] Extracción y desencriptación completada ({time.time() - stage_start:.4f}s)")
            
            if not mensaje_desencriptado:
                process_time = time.time() - start_time
                logger.warning(f"[DECODE] Mensaje desencriptado está vacío")
                return JSONResponse(
                    status_code=404,
                    content={
                        "success": False,
                        "error": "No se pudo extraer el mensaje",
                        "detalle": "Se extrajo un mensaje pero está vacío después de la desencriptación",
                        "processTime": round(process_time, 2)
                    }
                )
            
            # Intentar descomprimir el mensaje extraído
            try:
                logger.debug(f"[DECODE] Iniciando descompresión del mensaje")
                stage_start = time.time()
                mensaje_descomprimido = descomprimir(mensaje_desencriptado)
                logger.debug(f"[DECODE] Descompresión completada ({time.time() - stage_start:.4f}s)")
                
                process_time = time.time() - start_time
                logger.info(f"[DECODE] Mensaje extraído y descomprimido correctamente en {process_time:.2f} segundos")
                return {
                    "success": True,
                    "message": mensaje_descomprimido,
                    "processTime": round(process_time, 2)
                }
            except Exception as decomp_error:
                # Si la descompresión falla, devolvemos el mensaje sin descomprimir
                process_time = time.time() - start_time
                logger.warning(f"[DECODE] Mensaje extraído pero no se pudo descomprimir ({time.time() - stage_start:.4f}s): {str(decomp_error)}")
                return {
                    "success": True,
                    "message": mensaje_desencriptado,
                    "note": "El mensaje podría estar corrupto o no se pudo descomprimir correctamente",
                    "processTime": round(process_time, 2)
                }
                
        except Exception as e:
            error_detail = traceback.format_exc()
            process_time = time.time() - start_time
            logger.error(f"[DECODE] Error al extraer el mensaje: {str(e)}\n{error_detail}")
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Error al extraer el mensaje",
                    "detalle": f"Ocurrió un error al intentar extraer el mensaje: {str(e)}",
                    "ubicacion": error_detail,
                    "processTime": round(process_time, 2)
                }
            )
    
    except Exception as e:
        error_detail = traceback.format_exc()
        process_time = time.time() - start_time
        logger.error(f"[DECODE] Error general en proceso de decodificación: {str(e)}\n{error_detail}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Error al procesar el audio",
                "detalle": f"Ocurrió un error al intentar extraer el mensaje: {str(e)}",
                "ubicacion": error_detail,
                "processTime": round(process_time, 2)
            }
        )

@app.get("/health")
async def health_check():
    """Endpoint de verificación de estado"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.on_event("startup")
async def startup_event():
    """Se ejecuta cuando la aplicación inicia"""
    logger.info("API de Esteganografía de Audio iniciando...")
    
    # Verificar directorios
    if not PLOTS_DIR.exists():
        PLOTS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directorio de gráficas creado: {PLOTS_DIR}")

@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar"""
    logger.info("Limpiando archivos temporales...")
    # Remove all files in the temp directory that are older than 1 hour
    # In a real application, you might want to use a more sophisticated cleanup strategy
    for file in TEMP_DIR.glob("*"):
        try:
            if file.is_file():
                file.unlink()
        except Exception as e:
            logger.error(f"Error eliminando {file}: {e}")

# For local development
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)