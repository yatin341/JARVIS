🤖 JARVIS — AI Voice Assistant

A Python-based personal AI voice assistant capable of understanding voice commands, speaking responses, opening websites, playing YouTube videos, answering questions using Groq AI, performing voice typing, and maintaining conversation history.

📌 Overview

JARVIS is a personal voice assistant built with Python.

The project combines:

🎤 Speech Recognition

🗣️ Text-to-Speech

🧠 Groq AI

🔊 ElevenLabs Voice

▶️ YouTube Integration

🌐 Web Browser Automation

⌨️ Voice Typing

💾 Conversation History

💻 Python-based Computer Automation

The goal of this project is to create a practical voice-controlled AI assistant that can interact with the computer and provide AI-powered responses.

✨ Features

🎤 Voice Recognition

JARVIS listens to the user's voice through the microphone and converts speech into text.

The project uses the SpeechRecognition Python library with Google's speech recognition service.

Example:

User: Jarvis

JARVIS: Yes boss

After activation, JARVIS listens for the next command.

🗣️ Text-to-Speech

JARVIS speaks its responses instead of only displaying them in the terminal.

The current project uses:

ElevenLabs

for natural voice output.

There is also a pyttsx3 fallback function available in the project.

Example:

JARVIS: Opening Google boss

🧠 Groq AI Integration

JARVIS uses the Groq API to answer general questions that are not handled by predefined commands.

For example:

User: What is an API?

JARVIS: An API is a way for different software applications to communicate...

The AI is also given system instructions so that it behaves like a friendly personal assistant named JARVIS.

🧠 Conversation Context

JARVIS can remember recent messages during the current session.

The project keeps a rolling conversation context so that follow-up questions can refer to previous questions.

Example:

User: What is Python?

JARVIS: Python is a programming language...

User: Who created it?

JARVIS: Python was created by Guido van Rossum.

The project currently keeps up to 10 recent exchanges in the active conversation context.

💾 Conversation History

JARVIS saves user questions and AI responses into:

history.json

The saved information follows this structure:

{
    "user": "What is Python?",
    "AI": "Python is a programming language..."
}

This provides a record of previous interactions.

🌐 Website Control

JARVIS can open several websites using voice commands.

Supported commands include:

Open Google
Open YouTube
Open LinkedIn
Open ChatGPT
Open Gemini
Open Brave
Open Instagram
Open Pinterest
Open WhatsApp
Open Netflix
Open Jio Hotstar
Open GitHub

For example:

User: Open Google

JARVIS: Opening Google boss

▶️ YouTube Search & Playback

JARVIS can search for a requested video or song on YouTube through the project's YouTube module.

Example:

User: Play Believer on YouTube

JARVIS extracts the requested song/video name and sends it to:

youtube.py

The YouTube module handles the playback/search functionality.

⌨️ Voice Typing

JARVIS includes a voice typing mode.

Say:

Start typing

JARVIS will activate voice typing and type your spoken words into the currently active application.

Special commands include:

enter
backspace
space
next line
stop typing

For example:

User: Start typing

JARVIS: Voice typing activated. Tell me what to type.

User: Hello, how are you?

JARVIS types:
Hello, how are you?

Voice typing uses:

PyAutoGUI
Pyperclip
SpeechRecognition

💻 Computer Automation

JARVIS uses PyAutoGUI to interact with the computer.

It can:

Type text

Press keyboard keys

Paste clipboard content

Perform basic application interaction

The project can be extended with additional computer-control features.

🛠️ Technologies Used

Technology

Purpose

Python

Main programming language

SpeechRecognition

Voice-to-text

Google Speech Recognition

Speech recognition

Groq API

AI responses

ElevenLabs

Text-to-speech

pyttsx3

Fallback text-to-speech

PyAutoGUI

Computer automation

Pyperclip

Clipboard operations

Webbrowser

Opening websites

JSON

Conversation history

YouTube module

YouTube playback

📂 Project Structure

JARVIS/
│
├── mega_project_jarvis.py
├── youtube.py
├── history.json
├── requirements.txt
├── README.md
└── .gitignore

mega_project_jarvis.py

The main JARVIS program.

It handles:

Speech recognition

Voice activation

Text-to-speech

AI communication

Conversation context

Website opening

YouTube command handling

Voice typing

Computer automation

Conversation history

youtube.py

Handles the YouTube functionality used by JARVIS.

It receives the requested song/video and performs the YouTube playback operation.

history.json

Stores previous user questions and JARVIS responses.

This file is generated/updated while the assistant runs.

requirements.txt

