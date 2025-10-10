from __future__ import annotations

from pathlib import Path

import pytest

from blog import get_content_dir, load_posts


@pytest.fixture(autouse=True)
def clear_content_env(monkeypatch):
    """Clear content-dir environment variables so tests stay isolated."""

    for key in (
        'BLOG_CONTENT_DIR',
        'AUTHORING_CONTENT_DIR',
        'CONTENT_DIR',
    ):
        monkeypatch.delenv(key, raising=False)


def test_get_content_dir_prefers_override(tmp_path: Path):
    override = tmp_path / 'custom'
    result = get_content_dir(override)
    assert result == override


def test_get_content_dir_reads_authoring_env(monkeypatch, tmp_path: Path):
    monkeypatch.setenv('AUTHORING_CONTENT_DIR', str(tmp_path / 'posts'))
    result = get_content_dir()
    assert result == Path(str(tmp_path / 'posts'))


def test_load_posts_uses_environment_directory(monkeypatch, tmp_path: Path):
    posts_dir = tmp_path / 'env-posts'
    posts_dir.mkdir()
    post_path = posts_dir / 'sample.md'
    post_path.write_text(
        (
            '---\n'
            'title: Sample\n'
            'slug: sample\n'
            'date: 2024-05-01\n'
            '---\n\n'
            'Hello world'
        ),
        encoding='utf-8',
    )

    monkeypatch.setenv('AUTHORING_CONTENT_DIR', str(posts_dir))

    posts = load_posts()

    assert len(posts) == 1
    assert posts[0]['slug'] == 'sample'
