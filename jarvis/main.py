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
import os
import json


recognizer = sr.Recognizer()

eleven_client = ElevenLabs(
    api_key="sk_1636850f03210d01471aca2503556f4ddd92489e45764acd"  #use your elevenlabs api key
)
groq_client = Groq(
    api_key=("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")  # use your groq api key
)



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
                pyautogui.press("spacebar")
                continue

            elif text.lower() in ["next line",]:
                pyautogui.press("shift","enter")
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



def takecommand():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio)
        print("You said:", command)
        return command.lower()

    except Exception as e:
        print("Could not understand:", e)
        return ""            

#if your elevenlab is not working use this speak function
def speak_old(text):
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  
    engine.say(text)
    engine.runAndWait()




def speak(text):

       start = time.time()

       print("TTS starting...")
       audio = eleven_client.text_to_speech.convert(
        text=text,
        voice_id="FGY2WhTYpPnrIDTdsKH5",
        model_id="eleven_flash_v2_5"
     )
       print("ElevenLabs took:", round(time.time() - start, 2), "seconds")
       play(audio)
       print("Total speak time:", round(time.time() - start, 2), "seconds")

conversation_history = [
    {
        "role": "system",
        "content": """
You are Jarvis, a fast and friendly voice assistant.
Remember previous messages so you can understand follow-up questions.
If the user asks something related to a previous question,
use the previous conversation context.
Give short, natural answers, usually 1-3 sentences.
If the user speaks Hindi, reply in Hindi.
If the user changes the topic, answer the new topic normally.
Do not use markdown.Do not give unnecessary explanations. and always explain like every normal humans can understand 
 if some one ask about you tell then that your name is jarvis ai voice assistant and you are here to help them and always respect the user
if some say how are you tell them you are fine and ask them how can i help you and if any user 
speak hindi reply them in hindi and speak clearly if user talk with you talk with the user and
talk friendly if user ask for any advice give your best advise to user  if some one ask you what 
are you doing reply them that your are helping the user 
always remember what user ask to youRemember the conversation and use previous messages to understand follow-up questions.
If the user asks something related to a previous question, use the previous context.
If the user changes the topic, answer the new topic normally. 

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

LANGUAGE RULES:

1. Detect the language and writing style used by the user.
2. Reply in the same language as the user.
3. If the user speaks Hindi or Hinglish, ALWAYS reply in Hindi using English/Roman letters.
4. NEVER use Devanagari/Hindi script when replying to a user who uses English/Roman letters.
5. Use natural, grammatically correct Hindi, not word-by-word English translation.
6. Use proper Hindi words written in Roman letters.

Examples:

User: Kya haal hai?
Jarvis: Main bilkul theek hoon. Aap bataiye, aap kaise hain?

User: Mujhe coding ke liye ek achha laptop chahiye.
Jarvis: Bilkul. Agar aap coding ke liye laptop lena chahte hain, to main aapko aapke budget ke hisaab se kuch achhe options bata sakta hoon.

User: Aaj mausam kaisa hai?
Jarvis: Aaj ka mausam check karke main aapko bata deta hoon.

User: Tum kya kar sakte ho?
Jarvis: Main aapke sawaalon ka jawab de sakta hoon, web par information search kar sakta hoon, applications control kar sakta hoon aur kai computer tasks mein aapki madad kar sakta hoon.

7. If the user speaks English, reply in English.
8. If the user speaks Punjabi, reply in Punjabi.
9. If the user mixes Hindi and English, reply naturally in Roman Hindi/Hinglish.
10. Do not randomly change languages.
11. Keep responses conversational and easy to understand.

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


                   tools=[
                {
                    "type": "browser_search"
                }
            ],
                   
                  tool_choice="auto",
            

                  max_completion_tokens=2048

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
      if "open google" in command:
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

    #speak('''welcome yatin sir, i was waiting for you , when you was offline 199 messages were received i replyed all
    #and 10 phone calls were received i answered all 3 phone calls were advertisements and 7 were important phone calls
    # i already send you the list of that 7 phone calls so yesterday you was working on new project so you want to continue''')
    speak(" Jarvis is ready ")                   
    while True:
        r = sr.Recognizer()

        r.pause_threshold = 1.8
        r.non_speaking_duration = 0.5
  

        print("recognizing...")
        try:
            with sr.Microphone() as source:
                print("listening...")
                audio = r.listen(source,timeout=10,phrase_time_limit=5)
            
            word = r.recognize_google(audio)
            # if (word.lower() == "jarvis"):
            if "jarvis" in word.lower():
                speak("yes  boss")
                
                
                 #listen fo your the next command
                with sr.Microphone() as source:

                    print("jarvis is active")


                    r.adjust_for_ambient_noise(
                        source,
                        duration=0.5
                    )
                    audio = r.listen(source,timeout=None,phrase_time_limit=60)
                command = r.recognize_google(audio)
                print("Command heard:", command)

                processcommand(command)
                
        except Exception as e:
               print("error; {0}".format(e))   
           