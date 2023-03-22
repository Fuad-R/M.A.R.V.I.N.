import vosk
import subprocess
import pyaudio

# Initialize Vosk API
model = vosk.Model("model")
rec = vosk.KaldiRecognizer(model, 16000)

# Wait for "Hey MARVIN"
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()
while True:
    data = stream.read(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        text = rec.Result()
        if "Hey MARVIN" in text:
            break

# Transcribe live speech
while True:
    data = stream.read(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        text = rec.Result()
        print(text)
    else:
        print(rec.PartialResult())

# Enter text into Dalai
result = subprocess.run(["dalai", "ask", text], capture_output=True)
output = result.stdout.decode("utf-8").strip()

# Output result from Dalai into Larynx2
subprocess.run(["larynx2", output])
