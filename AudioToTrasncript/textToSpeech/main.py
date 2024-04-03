# main.py
from audio_recorder import AudioRecorder
from audio_transcriber import AudioTranscriber
from server_communicator import ServerCommunicator

def main():
    communicator = ServerCommunicator()
    communicator.connect()

    recorder = AudioRecorder()
    transcriber = AudioTranscriber(communicator)  # Se pasa el comunicador como argumento

    recorder.start_recording()

    try:
        while True:
            frames = recorder.record()
            transcriber.transcribe(frames)
    except KeyboardInterrupt:
        print("Interruption detected, stopping...")

    recorder.stop_recording()

if __name__ == "__main__":
    main()