Contains the Python packages required to install and run JARVIS.

README.md

Project documentation and setup instructions.

.gitignore

Prevents private information and unnecessary files from being uploaded to GitHub.

📦 Installation

1. Clone the Repository

Open PowerShell or Command Prompt:

git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git

Move into the project folder:

cd YOUR-REPOSITORY

2. Create a Virtual Environment

It is recommended to use a virtual environment.

python -m venv venv

Activate it on Windows:

venv\Scripts\activate

You should see something similar to:

(venv)

in your terminal.

3. Install Dependencies

Run:

pip install -r requirements.txt

If you have not created requirements.txt yet, install the packages used by the project:

pip install SpeechRecognition pyttsx3 groq pyautogui pyperclip elevenlabs

webbrowser, time, os, and json are part of Python's standard library and do not normally need separate installation.

🔑 API Configuration

JARVIS uses external APIs for AI responses and voice generation.

You need:

1. Groq API Key

Used for:

AI responses

2. ElevenLabs API Key

Used for:

Text-to-speech

⚠️ IMPORTANT: Protect Your API Keys

Never upload your API keys directly to GitHub.

Do NOT do this:

groq_client = Groq(
    api_key="YOUR_REAL_API_KEY"
)

or:

eleven_client = ElevenLabs(
    api_key="YOUR_REAL_API_KEY"
)

Instead, use environment variables.

🔐 Using a .env File

Create:

.env

Example:

GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

Then add .env to .gitignore.

🚫 .gitignore

A recommended .gitignore:

.env
venv/
.venv/
__pycache__/
*.pyc
history.json

This prevents API keys, virtual environments, generated files, and private conversation history from being uploaded.

▶️ Running JARVIS

After installing the dependencies and configuring your API keys, run:

python mega_project_jarvis.py

JARVIS will initialize and speak:

Jarvis is ready

🎤 How to Use

Once JARVIS is running, say:

Jarvis

JARVIS will respond:

Yes boss

Then give your command.

💬 Example Commands

Open Google

Open Google

Open YouTube

Open YouTube

Open LinkedIn

Open LinkedIn

Open ChatGPT

Open ChatGPT

Open Gemini

Open Gemini

Open WhatsApp

Open WhatsApp

Open GitHub

Open GitHub

Play a YouTube Video

Play Believer on YouTube

or:

Play Shape of You on YouTube

Start Voice Typing

Start typing

Then speak the text you want JARVIS to type.

🧠 How JARVIS Works

The basic workflow is:

                 ┌──────────────────┐
                 │      User        │
                 │   Voice Command  │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │     Speech       │
                 │   Recognition    │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Convert Speech   │
                 │     → Text       │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │     Command      │
                 │    Processing    │
                 └───────┬───┬──────┘
                         │   │
                ┌────────┘   └─────────┐
                ▼                      ▼
       ┌─────────────────┐    ┌─────────────────┐
       │ Specific Command│    │     Groq AI     │
       │                 │    │                 │
       │ Google          │    │ General         │
       │ YouTube         │    │ Questions       │
       │ Websites        │    │ Conversation    │
       │ Voice Typing    │    │                 │
       └────────┬────────┘    └────────┬────────┘
                │                      │
                └──────────┬───────────┘
                           ▼
                 ┌──────────────────┐
                 │ JARVIS Response  │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │   ElevenLabs     │
                 │  Text-to-Speech  │
                 └────────┬─────────┘
                          │
                          ▼
                    🔊 JARVIS Speaks

🔄 Command Processing

JARVIS first checks whether the command matches one of its predefined commands.

For example:

open google

is handled directly by JARVIS.

If the command is:

What is artificial intelligence?

and it does not match a predefined command, JARVIS sends it to Groq AI.

This creates two levels of command processing:

User Command
     │
     ▼
Is it a predefined command?
     │
   ┌─┴─┐
 YES   NO
  │     │
  ▼     ▼
Action Groq AI
        │
        ▼
     Response

🔌 APIs & Services Used

Groq API

Groq provides the AI intelligence behind JARVIS.

It allows the assistant to:

Answer general questions

Understand conversation context

Generate natural-language responses

Handle questions that are not predefined commands

ElevenLabs

ElevenLabs provides the voice output.

JARVIS sends the generated response to ElevenLabs and plays the returned audio.

The current project uses an ElevenLabs Flash model for faster voice generation.

Google Speech Recognition

Google Speech Recognition is used to convert microphone audio into text.

This allows users to interact with JARVIS using natural voice commands.

🧪 Testing

Before running the complete assistant, make sure:

