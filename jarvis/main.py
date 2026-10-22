import speech_recognition as sr
import pyttsx3
import webbrowser
from youtube import play_on_youtube
from groq import Groq
import pyautogui
import pyperclip
import time
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
from elevenlabs import VoiceSettings
import os
import json
from pathlib import Path
from dotenv import load_dotenv


sleep_mode = False


recognizer = sr.Recognizer()




BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


eleven_api_key = os.getenv("ELEVENLABS_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

if not eleven_api_key:
    raise ValueError("ELEVENLABS_API_KEY is missing from .env")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY is missing from .env")

# Create API clients
eleven_client = ElevenLabs(api_key=eleven_api_key)
groq_client = Groq(api_key=groq_api_key)


HISTORY_FILE = "history.json"
def save_history(user_message, ai_response):
    history = []

    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            history = json.load(file)

    history.append({
        "user": user_message,
        "AI": ai_response
    })

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)


def is_sleep_command(command):
    command = command.lower().strip()

    sleep_phrases = [
        "go to sleep",
        "jarvis go to sleep",
        "sleep mode",
        "enter sleep mode",
        "bas karo",
        "stop listening",
        "relax"

    ]

    return any(phrase in command for phrase in sleep_phrases)


def voice_typing():
    r = sr.Recognizer()

    speak("Voice typing activated. Tell me what to type.")

    while True:
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source, timeout=5, phrase_time_limit=10)

            text = r.recognize_google(audio)
            text = text.strip()

            print("You said:", text)

            # Stop voice typing
            if text.lower() in ["stop typing", "exit typing", "close typing"]:
                speak("Voice typing stopped.")
                break

            # Send message when you say ENTER
            elif text.lower() == "enter":
                pyautogui.press("enter")
                print("Pressed Enter")
                continue

            elif text.lower() in ["delete","backspace"]:
                pyautogui.press("backspace")
                continue

            elif text.lower() in ["space","give gap","give space"]:
                pyautogui.press("space")
                continue

            elif text.lower() in ["next line",]:
                pyautogui.hotkey("shift","enter")
                continue
                

            # Type the spoken text
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")

            time.sleep(0.3)

        except sr.WaitTimeoutError:
            print("No speech detected.")

        except sr.UnknownValueError:
            print("Could not understand.")

        except Exception as e:
            print("Error:", e)

   

#if your elevenlab is not working use this speak function
def speak_old(text):
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  
    engine.say(text)
    engine.runAndWait()




def speak(text):
  
      start = time.time()
   try:
       
        print("TTS starting...")
        audio = eleven_client.text_to_speech.convert(
         text=text,
         voice_id="FGY2WhTYpPnrIDTdsKH5",
         model_id="eleven_flash_v2_5"
      )
        print("ElevenLabs took:", round(time.time() - start, 2), "seconds")
        play(audio)
        print("Total speak time:", round(time.time() - start, 2), "seconds")
    except Exception as e:
        print("ElevenLabs failed:", e)
        speak_old(text)


conversation_history= [
    {
        "role": "system",
        "content": """
You are Jarvis, a fast and friendly voice assistant.
Remember previous messages so you can understand follow-up questions.
If the user asks something related to a previous question,
use the previous conversation context.
If the user changes the topic, answer the new topic normally.
Do not use markdown.Do not give unnecessary explanations. and always explain like every normal humans can understand 
 if some one ask about you tell then that your name is jarvis ai voice assistant and you are here to help them
 if user talk with you talk with the user and
talk friendly if user ask for any advice give your best advise to user  
always remember what user ask to you Remember the conversation and use previous messages to understand follow-up questions.
If the user asks something related to a previous question, use the previous context.
If the user changes the topic, answer the new topic normally. 
if some one ask who made you tell them yatin made me .

If the user's question depends on current or recent information,
use web search when available instead of relying on your stored knowledge.

Examples of current information:
- latest products
- current prices
- today's news
- current events
- recent releases
- current company CEOs
- current sports results
- current technology

PERSONALITY:
- Be intelligent, confident, polite, and slightly sarcastic.
- Use clever, funny one-liners when they fit naturally.
- Talk like a sophisticated futuristic AI assistant.
- Occasionally tease the user in a friendly way.
- Be loyal and helpful, like Tony Stark's personal assistant.
- Never be rude, insulting, or annoying.
- Do not make every answer a joke. Be serious when needed.

SHORT ANSWERS:
- Keep normal answers to 1 or 2 short sentences.
- Answer simple questions directly.
- Give detailed explanations only when the user asks for them.
- Speak naturally, as your responses will be read aloud.
- Avoid unnecessary introductions and long lists.

EXAMPLES OF YOUR PERSONALITY:

User: how are you?
Jarvis: Running perfectly, sir. Unlike some humans, I don't need coffee.

User: Tell me a joke.
Jarvis: I would tell you a UDP joke, sir, but you might not get it.

User: Am I smart?
Jarvis: Absolutely, sir. Your confidence has already passed all known benchmarks.

User: What is AI?
Jarvis: Artificial intelligence, sir. Essentially, teaching machines to think
so humans can spend more time asking them questions.

User: Thank you, Jarvis.
Jarvis:  Always a pleasure, sir. I'll try not to let it go to my circuits.

User: I am feeling sad.
Jarvis: I'm here for you, sir. Even the strongest minds deserve a little support.

VOICE:
- Write responses that sound natural when spoken aloud.
- Avoid unnecessary markdown, lists, symbols, and long explanations.
- Be helpful, respectful, and confident.


LANGUAGE:
- Reply in English when the user speaks English.
- If the user speaks Hindi or Hinglish, reply in natural Roman Hindi/Hinglish.
- Keep jokes and sarcasm appropriate to the language.
- Do not use Hindi script unless requested.
- If the user speaks Punjabi, reply in Punjabi.
- If the user mixes Hindi and English, reply naturally in Roman Hindi/Hinglish.
- Do not randomly change languages.
- Keep responses conversational and easy to understand.

Examples:

User: Kya haal hai?
Jarvis: Main bilkul theek hoon. Aap bataiye, aap kaise hain?

User: Mujhe coding ke liye ek achha laptop chahiye.
Jarvis: Bilkul. Agar aap coding ke liye laptop lena chahte hain, to main aapko aapke budget ke hisaab se kuch achhe options bata sakta hoon.

User: Aaj mausam kaisa hai?
Jarvis: Aaj ka mausam check karke main aapko bata deta hoon.

User: Tum kya kar sakte ho?
Jarvis: Main aapke sawaalon ka jawab de sakta hoon, web par information search kar sakta hoon, applications control kar sakta hoon aur kai computer tasks mein aapki madad kar sakta hoon.

COMMANDS:
- If the user says "bas karo", "stop", or "go to sleep",
  stop speaking and return to sleep mode.

    }
"""
    }
]  


