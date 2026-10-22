
import io
import os
import re
import threading
import time
import wave
from contextlib import asynccontextmanager
from pathlib import Path

import speech_recognition as sr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from elevenlabs import VoiceSettings
from elevenlabs.play import play

try:
    import winsound
except ImportError:
    winsound = None

import main as jarvis


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
FRONTEND = BASE_DIR / "frontend"

VOICE_ID = "FGY2WhTYpPnrIDTdsKH5"
VOICE_MODEL = "eleven_flash_v2_5"

VOICE_SETTINGS = {
    "stability": 0.60,
    "similarity_boost": 0.80,
    "style": 0.15,
    "use_speaker_boost": True,
}

FOLLOW_UP_SECONDS = 4
PCM_RATE = 24000

END_WORDS = (
    "thank you",
    "thanks",
    "that's all",
    "stop listening",
    "go to sleep",
    "goodbye",
    "bye",
)

SLEEP_WORDS = (
    "go to sleep",
    "sleep mode",
    "enter sleep mode",
    "bas karo",
    "stop listening",
    "relax",
)

status = {
    "state": "idle",
    "heard": "",
    "text": "",
}

status_lock = threading.Lock()
listener_started = False
listener_lock = threading.Lock()


# --------------------------------------------------
# FRONTEND STATUS
# --------------------------------------------------

def set_status(**kwargs):
    with status_lock:
        status.update(kwargs)


def get_status():
    with status_lock:
        return status.copy()


# --------------------------------------------------
# ELEVENLABS VOICE
# --------------------------------------------------

def clean_for_speech(text):
    text = str(text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[*_#`~>|{}\[\]]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def eleven_audio(text, output_format):
    return jarvis.eleven_client.text_to_speech.convert(
        voice_id=VOICE_ID,
        model_id=VOICE_MODEL,
        text=text,
        voice_settings=VoiceSettings(**VOICE_SETTINGS),
        output_format=output_format,
    )


def clear_speak(text):
    text = clean_for_speech(text) or "Done, boss."
    print("Jarvis:", text)

    if winsound:
        try:
            pcm = b"".join(
                eleven_audio(text, f"pcm_{PCM_RATE}")
            )

            padding = lambda seconds: (
                b"\x00" * int(PCM_RATE * 2 * seconds)
            )

            buffer = io.BytesIO()

            with wave.open(buffer, "wb") as audio_file:
                audio_file.setnchannels(1)
                audio_file.setsampwidth(2)
                audio_file.setframerate(PCM_RATE)
                audio_file.writeframes(
                    padding(0.2) + pcm + padding(0.5)
                )

            winsound.PlaySound(
                buffer.getvalue(),
                winsound.SND_MEMORY,
            )
            return

        except Exception as error:
            print("PCM playback failed:", error)

    # Fallback audio playback
    audio = b"".join(
        eleven_audio(text, "mp3_44100_128")
    )
    play(audio)


def tracked_speak(text):
    set_status(state="speaking", text=text)

    try:
        clear_speak(text)

    except Exception as error:
        print("ElevenLabs failed:", error)

        try:
            # Use the backup voice from main.py
            jarvis.speak_old(text)
        except Exception as backup_error:
            print("Backup voice failed:", backup_error)

    finally:
        set_status(state="idle", text="")


# --------------------------------------------------
# COMMAND HANDLING
# --------------------------------------------------

def handle_command(command):
    command = command.strip()

    if not command:
        return

    print("Command heard:", command)
    set_status(state="thinking", heard=command, text="")

    try:
        jarvis.processcommand(command)

    except Exception as error:
        print("Command error:", error)

    finally:
        set_status(state="idle", heard="", text="")


# --------------------------------------------------
# MICROPHONE / WAKE WORD LOOP
# --------------------------------------------------

def wake_loop():
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 1.8
    recognizer.non_speaking_duration = 0.5

    follow_until = 0

    tracked_speak("Jarvis is ready")

    while True:
        awake = False

        try:
            # Sleep mode still listens for the wake word.
            if jarvis.sleep_mode:
                follow_until = 0

            following = (
                not jarvis.sleep_mode
                and time.time() < follow_until
            )

            set_status(
                state="listening" if following else "idle",
                heard="",
                text="",
            )

            with sr.Microphone() as source:
                if not following:
                    print("Waiting for wake word: Jarvis")

                audio = recognizer.listen(
                    source,
                    timeout=10 if not following else FOLLOW_UP_SECONDS,
                    phrase_time_limit=30 if following else 8,
                )

            heard = recognizer.recognize_google(audio).strip()
            low = heard.lower()

            # --------------------------------------
            # FOLLOW-UP COMMANDS
            # --------------------------------------

            if following:
                if any(word in low for word in SLEEP_WORDS):
                    jarvis.sleep_mode = True
                    follow_until = 0
                    tracked_speak("Going to sleep, boss.")
                    continue

                if any(word in low for word in END_WORDS):
                    follow_until = 0
                    tracked_speak("Okay, boss.")
                    continue

                handle_command(heard)

                if jarvis.sleep_mode:
                    follow_until = 0
                else:
                    follow_until = time.time() + FOLLOW_UP_SECONDS

                continue

            # --------------------------------------
            # WAKE WORD
            # --------------------------------------

            if "jarvis" not in low:
                continue

            print("Wake word heard:", heard)
            awake = True

            # Wake Jarvis from sleep.
            jarvis.sleep_mode = False

            # Support: "Jarvis open YouTube"
            rest = low.split("jarvis", 1)[1].strip(" ,.!")

            if len(rest) > 2:
                handle_command(rest)

                if not jarvis.sleep_mode:
                    follow_until = time.time() + FOLLOW_UP_SECONDS
                else:
                    follow_until = 0

                continue

            tracked_speak("Yes, boss.")

            set_status(
                state="listening",
                heard="",
                text="",
            )

            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.3,
                )

                audio = recognizer.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=30,
                )

            command = recognizer.recognize_google(audio)
            handle_command(command)

            if not jarvis.sleep_mode:
                follow_until = time.time() + FOLLOW_UP_SECONDS
            else:
                follow_until = 0

        except sr.WaitTimeoutError:
            if time.time() >= follow_until:
                follow_until = 0

        except sr.UnknownValueError:
            if awake:
                tracked_speak(
                    "Sorry, boss. I didn't catch that."
                )

        except sr.RequestError as error:
            print("Speech recognition service error:", error)
            time.sleep(2)

        except Exception as error:
            print("Listener error:", error)
            time.sleep(1)


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app):
    global listener_started

    # Route all main.py speech through the interface.
    jarvis.speak = tracked_speak

    enable_wake_word = (
        os.getenv("ENABLE_LOCAL_WAKE_WORD", "false").lower()
        == "true"
    )

    if enable_wake_word:
        with listener_lock:
            if not listener_started:
                listener_started = True

                threading.Thread(
                    target=wake_loop,
                    daemon=True,
                    name="jarvis-microphone",
                ).start()

    yield


app = FastAPI(lifespan=lifespan)

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
    return get_status()


if FRONTEND.exists():
    app.mount(
        "/",
        StaticFiles(directory=FRONTEND, html=True),
        name="frontend",
    )
