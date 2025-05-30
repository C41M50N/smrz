from fastapi import APIRouter

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
        return {"summary": summary}
    except RuntimeError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
