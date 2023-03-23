import vosk
import subprocess
import pyaudio
import openai

# Initialize Vosk API
model = vosk.Model("model")
rec = vosk.KaldiRecognizer(model, 16000)

# Send chatbot intro to OpenAI Chat API
openai.api_key = "YOUR_API_KEY"
chatbot_name = "MARVIN"
chatbot_intro = "Hello MARVIN. You are an AI chatbot based on Iron Man's JARVIS. My name is Fuad and you live in my room. You are designed to help me out with my day-to-day tasks. Your name stands for Multifunctional Artificial Reality Virtual Intelligence Network. You have a voice and everything you say will be transcribed to live speech."
chatbot_prompt = f"{chatbot_name}: {chatbot_intro}\nUser:"

response = openai.Completion.create(
    engine="davinci",
    prompt=chatbot_prompt,
    max_tokens=1024,
    n=1,
    stop=None,
    temperature=0.5,
)

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
print(f"Speaking: {chatbot_output}")
subprocess.run(["larynx2", chatbot_output])
