from app.lib.article_content import ARTICLE_TO_MARKDOWN_PROMPT_2, article_to_markdown
from app.lib.llm_client import LLMClient, Models


MODELS: list[Models] = [
    Models.GEMINI_2_5_FLASH_LITE_PREVIEW,
    Models.GEMINI_2_5_PRO,
]


def test_level_1():
    url = "https://www.unkey.com/blog/uuid-ux"
    markdown = article_to_markdown(
        llm_client=LLMClient(
            model=Models.GEMINI_2_5_PRO, system_prompt=ARTICLE_TO_MARKDOWN_PROMPT_2
        ),
        url=url,
    )


def test_level_2():
    url = "https://grantslatton.com/how-to-software"
    markdown = article_to_markdown(
        llm_client=LLMClient(
            model=Models.GEMINI_2_5_PRO, system_prompt=ARTICLE_TO_MARKDOWN_PROMPT_2
        ),
        url=url,
    )


def test_level_3():
    url = "https://gerlacdt.github.io/blog/posts/cccp/"
    markdown = article_to_markdown(
        llm_client=LLMClient(
            model=Models.GEMINI_2_5_PRO, system_prompt=ARTICLE_TO_MARKDOWN_PROMPT_2
        ),
        url=url,
    )


def test_level_4():
    url = "https://martinfowler.com/articles/is-quality-worth-cost.html"
    markdown = article_to_markdown(
        llm_client=LLMClient(
            model=Models.GEMINI_2_5_PRO, system_prompt=ARTICLE_TO_MARKDOWN_PROMPT_2
        ),
        url=url,
    )


def test_level_5():
    url = "https://substack.com/inbox/post/161631616"
    markdown = article_to_markdown(
        llm_client=LLMClient(
            model=Models.GEMINI_2_5_PRO, system_prompt=ARTICLE_TO_MARKDOWN_PROMPT_2
        ),
        url=url,
    )
