from app.article.actions import article_to_markdown, get_clean_html


MODELS = [
    "google/gemini-2.0-flash",
]


def test_level_1():
    url = "https://www.unkey.com/blog/uuid-ux"
    html = get_clean_html(url)
    markdown = article_to_markdown(url, html)


def test_level_2():
    url = "https://grantslatton.com/how-to-software"
    html = get_clean_html(url)
    markdown = article_to_markdown(url, html)


def test_level_3():
    url = "https://gerlacdt.github.io/blog/posts/cccp/"
    html = get_clean_html(url)
    markdown = article_to_markdown(url, html)


def test_level_4():
    url = "https://martinfowler.com/articles/is-quality-worth-cost.html"
    html = get_clean_html(url)
    markdown = article_to_markdown(url, html)


def test_level_5():
    url = "https://substack.com/inbox/post/161631616"
    html = get_clean_html(url)
    markdown = article_to_markdown(url, html)
