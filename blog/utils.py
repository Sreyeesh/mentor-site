"""Utilities for loading and formatting blog content."""
from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import frontmatter
import markdown


_DEFAULT_CONTENT_DIR = Path('content/posts')


def _env_content_dir() -> Optional[str]:
    """Return an environment-provided content directory if available."""
    for env_var in (
        'BLOG_CONTENT_DIR',
        'AUTHORING_CONTENT_DIR',
        'CONTENT_DIR',
    ):
        value = os.getenv(env_var)
        if value:
            return value
    return None


def get_content_dir(override: Optional[Path | str] = None) -> Path:
    """Resolve the content directory with optional overrides.

    ``override`` takes priority, followed by environment variables that keep
    the blog in sync with the authoring tool. The final fallback is the
    default ``content/posts`` path that ships with the project.
    """

    if override:
        return Path(override).expanduser()

    env_value = _env_content_dir()
    if env_value:
        return Path(env_value).expanduser()

    return _DEFAULT_CONTENT_DIR


# Backwards compatibility for modules that import ``CONTENT_DIR`` directly.
CONTENT_DIR = get_content_dir()


def slug_from_filename(path: Path) -> str:
    """Fallback slug generator based on the filename."""
    return path.stem.lower().replace(' ', '-').replace('_', '-')


METADATA_LINE_RE = re.compile(r'^[A-Za-z0-9_]+:\s*.+$')


def strip_leading_metadata_lines(content: str) -> str:
    """Remove accidental metadata-style lines from the top of the body."""
    lines = content.splitlines()
    cleaned: List[str] = []
    skipping = True

    for line in lines:
        if skipping and not line.strip():
            continue
        if skipping and METADATA_LINE_RE.match(line.strip()):
            continue
        skipping = False
        cleaned.append(line)

    return '\n'.join(cleaned).lstrip()


def parse_post(path: Path) -> Dict[str, Any]:
    """Parse a Markdown file with front matter into a dictionary."""
    post_data = frontmatter.load(path)
    metadata = post_data.metadata

    slug = metadata.get('slug') or slug_from_filename(path)
    raw_date = metadata.get('date')
    try:
        published_at = (
            datetime.fromisoformat(str(raw_date)) if raw_date else None
        )
    except ValueError:
        published_at = None

    body = strip_leading_metadata_lines(post_data.content)

    html = markdown.markdown(
        body,
        extensions=['fenced_code', 'tables', 'sane_lists'],
    )

    words = body.split()
    word_count = len(words)
    reading_time = max(1, round(word_count / 200))
    excerpt = metadata.get('excerpt') or ' '.join(words[:50])
    if metadata.get('excerpt') is None and word_count > 50:
        excerpt += '…'

    return {
        'title': metadata.get('title', 'Untitled Post'),
        'slug': slug,
        'date': published_at,
        'date_display': (
            published_at.strftime('%B %d, %Y') if published_at else ''
        ),
        'description': metadata.get('description', ''),
        'excerpt': excerpt,
        'hero_image': metadata.get('hero_image'),
        'tags': metadata.get('tags', []),
        'content': html,
        'word_count': word_count,
        'reading_time': reading_time,
        'featured': metadata.get('featured', False),
        'source_path': path,
    }


def load_posts(
    content_dir: Optional[Path | str] = None,
) -> List[Dict[str, Any]]:
    """Load and sort all markdown posts."""
    directory = get_content_dir(content_dir)

    posts: List[Dict[str, Any]] = []
    if not directory.exists():
        return posts

    for path in sorted(directory.glob('*.md')):
        try:
            posts.append(parse_post(path))
        except Exception as exc:  # noqa: BLE001 - surface file errors
            print(f"❌ Failed to parse {path}: {exc}")

    # Sort by date (newest first), regardless of featured status
    posts.sort(
        key=lambda item: item.get('date') or datetime.min,
        reverse=True,
    )
    return posts


def find_post(
    slug: str,
    *,
    posts: Optional[Iterable[Dict[str, Any]]] = None,
) -> Optional[Dict[str, Any]]:
    """Return a post matching ``slug`` from ``posts`` or from disk."""
    candidates = list(posts) if posts is not None else load_posts()
    for post in candidates:
        if post.get('slug') == slug:
            return post
    return None


def normalize_media_path(value: Optional[str]) -> tuple[Optional[str], bool]:
    """Normalize a media reference to a static-relative path or return external URLs."""
    if not value:
        return None, False
    normalized = value.strip()
    if not normalized:
        return None, False
    if normalized.startswith(('http://', 'https://')):
        return normalized, True
    normalized = normalized.lstrip('/')
    if normalized.startswith('static/'):
        normalized = normalized[len('static/') :]
    return normalized or None, False


__all__ = [
    'CONTENT_DIR',
    'find_post',
    'get_content_dir',
    'load_posts',
    'normalize_media_path',
    'parse_post',
    'slug_from_filename',
    'strip_leading_metadata_lines',
]
