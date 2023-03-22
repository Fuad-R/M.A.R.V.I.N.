import vosk
import subprocess
import pyaudio
import openai

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

# Transcribe live speech and send to OpenAI Chat API
openai.api_key = "YOUR_API_KEY"
chatbot_name = "MARVIN"
chatbot_prompt = f"User: {text}\n{chatbot_name}:"

while True:
    data = stream.read(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        text = rec.Result()
        chatbot_input = chatbot_prompt + text
        response = openai.Completion.create(
            engine="davinci",
            prompt=chatbot_input,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )
        chatbot_output = response.choices[0].text.strip()
        print(chatbot_output)
    else:
        print(rec.PartialResult())

# Output result from OpenAI Chat API into Larynx2
subprocess.run(["larynx2", chatbot_output])
