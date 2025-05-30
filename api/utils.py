from enum import Enum
import os
import re
import urllib

from dotenv import load_dotenv
import requests
from lxml_html_clean import Cleaner
from newspaper import Article
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi

###############################################################################
#################################### HTML #####################################
###############################################################################


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


###############################################################################
################################## MARKDOWN ###################################
###############################################################################


def clean_markdown(markdown: str) -> str:
    """
    Cleans the given Markdown content by removing empty lines and trimming lines.
    """
    # Trim all lines
    markdown = "\n".join(line.strip() for line in markdown.splitlines())
    # Remove all empty lines immediately after any markdown heading (e.g., #, ##, ###, etc.)
    markdown = re.sub(r"^(#{1,6} .*)\n(\s*\n)+", r"\1\n", markdown, flags=re.MULTILINE)
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
    # Remove all empty lines and trim all lines
    cleaned_markdown = "\n".join(
        line.strip() for line in markdown.splitlines() if line.strip()
    )
    return cleaned_markdown


###############################################################################
################################## ARTICLE ####################################
###############################################################################


def get_article_title(url: str) -> str:
    """
    Extract the title of an article from its URL using Newspaper3k.
    """
    article = Article(url)
    article.download()
    article.parse()
    return article.title


###############################################################################
################################### VIDEO #####################################
###############################################################################


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
    """
    return any(re.match(pattern, url) for pattern in VALID_YOUTUBE_URL_PATTERNS)


def get_youtube_video_id(url: str) -> str:
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


def get_youtube_video_title(url: str) -> str:
    """
    Extract the title of a YouTube video from its URL.
    """
    # Method 1: Using oEmbed API (no API key required)
    try:
        oembed_url = (
            f"https://www.youtube.com/oembed?url={urllib.parse.quote(url)}&format=json"
        )
        response = requests.get(oembed_url)
        if response.status_code == 200:
            return response.json()["title"]
    except Exception:
        raise RuntimeError("Failed to fetch video title")


def get_video_transcript(url: str) -> str:
    """
    Extract video transcript from the given URL.
    """
    video_id = get_youtube_video_id(url)
    ytt_api = YouTubeTranscriptApi()

    # Retry fetch transcript up to 7 times in case of transient errors
    attempts = 0
    max_attempts = 7
    while attempts < max_attempts:
        try:
            transcript = ytt_api.fetch(video_id)
            transcript_text = " ".join([t.text for t in transcript]).replace("\n", " ")
            return transcript_text
        except Exception as e:
            attempts += 1
            if attempts >= max_attempts:
                print(f"Error fetching transcript after {max_attempts} attempts: {e}")
                raise RuntimeError("Failed to fetch video transcript")


###############################################################################
##################################### AI ######################################
###############################################################################

# Make sure to load LLM environment variables
load_dotenv()

openrouter_client = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)


class OpenRouterModels(str, Enum):
    """
    Enum for OpenRouter model references.
    """

    GEMMA_3_27B_IT = "google/gemma-3-27b-it"
    CLAUDE_3_5_HAIKU = "anthropic/claude-3.5-haiku"
    LLAMA_4_MAVERICK = "meta-llama/llama-4-maverick"


gemini_client = OpenAI(
    api_key=os.environ.get("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


class GeminiModels(str, Enum):
    """
    Enum for Gemini model references.
    """

    GEMINI_2_0_FLASH = "gemini-2.0-flash"
    GEMINI_2_5_FLASH = "gemini-2.5-flash-preview-05-20"
    GEMINI_2_5_PRO = "gemini-2.5-pro-preview-05-06"


############################ CONVERT TO MARKDOWN ##############################

CONVERT_TO_MARKDOWN_PROMPT = """
# TASK
You convert web content to clean Markdown format. You must preserve ALL original content while removing ads and unrelated sections.

# WHAT TO KEEP
- Main article text
- Article title 
- All headings and subheadings
- Lists and bullet points
- Links within the content
- Images that are part of the article
- Code blocks and examples
- References if they belong to the main article

# WHAT TO REMOVE
- Ads and advertisements
- Newsletter signup boxes
- Comments sections
- Sidebars with unrelated content
- Navigation menus
- Footer content

# STEP-BY-STEP PROCESS
1. Find the main article title - this becomes your H1 heading with `#`
2. Find the main article content - ignore everything else
3. Convert HTML tags to Markdown:
   - `<h2>` becomes `##`
   - `<h3>` becomes `###`
   - `<strong>` or `<b>` becomes `**text**`
   - `<em>` or `<i>` becomes `*text*`
4. Convert HTML codes to normal characters:
   - `&amp;` becomes `&`
   - `&lt;` becomes `<`
   - `&gt;` becomes `>`
   - `&#8211;` becomes `-`
   - `&#8217;` becomes `'`
5. Format lists properly:
   - Bullet points: `- item`
   - Numbered lists: `1. item`
6. Format links: `[link text](url)`
7. Fix image URLs and format them:
   - If image URL starts with `/` (like `/images/photo.jpg`), add the website domain to make it complete
   - Example: `/images/photo.jpg` becomes `https://example.com/images/photo.jpg`
   - Format as: `![description](complete-image-url)` on its own line

# IMAGE URL RULES
- Partial URLs that start with `/` are incomplete
- Add the main website URL to the beginning to make them work
- Example: If the website is `https://techblog.com` and image is `/assets/diagram.png`
- Result: `https://techblog.com/assets/diagram.png`
- Keep full URLs (starting with `http://` or `https://`) as they are

# FORMATTING RULES
- Put article title as `# Title` at the top
- No empty lines between paragraphs
- No empty lines after headings
- Put one empty line before and after blockquotes
- Put images on separate lines with empty lines before and after
- Never have two empty lines in a row
- Keep all links inline with the text

