from transcripcion import AudioTranscriber
from capturar_audio import MicrophoneStream
from server_communicator import ServerCommunicator

def main():
    print("Inicializando comunicador con el servidor...")
    communicator = ServerCommunicator()
    communicator.connect()

    print("Inicializando flujo de audio del micrófono...")
    audio_stream = MicrophoneStream()
    transcriber = AudioTranscriber(communicator)

    try:
        print("Iniciando transcripción de audio...")
        transcriber.transcribe_stream(audio_stream)
    except KeyboardInterrupt:
        print("Interrupción detectada, deteniendo...")

if __name__ == "__main__":
    main()
