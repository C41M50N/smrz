from api.utils import get_clean_html


MODELS = [
    "google/gemini-2.0-flash",
]


def test_level_1():
    html = get_clean_html("https://www.unkey.com/blog/uuid-ux")


def test_level_2():
    html = get_clean_html("https://gerlacdt.github.io/blog/posts/cccp/")


def test_level_3():
    html = get_clean_html(
        "https://martinfowler.com/articles/is-quality-worth-cost.html"
    )


def test_level_4():
    html = get_clean_html("https://substack.com/inbox/post/161631616")