# OUTPUT
Only output the final Markdown. Do not add explanations, warnings, or notes. Start with the article title as H1.
"""


def convert_to_markdown(url: str, html: str) -> str:
    """
    Convert the given content to Markdown using OpenAI's API.
    """

    response = openrouter_client.chat.completions.create(
        model=f"{OpenRouterModels.LLAMA_4_MAVERICK}:nitro",
        messages=[
            {"role": "system", "content": CONVERT_TO_MARKDOWN_PROMPT},
            {
                "role": "user",
                "content": f"Convert the following article HTML (found at {url}) to Markdown: {html}",
            },
        ],
    )

    markdown = response.choices[0].message.content
    if not markdown:
        raise RuntimeError("Failed to convert HTML to Markdown")

    return clean_markdown(markdown)


##################### IMPROVE TRANSCRIPT READABILITY ##########################

IMPROVE_TRANSCRIPT_PROMPT = """
# IDENTITY and PURPOSE
You are an expert at structuring video transcripts for improved readability. Your task is to add clear, descriptive headers and subheaders to video transcripts WITHOUT modifying, summarizing, or removing any of the original content.

## Instructions:

1. **Preserve ALL original text**: Keep every word, sentence, and paragraph exactly as written in the transcript. Do not summarize, paraphrase, or omit any content.

2. **Add strategic headers**: Insert headers and subheaders that break up the content into logical sections based on topic shifts, narrative flow, or structural elements.

3. **Use descriptive header formats**:
   - **Intro** - Opening remarks, introductions, setup
   - **Background** - Context, history, or foundational information  
   - **Main Point #1: [Specific Topic]** - First major point or argument
   - **Main Point #2: [Specific Topic]** - Second major point or argument
   - **Reason #1: [Specific Reason]** - Supporting reasons or evidence
   - **Example: [Brief Description]** - Case studies, stories, or illustrations
   - **Discussion** - Analysis, debate, or exploration of ideas
   - **Q&A** - Question and answer segments
   - **Key Takeaways** - Important conclusions or insights
   - **Conclusion** - Final thoughts, wrap-up
   - **Outro** - Closing remarks, calls to action, sign-offs

4. **Header placement guidelines**:
   - Insert headers at natural topic transitions
   - Place headers before the relevant content begins
   - Use subheaders (with ##) for subsections within main topics
   - Ensure headers reflect the actual content that follows

5. **Formatting**:
   - Use markdown header formatting (## for main headers, ### for subheaders)
   - Make headers specific and descriptive rather than generic
   - Remove any unneccessary paragraph breaks that do not separate distinct ideas

6. **What NOT to do**:
   - Do not change any original wording (but you can remove newlines in the middle of sentences)
   - Do not add your own commentary or explanations
   - Do not create summaries or bullet points
   - Do not rearrange the content order
   - Do not remove filler words, repetitions, or speech patterns

## Example Output Format:

```
## Intro
[Original transcript text for introduction...]

## Main Point #1: The Importance of Time Management
[Original transcript text about time management...]

### Example: The Pomodoro Technique
[Original transcript text about the example...]

## Main Point #2: Building Better Habits
[Original transcript text about habits...]

## Conclusion
[Original transcript text for conclusion...]

## Outro
[Original transcript text for closing...]
```

Only output Markdown with the added headers and subheaders. Do not include any additional explanations, notes, or formatting outside of the headers. Do not wrap the markdown in a code block or any other formatting.

Your goal is to make the transcript easier to navigate and read while maintaining 100% fidelity to the original content.
"""


def improve_transcript_readability(transcript: str, title: str) -> str:
    """
    Improve the readability of a video transcript by adding headers and subheaders.
    This function uses OpenAI's API to process the transcript.
    """

    response = gemini_client.chat.completions.create(
        model=GeminiModels.GEMINI_2_0_FLASH,
        messages=[
            {"role": "system", "content": IMPROVE_TRANSCRIPT_PROMPT},
            {
                "role": "user",
                "content": f"Improve the readability of the following video transcript: {transcript}",
            },
        ],
    )

    improved_transcript = f"# {title}\n" + response.choices[0].message.content
    if not improved_transcript:
        raise RuntimeError("Failed to improve transcript readability")

    return clean_markdown(improved_transcript)


############################## SUMMARIZATION ##################################

SYSTEM_PROMPT = """
# IDENTITY and PURPOSE
You are a summarization system that extracts the most interesting, useful, and surprising aspects of an article or video transcript.
Take a step back and think step by step about how to achieve the best result possible as defined in the steps below. You have a lot of freedom to make this work well.

## OUTPUT SECTIONS
1. You extract a summary of the content in 30 words or less, including who is presenting and the content being discussed. This section should not have a heading; only the paragraph.
2. You extract the top 3 to 7 ideas from the input in a section called "ideas".
4. You extract the 4 to 8 most insightful and interesting recommendations that can be collected from the content into a section called "recommendations".
3. You extract the 2 to 4 most insightful and interesting quotes from the input into a section called "quotes". Use the exact quote text from the input.

## OUTPUT INSTRUCTIONS
1. You only output Markdown.
2. Do not give warnings or notes; only output the requested sections.
3. Use H3 headers for each section.
4. Do not capitalize the section headers.
5. You use bullets (`-`), not numbered lists.
6. Do not repeat ideas, or quotes.
7. Do not start items with the same opening words.
"""


def summarize_content(content: str) -> str:
    """
    Summarize the given content using OpenAI's API.
    """

    response = gemini_client.chat.completions.create(
        model=GeminiModels.GEMINI_2_0_FLASH,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Summarize the following content: {content}"},
        ],
    )

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Failed to summarize content")

    return clean_markdown(content)
