import re
import requests
from lxml_html_clean import Cleaner

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


#############################################################################
################################## MARKUP ###################################
#############################################################################


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


def clean_markdown(markdown: str) -> str:
    """
    Cleans the given Markdown content by removing empty lines and trimming lines.
    """
    # Trim all lines
    markdown = "\n".join(line.strip() for line in markdown.splitlines())
    # Make sure there are exactly one empty line between all lines that are not empty.
    # This ensures that paragraphs are separated by a single blank line.
    markdown = re.sub(r"\n\s*\n+", "\n\n", markdown)
    # Remove all empty lines between list items (both ordered and unordered)
    # This ensures that consecutive list items are not separated by blank lines.
    markdown = re.sub(
        r"((?:^|\n)[ \t]*[-*+] .+?)\n(?:[ \t]*\n)+(?=[ \t]*[-*+] )",
        r"\1\n",
        markdown,
        flags=re.MULTILINE,
    )
    markdown = re.sub(
        r"((?:^|\n)[ \t]*\d+\.\s.+?)\n(?:[ \t]*\n)+(?=[ \t]*\d+\.\s)",
        r"\1\n",
        markdown,
        flags=re.MULTILINE,
    )
    return markdown.strip()


#############################################################################
################################### MISC ####################################
#############################################################################


def is_direct_audio_url(url: str) -> bool:
    """
    Check if the given URL is a direct link to an audio file.
    """
    return url.lower().endswith((".mp3", ".wav", ".ogg", ".flac", ".aac"))


def is_direct_video_url(url: str) -> bool:
    """
    Check if the given URL is a direct link to a video file.
    """
    return url.lower().endswith((".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv"))
