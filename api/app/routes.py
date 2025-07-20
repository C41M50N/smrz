from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.lib.llm_client import LLMClient, Models
from app.lib.summarization import SUMMARIZE_PROMPT_1, summarize_content
from app.lib.article_content import (
    ARTICLE_TO_MARKDOWN_PROMPT_2,
    extract_article_metadata,
    article_to_markdown,
)
from app.lib.video_content import extract_video_metadata, get_video_transcript
from app.lib.transcription import IMPROVE_TRANSCRIPT_PROMPT_1, VideoTranscriber
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
                transcript_readability_llm_client=LLMClient(
                    model=Models.GEMINI_2_5_FLASH_LITE_PREVIEW,
                    system_prompt=IMPROVE_TRANSCRIPT_PROMPT_1,
                ),
            )

            metadata = extract_video_metadata(url)
            title = metadata.title
            content = get_video_transcript(video_transcriber, url)
        else:
            metadata = extract_article_metadata(url)
            title = metadata.title
            content = article_to_markdown(
                llm_client=LLMClient(
                    model=Models.GEMINI_2_5_PRO,
                    system_prompt=ARTICLE_TO_MARKDOWN_PROMPT_2,
                ),
                url=url,
            )

        summary = f"# {title}\n\n" + summarize_content(
            llm_client=LLMClient(
                model=Models.GEMINI_2_5_FLASH_LITE_PREVIEW,
                system_prompt=SUMMARIZE_PROMPT_1,
            ),
            content=content,
        )
        print(f"\nSummary:\n{summary}")
        return JSONResponse(
            {
                "metadata": metadata.model_dump(mode="json"),
                "content": content,
                "summary": summary,
            },
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
