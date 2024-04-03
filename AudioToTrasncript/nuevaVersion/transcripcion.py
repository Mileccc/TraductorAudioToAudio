import speech_recognition as sr
import time

class AudioTranscriber:
    def __init__(self, communicator):
        self.recognizer = sr.Recognizer()
        self.communicator = communicator

    def transcribe_stream(self, audio_stream):
        with audio_stream as stream:
            audio_generator = stream.generator()
            for audio_content in audio_generator:
                audio_data = sr.AudioData(audio_content, stream.rate, stream.sample_width)
                try:
                    print("Transcribiendo audio...")
                    text = self.recognizer.recognize_google(audio_data, language='es-ES')
                    print("Transcripción: ", text)
                    self.communicator.send_transcription(text)
                except sr.UnknownValueError:
                    print("Google Speech Recognition no pudo entender el audio")
                except sr.RequestError as e:
                    print(f"No se pudo solicitar resultados del servicio de Google Speech Recognition; {e}")
                time.sleep(4) 