Your microphone works

Speech recognition is available

Your API keys are configured

Your internet connection is working

ElevenLabs audio playback is configured correctly

You can test individual components separately while developing the project.

🖥️ System Requirements

Recommended environment:

Operating System: Windows
Python: 3.x
Microphone: Required
Internet Connection: Required
Web Browser: Required

An internet connection is required for services such as:

Google Speech Recognition

Groq API

ElevenLabs

YouTube functionality

⚠️ Troubleshooting

Microphone Not Working

Make sure:

Your microphone is connected.

Windows has microphone permissions enabled.

Your correct microphone is selected.

SpeechRecognition dependencies are installed.

ModuleNotFoundError

If Python says:

ModuleNotFoundError: No module named 'something'

try:

pip install something

Or reinstall the project dependencies:

pip install -r requirements.txt

Groq API Error

If Groq returns an error, check:

API key

Internet connection

Selected model

API limits/quota

Current API availability

ElevenLabs Voice Error

Check:

ElevenLabs API key

Voice ID

ElevenLabs account/API limits

Audio playback configuration

🔒 Security

This project uses API keys.

For security:

Never commit:

.env

Never publish:

GROQ_API_KEY
ELEVENLABS_API_KEY

If you accidentally expose an API key:

Immediately revoke/regenerate the exposed key from the relevant provider.

Do not simply delete the key from the latest commit and assume it is safe; exposed secrets can remain in Git history.

🚀 Future Improvements

This project can be expanded significantly.

Possible future features include:

🌤️ Weather information

📰 News headlines

⏰ Alarms and reminders

📅 Calendar integration

📧 Email automation

💻 Advanced PC control

🔊 Faster voice interaction

🗣️ Custom wake word

🧠 Long-term memory

📱 Mobile application

🌐 Web dashboard

👁️ Computer vision

📷 Image understanding

🎵 Better music control

📁 File management

🔍 Advanced web search

🔐 User authentication

🎙️ More natural voice interaction

📈 Project Roadmap

Phase 1 — Basic Assistant

Python setup

Speech recognition

Text-to-speech

Basic command processing

Browser control

Phase 2 — AI Integration

Groq API

AI-generated responses

Natural-language questions

Conversation context

Phase 3 — Voice & Automation

ElevenLabs voice

Voice typing

Keyboard automation

Clipboard automation

Phase 4 — YouTube & Web Automation

YouTube integration

Video/song playback

Website commands

Browser automation

Phase 5 — Advanced AI Assistant

Long-term memory

Custom wake word

Computer vision

Advanced PC control

GUI dashboard

Personal automation

Offline capabilities

📚 What I Learned From This Project

Building JARVIS helped me practice:

Python programming

Functions

Conditional statements

Loops

Exception handling

APIs

JSON

Speech recognition

Text-to-speech

Browser automation

Computer automation

Clipboard operations

Environment variables

Python modules

Conversation memory

Debugging

Git and GitHub

🎓 Educational Purpose

This project was created as a learning project to understand how different technologies can be combined to build an AI-powered voice assistant.

It demonstrates how Python can connect:

Voice
  +
AI
  +
APIs
  +
Automation
  +
Text-to-Speech
  =
AI Voice Assistant

🤝 Contributing

Contributions and suggestions are welcome.

If you want to improve the project:

Fork the repository.

Create a new branch.

git checkout -b feature/new-feature

Make your changes.

Commit your changes.

git add .
git commit -m "Add new feature"

Push your branch.

git push origin feature/new-feature

Open a Pull Request.

⭐ Support

If you find this project useful or interesting, consider giving the repository a ⭐ on GitHub.

Feedback and suggestions are also welcome.

👨‍💻 Author

Yatin Jangra

B.Tech — Artificial Intelligence & Machine Learning

Interested in:

Python

Artificial Intelligence

Machine Learning

Voice Assistants

Automation

APIs

This project is part of my journey of learning Python, AI, APIs, and automation.

📜 License

This project is created for educational and personal learning purposes.

If you reuse significant portions of the project, please give appropriate credit to the original repository.

⚠️ Disclaimer

JARVIS is an educational personal-assistant project.

The project depends on third-party services and APIs. Availability, quotas, authentication requirements, pricing, and functionality may change according to those services.

API keys must be kept private and should never be committed to a public GitHub repository.

⭐ If You Like This Project

Give it a star ⭐

Follow the repository for future updates.

More JARVIS features are planned! 🚀

Built with Python 🐍 + AI 🧠 + Voice 🎙️ + Automation 💻 + APIs 🔌00   