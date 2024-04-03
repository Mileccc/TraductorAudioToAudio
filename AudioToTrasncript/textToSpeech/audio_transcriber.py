# audio_transcriber.py
import speech_recognition as sr

class AudioTranscriber:
    def __init__(self, communicator):
        self.recognizer = sr.Recognizer()
        self.communicator = communicator  # Almacenar la referencia al ServerCommunicator

    def transcribe(self, frames):
        audio_data = sr.AudioData(b''.join(frames), 16000, 2)
        try:
            text = self.recognizer.recognize_google(audio_data, language='es-ES')
            print("Transcription: ", text)
            self.communicator.send_transcription(text)  # Usar el comunicador para enviar la transcripción
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
