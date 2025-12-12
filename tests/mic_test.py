import pyaudio

p = pyaudio.PyAudio()

stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=44100,
    input=True,
    frames_per_buffer=1024
)

print("Microphone access requested. Press Ctrl+C to stop.")
try:
    while True:
        stream.read(1024)
except KeyboardInterrupt:
    pass

stream.stop_stream()
stream.close()
p.terminate()
