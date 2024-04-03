Este es el estado actual de la aplicación:
{
***main.py :***
[[
import asyncio
from procesamiento_frases import ProcesadorDeFrases
from route import CustomClient
from tts_manager import GestorTTS

URI = 'http://localhost:3000'

async def main():
    procesador = ProcesadorDeFrases()
    gestor_tts = GestorTTS(procesador)
    cliente = CustomClient(uri=URI, procesar_frase_callback=procesador.procesar_palabra)
    await cliente.start()

if __name__ == "__main__":
    asyncio.run(main())



]],

***route.py :***
[[
import socketio

class CustomClient(socketio.AsyncClient):
    def __init__(self, uri, procesar_frase_callback):
        super().__init__(reconnection=True, reconnection_attempts=5, reconnection_delay=1)
        self.uri = uri
        self.procesar_frase_callback = procesar_frase_callback
        self.on('connect', self.handle_connect)
        self.on('disconnect', self.handle_disconnect)
        self.on('traduccion', self.on_traduccion)

    async def start(self):
        await self.connect(self.uri)
        await self.wait()

    async def handle_connect(self):
        print("Conexión establecida con el servidor.")

    async def handle_disconnect(self):
        print("Desconexión del servidor.")

    async def on_traduccion(self, data):
        self.procesar_frase_callback(data)


]],

***procesamiento_frases.py***
[[
from queue import Queue

class ProcesadorDeFrases:
    def __init__(self):
        self.cola_frases = Queue()
        self.frase_actual = ""
        self.id_actual = 0  # Usando un contador simple para identificar las frases

    def limpiar_palabra(self, palabra):
        return palabra.strip().replace('"', '').replace("'", "").replace("``", "").replace("´´", "")

    def procesar_palabra(self, palabra):
        palabra_limpia = self.limpiar_palabra(palabra)

        if palabra_limpia == "" or palabra_limpia in ["'", '"', "``", "´´"]:
            return

        if palabra_limpia.endswith((".", "?", "!")):
            if self.frase_actual != "":
                frase_completa = f"{self.frase_actual}{palabra_limpia}"
                self.cola_frases.put((self.id_actual, frase_completa))
                self.frase_actual = ""
                self.id_actual += 1  # Incrementar el ID para la próxima frase
        else:
            self.frase_actual += f"{palabra_limpia} "


]],

***tts_manager.py***:
[[
import torch
from TTS.api import TTS
import pyaudio
import wave
import time
from queue import PriorityQueue
import threading

class GestorTTS:
    def __init__(self, procesador_de_frases):
        self.model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.language = "en"
        self.speaker_wavs = "./audio.wav"
        self.tts = TTS(self.model_name).to(self.device)
        self.cola_audios = PriorityQueue()
        self.procesador_de_frases = procesador_de_frases
        threading.Thread(target=self.procesar_y_reproducir_frases, daemon=True).start()

    def procesar_y_reproducir_frases(self):
        while True:
            if not self.procesador_de_frases.cola_frases.empty():
                id_frase, frase = self.procesador_de_frases.cola_frases.get()
                file_path = self.text_to_speech(frase, id_frase)
                self.play_audio(file_path)
            time.sleep(1)

    def text_to_speech(self, text, id_frase):
        file_path = f"output_{int(time.time())}_{id_frase}.wav"
        self.tts.tts_to_file(text=text, speaker_wav=self.speaker_wavs, language=self.language, file_path=file_path)
        return file_path

    def play_audio(self, file_path):
        p = pyaudio.PyAudio()
        wf = wave.open(file_path, 'rb')
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)
        stream.stop_stream()
        stream.close()
        p.terminate()


]]

}