from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.features.transcription import YoutubeVideoTranscriber
from app.utils import (
    extract_article_metadata,
    extract_youtube_metadata,
    get_clean_html,
    is_youtube_url,
    normalize_youtube_url,
)


router = APIRouter()


@router.get("/")
def index():
    return "fine, i'll do it myself"


@router.get("/clean-html", description="Returns cleaned HTML content from a URL.")
def clean_html(url: str):
    return JSONResponse(
        content={"html": get_clean_html(url)}, status_code=status.HTTP_200_OK
    )


@router.get("/article-metadata", description="Returns metadata for an article.")
def article_metadata(url: str):
    return JSONResponse(
        content=extract_article_metadata(url), status_code=status.HTTP_200_OK
    )


@router.get("/youtube-metadata", description="Returns metadata for a YouTube video.")
def youtube_metadata(url: str):
    if not is_youtube_url(url):
        return JSONResponse(
            content={"error": "Invalid YouTube URL"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return JSONResponse(
        content=extract_youtube_metadata(url), status_code=status.HTTP_200_OK
    )


@router.get(
    "/youtube-transcription",
    description="Returns the transcription of a YouTube video.",
)
def youtube_transcription(url: str):
    if not is_youtube_url(url):
        return JSONResponse(
            content={"error": "Invalid YouTube URL"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    url = normalize_youtube_url(url)
    transcriber = YoutubeVideoTranscriber()
    return JSONResponse(
        content={"transcription": transcriber.transcribe_video(url)},
        status_code=status.HTTP_200_OK,
    )
