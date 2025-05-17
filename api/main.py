import re
import os
from typing import Generator
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from newspaper import Article
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()

app = FastAPI()

openai_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


@app.get("/")
def index():
    return "Hello, World!"


@app.get("/summarize")
def summarize(url: str):
    """
    Summarize the content from the given URL.
    """
    # Check if url is valid
    if not url.startswith(("http://", "https://")):
        return {"error": "Invalid URL. Please provide a valid URL."}

    try:
        if is_valid_youtube_url(url):
            content = get_video_transcript(url)
        else:
            content = get_text_content(url)

        summary = summarize_content(content)
        return {"summary": summary}
    except RuntimeError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@app.get("/summarize/stream")
def summarize_stream(url: str):
    """
    Summarize the content from the given URL. (Streaming version)
    This version is designed to handle larger content by streaming the response.
    """
    # Check if url is valid
    if not url.startswith(("http://", "https://")):
        return {"error": "Invalid URL. Please provide a valid URL."}

    try:
        if is_valid_youtube_url(url):
            content = get_video_transcript(url)
        else:
            content = get_text_content(url)

        return StreamingResponse(
            summarize_content_stream(content),
            media_type="text/plain",
        )
    except RuntimeError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


def get_text_content(url: str) -> str:
    """
    Extract text content from the given URL using Newspaper3k.
    """
    article = Article(url)
    article.download()
    article.parse()
    return article.text


def get_video_transcript(url: str) -> str:
    """
    Extract video transcript from the given URL.
    """
    video_id = get_youtube_video_id(url)
    ytt_api = YouTubeTranscriptApi()
    try:
        transcript = ytt_api.fetch(video_id)
        transcript_text = " ".join([t.text for t in transcript])
        return transcript_text
    except Exception:
        raise RuntimeError("Failed to fetch video transcript")


# Regular expression patterns to match various YouTube URL formats
# and capture the video ID.
# The video ID is typically 11 characters long and can contain
# letters (upper and lower case), numbers, underscores, and hyphens.
VALID_YOUTUBE_URL_PATTERNS = [
    r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})",  # Standard format
    r"(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]{11})",  # Shortened format
    r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})",  # Embed format
    r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([a-zA-Z0-9_-]{11})",  # Older embed format
    r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})",  # Shorts format
    r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/live\/([a-zA-Z0-9_-]{11})",  # Live format
]


def is_valid_youtube_url(url: str) -> bool:
    """
    Check if the given URL is a valid YouTube video URL.

    Args:
        url: The YouTube video URL string.

    Returns:
        True if the URL is valid, False otherwise.
    """
    return any(re.match(pattern, url) for pattern in VALID_YOUTUBE_URL_PATTERNS)


def get_youtube_video_id(url: str) -> str:
    """
    Extracts the YouTube video ID from a given YouTube video URL.

    Args:
        url: The YouTube video URL string.

    Returns:
        The YouTube video ID.

    Raises:
        RuntimeError: If the video ID cannot be extracted or the URL is invalid.
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


SYSTEM_PROMPT = """
# IDENTITY and PURPOSE
You are a summarization system that extracts the most interesting, useful, and surprising aspects of an article or video transcript.
Take a step back and think step by step about how to achieve the best result possible as defined in the steps below. You have a lot of freedom to make this work well.

## OUTPUT SECTIONS
1. You extract a summary of the content in 30 words or less, including who is presenting and the content being discussed into a section called SUMMARY.
2. You extract the top 3 to 7 ideas from the input in a section called IDEAS:.
3. You extract the 4 to 8 most insightful and interesting quotes from the input into a section called QUOTES:. Use the exact quote text from the input.
4. You extract the 4 to 8 most insightful and interesting recommendations that can be collected from the content into a section called RECOMMENDATIONS.

## OUTPUT INSTRUCTIONS
1. You only output Markdown.
2. Do not give warnings or notes; only output the requested sections.
3. Use H3 headers for each section.
4. You use bullets (`-`), not numbered lists.
5. Do not repeat ideas, or quotes.
6. Do not start items with the same opening words.
"""


def summarize_content(content: str) -> str:
    """
    Summarize the given content using OpenAI's API.
    """

    response = openai_client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Summarize the following content: {content}"},
        ],
    )

    return response.choices[0].message.content


def summarize_content_stream(content: str) -> Generator:
    """
    Summarize the given content using OpenAI's API. (Streaming version)
    This version is designed to handle larger content by streaming the response.
    """

    response = openai_client.chat.completions.create(
        model="gemini-2.0-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Summarize the following content: {content}"},
        ],
        stream=True,
    )

    # Collect the streamed response
    for chunk in response:
        yield chunk.choices[0].delta.content
