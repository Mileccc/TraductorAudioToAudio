import threading
import sys
import os
import queue
import time
import signal
import wave
import pyaudio
from faster_whisper import WhisperModel
# Importación de socketio removida ya que no se usará

# Inicializar cliente SocketIO para conectar con el servidor NestJS
# Líneas relacionadas con socketio removidas ya que no se usará

# Define una cola para gestionar los segmentos de audio para transcribir
cola_transcripciones = queue.Queue()

def transcribir_segmentos():
    tam_modelo = "large-v2"
    modelo = WhisperModel(tam_modelo, device="cuda", compute_type="float16")
    
    while True:
        if not cola_transcripciones.empty():
            ruta_archivo = cola_transcripciones.get()
            try:
                segmentos, info = modelo.transcribe(ruta_archivo, beam_size=5)
                if info.language == 'es':
                    transcripcion = " ".join([segment.text for segment in segmentos])
                    # Mostrar transcripción por consola en lugar de enviarla a un servidor
                    print(transcripcion)
            except Exception as e:
                print(f"Error al transcribir {ruta_archivo}: {e}")
            finally:
                # Asegurarse de que el archivo siempre se elimine
                os.remove(ruta_archivo)

def grabacion_continua():
    trozo = 1024
    formato = pyaudio.paInt16
    canales = 1
    tasa_muestras = 16000
    duracion_segmento = 3  # Duración del segmento en segundos

    p = pyaudio.PyAudio()
    stream = p.open(format=formato, channels=canales, rate=tasa_muestras, input=True, frames_per_buffer=trozo)
    
    print("Inicio de la grabación continua...")

    try:
        while True:
            cuadros_audio = []
            for i in range(0, int(tasa_muestras / trozo * duracion_segmento)):
                data = stream.read(trozo)
                cuadros_audio.append(data)
            
            # Guarda el segmento actual en un archivo temporal
            nombre_archivo = f"temp_segment_{int(time.time())}.wav"
            wf = wave.open(nombre_archivo, 'wb')
            wf.setnchannels(canales)
            wf.setsampwidth(p.get_sample_size(formato))
            wf.setframerate(tasa_muestras)
            wf.writeframes(b''.join(cuadros_audio))
            wf.close()
            
            # Añadir el nombre del archivo a la cola para su transcripción
            cola_transcripciones.put(nombre_archivo)
            
    except KeyboardInterrupt:
        print("Deteniendo la grabación y transcripción...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def limpiar_archivos_temporales():
    print("Limpiando archivos temporales...")
    while not cola_transcripciones.empty():
        ruta_archivo = cola_transcripciones.get_nowait()
        try:
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
                print(f"Archivo temporal eliminado: {ruta_archivo}")
        except Exception as e:
            print(f"No se pudo eliminar el archivo temporal {ruta_archivo}: {e}")

def handler_sigint(signum, frame):
    limpiar_archivos_temporales()
    print("Programa terminado.")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler_sigint)
    threading.Thread(target=transcribir_segmentos, daemon=True).start()
    grabacion_continua()
