import socketio
import time

class ServerCommunicator:
    def __init__(self, server_url='http://localhost:3000'):
        self.sio = socketio.Client()
        self.server_url = server_url
        self.connected = False

        @self.sio.event
        def connect():
            print(f"Conectado a {self.server_url}")
            self.connected = True

    def connect(self):
        print("Conectando con el servidor...")
        self.sio.connect(self.server_url)
        while not self.connected:
            time.sleep(0.1)
        print("Conexión con el servidor establecida.")

    def send_transcription(self, transcription):
        if self.connected:
            print(f"Enviando transcripción al servidor: {transcription}")
            self.sio.emit('transcripcion', transcription)
        else:
            print("No conectado al servidor.")