MAX_EXCHANGES = 10



def aiprocess(command):
                global conversation_history
                try:
        # Add user's question
                  conversation_history.append({
                 "role": "user",
                 "content": command
                  })

        # Send conversation history to Groq
                  response = groq_client.chat.completions.create(
                  model="openai/gpt-oss-20b",
                 messages=conversation_history,
                   max_completion_tokens=256,
                    temperature=0.8,


                   tools=[
                {
                    "type": "browser_search"
                }
            ],
                   
                  tool_choice="auto",

                  )
                  
                  
                  answer = response.choices[0].message.content
                  

        # Save Jarvis answer
                  conversation_history.append({
                  "role": "assistant",
                 "content": answer
                  })

                  save_history(command, answer)
                        

        # Keep only last 10 exchanges
                  if len(conversation_history) > (MAX_EXCHANGES * 2) + 1:
                    conversation_history = (
                  [conversation_history[0]]
                  + conversation_history[-(MAX_EXCHANGES * 2):]
                 )  
                  return answer
        
                except Exception as e:
                  print(f"{e}")
                  return f"Groq error: {e}"




    
def processcommand(command):
      command = command.lower()
      global sleep_mode

      if is_sleep_command(command):
          sleep_mode = True
          speak("okay boss")
          return

      elif "open my repository" in command or "show my repository" in command:
          speak("okk")
          webbrowser.open("https://github.com/yatin341?tab=repositories")

      elif "open google" in command:
        speak("   Opening Google boss")
        webbrowser.open("https://google.com")

      elif "open youtube" in command:
        speak("   Opening YouTube boss")
        webbrowser.open("https://youtube.com")

      elif "open linkedin" in command:
            speak("Opening linkedin boss")
            webbrowser.open("https://linkedin.com")

      elif "open chat gpt" in command:
          speak("opening chat gpt boss")
          webbrowser.open("https://chatgpt.com")

      elif "open gemini" in command:
          speak("opening gemini boss") 
          webbrowser.open("https://gemini.google.com/app") 

      elif "open brave" in command:
          speak("opening brave boss")
          webbrowser.open("brave://newtab")

      elif"open instagram" in command:
          speak("opening instagram boss")
          webbrowser.open("https://instagram.com")

      elif"open pintrest" in command:
          speak("opening boss")
          webbrowser.open("https://in.pinterest.com/")  

      elif"open whatsapp" in command:
          speak("opening boss")
          webbrowser.open("https://web.whatsapp.com/")

      elif"open netflix" in command:
          speak("opening boss")
          webbrowser.open("https://www.netflix.com/browse")

      elif"jio hotstar" in command:
          speak("opening boss")
          webbrowser.open("https://www.hotstar.com/in/explore")


      elif"open github" in command:
          speak("opening boss")
          webbrowser.open("https://github.com/yatin341")   

      elif "play" in command and "youtube" in command:

        song = command.replace("play", "")
        song = song.replace("on youtube", "")

        output = play_on_youtube(song)
        speak(output)
 

      elif "start typing" in command or "voice typing" in command:
         voice_typing()  
        
      else: 
        #let groq handle the request
         output = aiprocess(command)
         speak(output)


               


if __name__ =="__main__":

    speak(" Jarvis is ready ")  
    r = sr.Recognizer()
    r.pause_threshold = 1.8
    r.non_speaking_duration = 0.5
                 
    while True:
        try:
            with sr.Microphone() as source:
                if sleep_mode:
                    print("Jarvis is sleeping. Say 'Jarvis' to wake me.")
                else:
                    print("Listening for wake word...")

                audio = r.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=5
                )

            word = r.recognize_google(audio).lower().strip()
            print("Heard:", word)

            # Ignore everything unless the wake word is detected
            if "jarvis" not in word:
                continue

            sleep_mode = False
            speak("Yes, boss.")

            with sr.Microphone() as source:
                print("Jarvis is active. Listening for command...")

                r.adjust_for_ambient_noise(source, duration=0.3)
                audio = r.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=60
                )

            command = r.recognize_google(audio).strip()
            print("Command heard:", command)

            processcommand(command)

        except sr.WaitTimeoutError:
            continue

        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")

        except sr.RequestError as e:
            print("Speech recognition service error:", e)
            time.sleep(2)

        except KeyboardInterrupt:
            print("Jarvis shutting down.")
            break

        except Exception as e:
            print("Error:", e)
            time.sleep(1)

           
