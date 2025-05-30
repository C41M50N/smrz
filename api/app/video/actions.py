import re
import requests
import urllib
from youtube_transcript_api import YouTubeTranscriptApi

from app.clients import GEMINI_CLIENT, GeminiModels
from app.common.actions import clean_markdown

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


def improve_transcript_readability(transcript: str, title: str) -> str:
    """
    Improve the readability of a video transcript by adding headers and subheaders.
    This function uses OpenAI's API to process the transcript.
    """

    response = GEMINI_CLIENT.chat.completions.create(
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
