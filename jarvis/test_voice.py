import pyttsx3

engine = pyttsx3.init("sapi5")

engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)

voices = engine.getProperty("voices")

print("Voices found:", len(voices))

for i, voice in enumerate(voices):
    print(i, voice.name)

engine.say("Hello sir. This is Jarvis.")
engine.runAndWait()

print("Voice test completed.")