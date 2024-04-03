# audio_recorder.py
import pyaudio

class AudioRecorder:
    def __init__(self, format=pyaudio.paInt16, channels=1, rate=16000, chunk=1024, record_seconds=10):
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.record_seconds = record_seconds
        self.audio_interface = pyaudio.PyAudio()
        self.stream = None

    def start_recording(self):
        self.stream = self.audio_interface.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
        print("Recording Started.")

    def stop_recording(self):
        print("Recording Stopped.")
        self.stream.stop_stream()
        self.stream.close()
        self.audio_interface.terminate()

    def record(self):
        frames = []
        for i in range(0, int(self.rate / self.chunk * self.record_seconds)):
            data = self.stream.read(self.chunk)
            frames.append(data)
        return frames
