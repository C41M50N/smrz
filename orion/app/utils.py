import datetime
import re
import urllib.parse

import requests
from dateutil import parser
from lxml import html
from lxml.html.clean import Cleaner
from newspaper import Article
from pydantic import BaseModel


def get_clean_html(url: str) -> str:
    """
    Fetches the HTML content from the specified URL and returns a cleaned version of the HTML.
    """
    try:
        html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
        cleaner = Cleaner()
        cleaned_html = cleaner.clean_html(html)
        # Remove all empty lines and trim all lines
        cleaned_html = "\n".join(
            line.strip() for line in cleaned_html.splitlines() if line.strip()
        )
        return cleaned_html
    except Exception:
        raise RuntimeError("Failed to fetch or clean HTML content")


def get_json_from_url(url: str) -> dict[str, str]:
    """
    Fetch JSON data from a URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch JSON from {url}: {e}")


def parse_date(date_str: str) -> datetime.date:
    """
    Parse a date string into a datetime.date object.
    Uses dateutil.parser for flexibility in date formats.
    """
    try:
        return parser.parse(date_str, fuzzy=True).date()
    except Exception as e:
        raise ValueError(f"Failed to parse date '{date_str}': {e}")


#############################################################################
################################# YOUTUBE ###################################
#############################################################################

# Regular expression patterns to match various YouTube URL formats and capture the video ID.
# The video ID is typically 11 characters long and can contain letters (upper and lower case),
# numbers, underscores, and hyphens.
VALID_YOUTUBE_URL_PATTERNS = [
    r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})",  # Standard format
    r"(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]{11})",  # Shortened format
    r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})",  # Embed format
    r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([a-zA-Z0-9_-]{11})",  # Older embed format
    r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})",  # Shorts format
    r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/live\/([a-zA-Z0-9_-]{11})",  # Live format
]


def is_youtube_url(url: str) -> bool:
    """
    Check if the given URL is a valid YouTube video URL.
    """
    return any(re.match(pattern, url) for pattern in VALID_YOUTUBE_URL_PATTERNS)


def parse_youtube_video_id(url: str) -> str:
    """
    Extracts the YouTube video ID from a given YouTube video URL.
    """
    for pattern in VALID_YOUTUBE_URL_PATTERNS:
        match = re.search(pattern, url)
        if match:
            # The video ID is in the first capturing group
            video_id = match.group(1)
            # Further validation: ensure the extracted ID is exactly 11 characters
            # and contains only valid characters. This is mostly handled by the regex
            # but an explicit check can be an extra safeguard.
            if len(video_id) == 11 and re.fullmatch(r"[a-zA-Z0-9_-]+", video_id):
                return video_id

    # If no pattern matched or the extracted ID was not valid
    raise RuntimeError("Invalid YouTube video URL or unable to extract video ID.")


def normalize_youtube_url(url: str) -> str:
    """
    Normalize a YouTube URL to a standard format.
    This function will convert any valid YouTube URL to the standard watch format.
    """
    video_id = parse_youtube_video_id(url)
    return f"https://www.youtube.com/watch?v={video_id}"


###############################################################################


class ArticleMetadata(BaseModel):
    title: str
    author: str | None = None
    published_date: datetime.date | None = None
    favicon: str | None = None
    meta_image: str | None = None


def extract_article_metadata(url: str) -> ArticleMetadata:
    """
    Extract metadata from an article using Newspaper3k.
    """
    article = Article(url)
    article.download()
    article.parse()

    published_date = article.publish_date
    if isinstance(published_date, str):
        try:
            published_date = parse_date(published_date)
        except ValueError:
            published_date = None
    elif isinstance(published_date, datetime.datetime):
        published_date = published_date.date()
    elif not isinstance(published_date, datetime.datetime):
        published_date = None

    return ArticleMetadata(
        title=article.title,
        author=", ".join(article.authors) if article.authors else None,
        published_date=published_date,  # type: ignore
        favicon=f"https://{url.split('/')[2]}/favicon.ico",
        meta_image=article.meta_img,
    )


###############################################################################


class YoutubeMetadata(BaseModel):
    title: str
    channel: str | None = None
    published_date: datetime.date | None = None
    thumbnail_url: str | None = None


def extract_youtube_metadata(url: str) -> YoutubeMetadata:
    """
    Extract metadata from a YouTube video URL. This function assumes the URL is a valid YouTube video link.
    """

    video_id = parse_youtube_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube video URL")

    x = get_json_from_url(
        f"https://www.youtube.com/oembed?url={urllib.parse.quote(url)}&format=json"
    )

    title = x["title"]
    channel = x.get("author_name", None)
    thumbnail_url = x.get("thumbnail_url", None)
    published_date = None
    try:
        published_date = _get_youtube_video_publish_date(url)
    except Exception:
        pass

    return YoutubeMetadata(
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
