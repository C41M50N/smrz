import re

import requests
from lxml_html_clean import Cleaner

from app.clients import GEMINI_CLIENT, GeminiModels


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


def summarize_content(content: str) -> str:
    """
    Summarize the given content using OpenAI's API.
    """

    response = GEMINI_CLIENT.chat.completions.create(
        model=GeminiModels.GEMINI_2_0_FLASH,
        messages=[
            {"role": "system", "content": SUMMARIZE_PROMPT},
            {"role": "user", "content": f"Summarize the following content: {content}"},
        ],
    )

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Failed to summarize content")

    return clean_markdown(content)


SUMMARIZE_PROMPT = """
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
