"""Utilities for rendering blog content."""
from __future__ import annotations

import re
from typing import List, Optional

import markdown


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


def render_body(markdown_text: str) -> str:
    """Convert a Markdown string to safe HTML."""
    return markdown.markdown(
        markdown_text or '',
        extensions=['fenced_code', 'tables', 'sane_lists'],
    )


def reading_time(text: str) -> int:
    """Return estimated reading time in minutes (minimum 1)."""
    word_count = len((text or '').split())
    return max(1, round(word_count / 200))


def auto_excerpt(text: str, words: int = 50) -> str:
    """Return first ``words`` words of ``text`` with a trailing ellipsis."""
    parts = (text or '').split()
    if len(parts) <= words:
        return text or ''
    return ' '.join(parts[:words]) + '\u2026'


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
        normalized = normalized[len('static/'):]
    return normalized or None, False


__all__ = [
    'auto_excerpt',
    'normalize_media_path',
    'render_body',
    'reading_time',
    'strip_leading_metadata_lines',
]
