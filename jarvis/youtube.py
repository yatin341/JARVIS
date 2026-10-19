import os
from pathlib import Path
from dotenv import load_dotenv
from googleapiclient.discovery import build
import webbrowser

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")


def play_on_youtube(query):
    if not YOUTUBE_API_KEY:
        return "YouTube API key is missing from .env."

    try:
        youtube = build(
            "youtube",
            "v3",
            developerKey=YOUTUBE_API_KEY
        )

        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=1
        )

        response = request.execute()

        if response.get("items"):
            video_id = response["items"][0]["id"]["videoId"]
            url = f"https://www.youtube.com/watch?v={video_id}"
            webbrowser.open(url)
            return f"Playing {query} on YouTube."

        return "Sorry, I could not find that video."

    except Exception as e:
        print("YouTube API error:", e)
        return "Sorry boss, YouTube search failed."
