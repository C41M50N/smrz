import datetime
import urllib.parse
from pydantic import BaseModel
import requests
from lxml import html

from app.lib.transcription import VideoTranscriber
from app.utils import get_json_from_url, parse_youtube_video_id


def get_video_transcript(video_transcriber: VideoTranscriber, url: str) -> str:
    return video_transcriber.transcribe_video(source_url=url)


class VideoMetadata(BaseModel):
    title: str | None = None
    channel: str | None = None
    published_date: datetime.date | None = None
    thumbnail_url: str | None = None


def extract_video_metadata(url: str) -> VideoMetadata:
    """
    Extract metadata from a YouTube video URL. This function assumes the URL is a valid YouTube video link.
    """

    video_id = parse_youtube_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube video URL")

    x = get_json_from_url(
        f"https://www.youtube.com/oembed?url={urllib.parse.quote(url)}&format=json"
    )

    title = x.get("title", None)
    channel = x.get("author_name", None)
    thumbnail_url = x.get("thumbnail_url", None)
    published_date = None
    try:
        published_date = _get_youtube_video_publish_date(url)
    except Exception:
        pass

    return VideoMetadata(
        title=title,
        channel=channel,
        published_date=published_date,
        thumbnail_url=thumbnail_url,
    )


def _get_youtube_video_publish_date(yt_url: str) -> datetime.date:
    """
    Extract the publish date from a YouTube video URL.

    Args:
        video_url (str): YouTube video URL

    Returns:
        str: Publish date in ISO format, or None if not found

    Raises:
        requests.RequestException: If the HTTP request fails
        ValueError: If the URL is invalid or date cannot be extracted
    """
    try:
        # Add headers to avoid being blocked
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(yt_url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse HTML with lxml
        tree = html.fromstring(response.text)

        # Find the publish date meta tag using XPath
        date_elements = tree.xpath('//meta[@itemprop="datePublished"]/@content')

        if date_elements:
            # Parse the date string using dateutil for flexibility
            date_str = date_elements[0]
            from dateutil import parser

            return parser.parse(date_str).date()
        else:
            raise ValueError("Publish date not found in the video page")

    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to fetch video page: {e}")
    except Exception as e:
        raise ValueError(f"Error extracting publish date: {e}")
