from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.lib.summarization import summarize_content
from app.lib.article_content import (
    get_article_title,
    article_to_markdown,
)
from app.lib.video_content import get_video_transcript, get_youtube_video_title
from app.lib.transcription import VideoTranscriber


from app.utils import (
    is_youtube_url,
    is_direct_audio_url,
    is_direct_video_url,
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
        if is_youtube_url(url) or is_direct_video_url(url) or is_direct_audio_url(url):
            video_transcriber = VideoTranscriber(
                transcript_readability_llm_client=OpenRouterLLMClient,
                transcript_readability_model=OpenRouterModel.GEMINI_2_5_FLASH_PREVIEW,
            )
            title = None
            if is_youtube_url(url):
                title = get_youtube_video_title(url)

            content = get_video_transcript(video_transcriber, url)
        else:
            title = get_article_title(url)
            content = article_to_markdown(
                llm_client=OpenRouterLLMClient,
                model=OpenRouterModel.GEMINI_2_5_FLASH_PREVIEW,
                url=url,
            )

        summary = f"# {title}\n\n" + summarize_content(
            llm_client=OpenRouterLLMClient,
            model=OpenRouterModel.GEMINI_2_5_FLASH_PREVIEW,
            content=content,
        )
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
