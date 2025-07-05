import urllib.parse
import requests
import urllib

from app.lib.transcription import VideoTranscriber


def get_youtube_video_title(url: str) -> str:
    """
    Extract the title of a YouTube video from its URL.
    """
    # Method 1: Using oEmbed API (no API key required)
    try:
        oembed_url = (
            f"https://www.youtube.com/oembed?url={urllib.parse.quote(url)}&format=json"
        )
        response = requests.get(oembed_url)
        if response.status_code != 200:
            raise RuntimeError("Failed to fetch video title")
        return response.json()["title"]
    except Exception:
        raise RuntimeError("Failed to fetch video title")


def get_video_transcript(video_transcriber: VideoTranscriber, url: str) -> str:
    return video_transcriber.transcribe_video(source_url=url)
