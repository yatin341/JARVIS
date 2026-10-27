
import io
import re
import threading
import time
import wave
from contextlib import asynccontextmanager
from pathlib import Path
import os

import speech_recognition as sr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from elevenlabs import VoiceSettings
from elevenlabs.play import play



try:
    import winsound          # built into Windows, plays audio and waits until it has really finished
except ImportError:
    winsound = None

import main as jarvis 

FRONTEND = Path(__file__).parent / "frontend"


VOICE_ID = "FGY2WhTYpPnrIDTdsKH5"
VOICE_MODEL = "eleven_flash_v2_5"   
VOICE_SETTINGS = dict(stability=0.60, similarity_boost=0.80, style=0.15, use_speaker_boost=True)
FOLLOW_UP_SECONDS = 4                   # how long Jarvis keeps listening after an answer (0 = always need "Jarvis")
END_WORDS = ("thank you", "thanks", "that's all", "stop listening", "go to sleep", "goodbye", "bye")
PCM_RATE = 24000

def clean_for_speech(text):
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[*_#`~>|{}\[\]]", "", text)
    return re.sub(r"\s+", " ", text).strip()

def eleven_audio(text, fmt):
    return jarvis.eleven_client.text_to_speech.convert(
        voice_id=VOICE_ID, model_id=VOICE_MODEL, text=text,
        voice_settings=VoiceSettings(**VOICE_SETTINGS), output_format=fmt)


def clear_speak(text):
    """Speaks the whole sentence and only returns after the audio has really finished."""
    text = clean_for_speech(text) or "Done, boss."
    print("Jarvis:", text)

    if winsound:
        try:
            pcm = b"".join(eleven_audio(text, f"pcm_{PCM_RATE}"))
            pad = lambda sec: b"\x00" * int(PCM_RATE * 2 * sec)
            buf = io.BytesIO()
            with wave.open(buf, "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(PCM_RATE)
                w.writeframes(pad(0.2) + pcm + pad(0.5))   # silence at both ends: nothing gets clipped
            winsound.PlaySound(buf.getvalue(), winsound.SND_MEMORY)   # waits until playback is done
            return
        except Exception as e:
            print("PCM playback failed, trying normal playback:", e)

    play(b"".join(eleven_audio(text, "mp3_44100_128")))
    time.sleep(0.5)


real_speak = clear_speak
status = {"state": "idle", "heard": "", "text": ""}   # what the web page displays


def set_status(**kw):
    status.update(kw)


def tracked_speak(text):
    """Your speak(), but it tells the web page when Jarvis is talking (so the animation matches the voice)."""
    set_status(state="speaking", text=text)
    try:
        try:
            real_speak(text)                 # ElevenLabs
        except Exception as e:
            print("ElevenLabs failed, using backup voice:", e)
            jarvis.speak_old(text)           # pyttsx3 backup from your code
    except Exception as e:
        print("Voice error:", e)
        time.sleep(min(6, 0.8 + len(text) * 0.05))
    finally:
        set_status(state="idle", text="")


def handle_command(command):
    print("Command heard:", command)
    set_status(state="thinking", heard=command, text="")
    try:
        jarvis.processcommand(command)
    except Exception as e:
        print("Command error:", e)
    set_status(state="idle", heard="", text="")


def wake_loop():
    r = sr.Recognizer()
    r.pause_threshold = 1.8
    r.non_speaking_duration = 0.5
    follow_until = 0

    tracked_speak("Jarvis is ready")
    while True:
        awake = False
        following = time.time() < follow_until
        try:
            set_status(state="listening" if following else "idle", heard="", text="")

           
            if following:
                with sr.Microphone() as source:
                    audio = r.listen(source, timeout=FOLLOW_UP_SECONDS, phrase_time_limit=30)
                command = r.recognize_google(audio)
                if any(w in command.lower() for w in END_WORDS):
                    follow_until = 0
                    tracked_speak("Okay boss.")
                    continue
                handle_command(command)
                follow_until = time.time() + FOLLOW_UP_SECONDS
                continue

          
            with sr.Microphone() as source:
                audio = r.listen(source, timeout=10, phrase_time_limit=5)
            heard = r.recognize_google(audio)
            low = heard.lower()
            if "jarvis" not in low:
                continue

            print("Wake word heard:", heard)
            awake = True

            rest = low.split("jarvis", 1)[1].strip(" ,.")     # "Jarvis open youtube" in one sentence
            if len(rest) > 2:
                handle_command(rest)
                follow_until = time.time() + FOLLOW_UP_SECONDS
                continue

            tracked_speak("yes boss")
            set_status(state="listening", heard="", text="")
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=10, phrase_time_limit=30)
            handle_command(r.recognize_google(audio))
            follow_until = time.time() + FOLLOW_UP_SECONDS

        except sr.WaitTimeoutError:
            follow_until = 0                       # nobody spoke
        except sr.UnknownValueError:
            if awake:
                tracked_speak("Sorry boss, I didn't catch that.")
        except Exception as e:
            print("error:", e)
            time.sleep(1)


@asynccontextmanager
async def lifespan(app):
    jarvis.speak = tracked_speak

    # Start microphone listening only on your own laptop
    enable_wake_word = (
        os.getenv("ENABLE_LOCAL_WAKE_WORD", "false").lower() == "true"
    )

    if enable_wake_word:
        threading.Thread(target=wake_loop, daemon=True).start()

    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/state")
def state():
    return status


if FRONTEND.exists():
    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
