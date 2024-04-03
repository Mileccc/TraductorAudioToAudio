import pyaudio
from six.moves import queue

class MicrophoneStream:
    def __init__(self, rate=16000, chunk=1024):
        self.rate = rate
        self.chunk = chunk
        self.stream = None
        self.audio_interface = pyaudio.PyAudio()
        self.buffer = queue.Queue()
        self.closed = True
        self.sample_width = None

    def __enter__(self):
        print("Abriendo flujo de micrófono...")
        self.stream = self.audio_interface.open(format=pyaudio.paInt16,
                                                channels=1,
                                                rate=self.rate,
                                                input=True,
                                                frames_per_buffer=self.chunk,
                                                stream_callback=self.callback)
        self.closed = False
        self.sample_width = self.audio_interface.get_sample_size(pyaudio.paInt16)
        return self

    def __exit__(self, type, value, traceback):
        self.closed = True
        self.stream.stop_stream()
        self.stream.close()
        self.buffer.put(None)
        self.audio_interface.terminate()
        print("Flujo de micrófono cerrado.")

    def callback(self, in_data, frame_count, time_info, status_flags):
        self.buffer.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        print("Generando datos de audio...")
        while not self.closed:
            chunk = self.buffer.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self.buffer.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)
