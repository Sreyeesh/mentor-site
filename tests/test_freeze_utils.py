import pytest

from blog import strip_leading_metadata_lines
from freeze import SITE_CONFIG, require_site_url_for_static_build


def test_strip_leading_metadata_removes_metadata_block():
    content = (
        "title: Example Post\n"
        "slug: example-post\n"
        "tags: foo, bar\n\n"
        "# Heading\n\nBody text."
    )
    cleaned = strip_leading_metadata_lines(content)
    assert cleaned.startswith('# Heading')
    assert 'example-post' not in cleaned


def test_strip_leading_metadata_leaves_normal_text():
    content = "First line\nSecond line"
    cleaned = strip_leading_metadata_lines(content)
    assert cleaned == content


def test_static_build_requires_site_url(monkeypatch):
    monkeypatch.setitem(SITE_CONFIG, 'site_url', '')

    with pytest.raises(SystemExit, match='SITE_URL is not set'):
        require_site_url_for_static_build()


def test_static_build_allows_configured_site_url(monkeypatch):
    monkeypatch.setitem(SITE_CONFIG, 'site_url', 'https://example.com')

    require_site_url_for_static_build()
