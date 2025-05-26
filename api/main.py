from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from api.utils import (
    convert_to_markdown,
    summarize_content,
    get_article_title,
    get_clean_html,
    get_video_transcript,
    get_youtube_video_title,
    is_valid_youtube_url,
)

load_dotenv()

app = FastAPI()


@app.get("/")
def index():
    return "Hello, World!"


@app.get("/mkdn")
def markdown(url: str):
    """
    Test if the given URL is valid.
    """
    # Check if url is valid
    if not url.startswith(("http://", "https://")):
        return {"error": "Invalid URL. Please provide a valid URL."}

    try:
        title = get_article_title(url)
        html = get_clean_html(url)
        with open("article.html", "w") as f:
            f.write(html)
        markdown = convert_to_markdown(url, html)
        print(markdown)
        return {"title": title, "content": markdown}
    except RuntimeError as e:
        return {"error": str(e)}
    except Exception as e:
        return JSONResponse({"error": f"An error occurred: {str(e)}"}, status_code=500)


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
            title = get_youtube_video_title(url)
        else:
            title = get_article_title(url)
            html = get_clean_html(url)
            content = convert_to_markdown(url, html)
            print(content)

        summary = f"# {title}\n\n" + summarize_content(content)
        return {"summary": summary}
    except RuntimeError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
