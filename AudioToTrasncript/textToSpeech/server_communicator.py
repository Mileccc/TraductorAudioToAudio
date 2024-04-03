# server_communicator.py
import socketio
import time

class ServerCommunicator:
    def __init__(self, server_url='http://localhost:3000'):
        self.sio = socketio.Client()
        self.server_url = server_url
        self.connected = False  # Añadido para controlar el estado de la conexión
        
        # Definir un handler para el evento de conexión
        @self.sio.event
        def connect():
            print(f"Connected to {self.server_url}")
            self.connected = True

    def connect(self):
        self.sio.connect(self.server_url)
        while not self.connected:  # Espera activamente hasta que se establezca la conexión
            time.sleep(0.1)
        
    def send_transcription(self, transcription):
        if self.connected:  # Verifica que la conexión esté activa antes de enviar
            self.sio.emit('transcripcion', transcription)
            print("Transcription sent to server.")
        else:
            print("Not connected to server.")
