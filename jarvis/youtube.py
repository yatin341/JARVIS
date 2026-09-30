from googleapiclient.discovery import build
import webbrowser

YOUTUBE_API_KEY = "AIzaSyBM4rDRv-Rzpt3Y6PEMRLZgd6RakkkeMeU"


def play_on_youtube(query):

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

    if response["items"]:
        video_id = response["items"][0]["id"]["videoId"]

        url = f"https://www.youtube.com/watch?v={video_id}"

        webbrowser.open(url)

        return f"Playing {query} on YouTube."

    return "Sorry, I could not find that video."