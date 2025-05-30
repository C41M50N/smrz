from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.article.actions import (
    article_to_markdown,
    get_article_title,
)
from app.common.actions import (
    get_clean_html,
    summarize_content,
)
from app.video.actions import (
    get_video_transcript,
    get_youtube_video_title,
    improve_transcript_readability,
    is_valid_youtube_url,
)

router = APIRouter()


@router.get("/")
def index():
    return "fine, i'll do it myself"


@router.get("/smrz")
def summarize(url: str):
    """
    Summarize the content from the given URL.
    """
    # Check if url is valid
    if not url.startswith(("http://", "https://")):
        return {"error": "Invalid URL. Please provide a valid URL."}

    try:
        if is_valid_youtube_url(url):
            title = get_youtube_video_title(url)
            transcript = get_video_transcript(url)
            content = improve_transcript_readability(transcript, title)
            print(f"Video Title: {title}\nTranscript:\n{content}")
        else:
            title = get_article_title(url)
            html = get_clean_html(url)
            content = article_to_markdown(url, html)
            print(f"Article Title: {title}\nContent:\n{content}")

        summary = f"# {title}\n\n" + summarize_content(content)
        print(f"\nSummary:\n{summary}")
        return JSONResponse(
            {"title": title, "content": content, "summary": summary},
            status_code=status.HTTP_200_OK,
        )
    except RuntimeError as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        return JSONResponse(
            {"error": f"An unexpected error occurred: {str(e)}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
