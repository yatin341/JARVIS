
import io
import os
import re
import threading
import time
import wave
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Desktop-only imports should not run on Render.
IS_DESKTOP = (
    os.name == "nt"
    and os.getenv("JARVIS_MODE", "desktop").lower() == "desktop"
)

jarvis = None
sr = None
VoiceSettings = None
play = None

if IS_DESKTOP:
    import speech_recognition as sr
    from elevenlabs import VoiceSettings
    from elevenlabs.play import play

    try:
        import winsound
    except ImportError:
        winsound = None

    import main as jarvis
else:
    winsound = None

FRONTEND = Path(__file__).parent / "frontend"

# Voice settings for local Windows Jarvis
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
VOICE_MODEL = "eleven_flash_v2_5"
VOICE_SETTINGS = {
    "stability": 0.60,
    "similarity_boost": 0.80,
    "style": 0.15,
    "use_speaker_boost": True,
}
FOLLOW_UP_SECONDS = 4
END_WORDS = (
    "thank you", "thanks", "that's all",
    "stop listening", "go to sleep", "goodbye", "bye"
)
PCM_RATE = 24000

status = {"state": "idle", "heard": "", "text": ""}


def set_status(**kwargs):
    status.update(kwargs)


def clean_for_speech(text):
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[*_#`~>|\[\]{}]", "", text)
    return re.sub(r"\s+", " ", text).strip()


# ---------- Local desktop voice functions ----------

def eleven_audio(text, fmt):
    return jarvis.eleven_client.text_to_speech.convert(
        voice_id=VOICE_ID,
        model_id=VOICE_MODEL,
        text=text,
        voice_settings=VoiceSettings(**VOICE_SETTINGS),
        output_format=fmt,
    )


def clear_speak(text):
    text = clean_for_speech(text) or "Done, boss."
    print("Jarvis:", text)

    if winsound:
        try:
            pcm = b"".join(eleven_audio(text, f"pcm_{PCM_RATE}"))
            padding = lambda sec: b"\x00" * int(PCM_RATE * 2 * sec)

            buffer = io.BytesIO()
            with wave.open(buffer, "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(PCM_RATE)
                wav.writeframes(padding(0.2) + pcm + padding(0.5))

            winsound.PlaySound(
                buffer.getvalue(),
                winsound.SND_MEMORY,
            )
            return
        except Exception as exc:
            print("PCM playback failed:", exc)

    play(b"".join(eleven_audio(text, "mp3_44100_128")))
    time.sleep(0.5)


def tracked_speak(text):
    set_status(state="speaking", text=text)
    try:
        clear_speak(text)
    except Exception as exc:
        print("ElevenLabs voice error:", exc)
    finally:
        set_status(state="idle", text="")


def handle_command(command):
    print("Command heard:", command)
    set_status(state="thinking", heard=command, text="")
    try:
        if jarvis is not None:
            jarvis.processcommand(command)
    except Exception as exc:
        print("Command error:", exc)
    finally:
        set_status(state="idle", heard="", text="")


def wake_loop():
    if not IS_DESKTOP or sr is None:
        return

    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 1.8
    recognizer.non_speaking_duration = 0.5
    follow_until = 0

    tracked_speak("Jarvis is ready")

    while True:
        awake = False
        following = time.time() < follow_until

        try:
            set_status(
                state="listening" if following else "idle",
                heard="",
                text="",
            )

            with sr.Microphone() as source:
                if not following:
                    audio = recognizer.listen(
                        source, timeout=10, phrase_time_limit=5
                    )
                else:
                    audio = recognizer.listen(
                        source,
                        timeout=FOLLOW_UP_SECONDS,
                        phrase_time_limit=30,
                    )

            heard = recognizer.recognize_google(audio)
            low = heard.lower()

            if following:
                if any(word in low for word in END_WORDS):
                    follow_until = 0
                    tracked_speak("Okay boss.")
                    continue

                handle_command(heard)
                follow_until = time.time() + FOLLOW_UP_SECONDS
                continue

            if "jarvis" not in low:
                continue

            awake = True
            print("Wake word heard:", heard)

            rest = low.split("jarvis", 1)[1].strip(" ,.")
            if len(rest) > 2:
                handle_command(rest)
                follow_until = time.time() + FOLLOW_UP_SECONDS
                continue

            tracked_speak("Yes boss")
            set_status(state="listening", heard="", text="")

            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(
                    source, timeout=10, phrase_time_limit=30
                )

            handle_command(recognizer.recognize_google(audio))
            follow_until = time.time() + FOLLOW_UP_SECONDS

        except sr.WaitTimeoutError:
            follow_until = 0
        except sr.UnknownValueError:
            if awake:
                tracked_speak("Sorry boss, I didn't catch that.")
        except Exception as exc:
            print("Wake loop error:", exc)
            time.sleep(1)


# ---------- FastAPI hosted and desktop app ----------

class ChatRequest(BaseModel):
    message: str


HOSTED_SYSTEM_PROMPT = """
You are Jarvis, a friendly and intelligent AI assistant.
Be confident, helpful, and slightly witty when appropriate.
Keep ordinary answers short, usually one or two sentences.
Reply in English when the user speaks English.
Reply in natural Roman Hindi/Hinglish when the user uses Hindi or Hinglish.
If asked who created you, say Yatin created you.
Never claim you performed actions on the user's computer.
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    if IS_DESKTOP and jarvis is not None:
        jarvis.speak = tracked_speak

        if os.getenv("ENABLE_LOCAL_WAKE_WORD", "false").lower() == "true":
            threading.Thread(target=wake_loop, daemon=True).start()

    yield


app = FastAPI(title="Jarvis AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/state")
def get_state():
    return status


@app.post("/api/chat")
def chat(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is missing from environment variables.",
        )

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": HOSTED_SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            max_completion_tokens=256,
            temperature=0.8,
        )

        reply = response.choices[0].message.content or ""
        return {"reply": reply}

    except Exception as exc:
        print("Groq request failed:", repr(exc))
        raise HTTPException(
            status_code=502,
            detail="Jarvis could not get a response from the AI service.",
        )


if FRONTEND.exists():
    app.mount(
        "/",
        StaticFiles(directory=FRONTEND, html=True),
        name="frontend",
    )
