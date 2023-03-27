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
chatbot_intro = "Pretend you are MARVIN, an AI voice assistant based off of Iron man's Jarvis, you will respond as he would."
chatbot_prompt = f"{chatbot_name}: {chatbot_intro}\nUser:"

response = openai.Completion.create(
    engine="davinci",
    prompt=chatbot_prompt,
    max_tokens=1024,
    n=1,
    stop=None,
    temperature=0.65,
)

# Initialize conversation history
conversation_history = [
    {"role": "system", "content": chatbot_intro}
]

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
        print(f"Transcribed speech: {text}")
        if "MARVIN reset context" in text:
            conversation_history = [
                {"role": "system", "content": chatbot_intro}
            ]
            chatbot_output = "Context has been reset."
        else:
            conversation_history.append({"role": "user", "content": text})
            response = openai.ChatCompletion.create(
                model="davinci",
                messages=conversation_history,
                temperature=0.65,
            )
            chatbot_output = response.choices[0].message["content"].strip()
            conversation_history.append({"role": "assistant", "content": chatbot_output})
        print(chatbot_output)
    else:
        print(rec.PartialResult())

# Output result from OpenAI Chat API into Larynx2
print(f"Speaking: {chatbot_output}")
subprocess.run(["/home/pi/larynx2", chatbot_output])
