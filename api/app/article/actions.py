from newspaper import Article

from app.clients import OPENROUTER_CLIENT, OpenRouterModels
from app.common.actions import clean_markdown


def get_article_title(url: str) -> str:
    """
    Extract the title of an article from its URL using Newspaper3k.
    """
    article = Article(url)
    article.download()
    article.parse()
    return article.title


###############################################################################
##################################### AI ######################################
###############################################################################


def article_to_markdown(url: str, html: str) -> str:
    """
    Uses an LLM to convert an article HTML to Markdown.
    """

    response = OPENROUTER_CLIENT.chat.completions.create(
        model=f"{OpenRouterModels.LLAMA_4_MAVERICK}:nitro",
        messages=[
            {"role": "system", "content": ARTICLE_TO_MARKDOWN_PROMPT},
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


ARTICLE_TO_MARKDOWN_PROMPT = """
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
