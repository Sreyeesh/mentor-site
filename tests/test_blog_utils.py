"""Tests for blog utility functions."""
from __future__ import annotations

from blog.utils import (
    auto_excerpt,
    normalize_media_path,
    reading_time,
    render_body,
    strip_leading_metadata_lines,
)


def test_render_body_converts_markdown():
    html = render_body('# Hello\n\nWorld')
    assert '<h1>' in html
    assert 'Hello' in html


def test_render_body_empty():
    assert render_body('') == ''
    assert render_body(None) == ''


def test_reading_time_minimum_one():
    assert reading_time('') == 1
    assert reading_time('word ' * 100) == 1


def test_reading_time_calculation():
    # 400 words → 2 minutes
    text = 'word ' * 400
    assert reading_time(text) == 2


def test_auto_excerpt_short_text():
    text = 'Short text.'
    assert auto_excerpt(text) == text


def test_auto_excerpt_truncates():
    text = ' '.join([f'word{i}' for i in range(100)])
    result = auto_excerpt(text, words=50)
    assert result.endswith('\u2026')
    assert len(result.split()) == 50  # ellipsis is appended directly to last word


def test_normalize_media_path_external():
    path, is_external = normalize_media_path('https://example.com/img.jpg')
    assert is_external is True
    assert path == 'https://example.com/img.jpg'


def test_normalize_media_path_static():
    path, is_external = normalize_media_path('static/images/hero.jpg')
    assert is_external is False
    assert path == 'images/hero.jpg'


def test_normalize_media_path_none():
    path, is_external = normalize_media_path(None)
    assert path is None
    assert is_external is False


def test_strip_leading_metadata_removes_metadata_block():
    content = 'title: My Post\ndate: 2024-01-01\n\nBody text here.'
    result = strip_leading_metadata_lines(content)
    assert 'title:' not in result
    assert 'Body text here.' in result


def test_strip_leading_metadata_leaves_normal_text():
    content = 'Just a normal paragraph.\n\nAnother one.'
    result = strip_leading_metadata_lines(content)
    assert result == content
