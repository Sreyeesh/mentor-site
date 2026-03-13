"""Utilities for loading and formatting blog content."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

import markdown


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


def _render_markdown(content: str) -> str:
    """Render Markdown string to HTML."""
    return markdown.markdown(
        content,
        extensions=['fenced_code', 'tables', 'sane_lists'],
    )


def render_post(post_obj: Any) -> Dict[str, Any]:
    """Convert a Post model instance to the dict format templates expect."""
    body = post_obj.content or ''
    html = _render_markdown(body)

    words = body.split()
    word_count = len(words)
    reading_time = max(1, round(word_count / 200))

    stored_excerpt = post_obj.excerpt
    if stored_excerpt:
        excerpt = stored_excerpt
    else:
        excerpt = ' '.join(words[:50])
        if word_count > 50:
            excerpt += '…'

    date_obj = post_obj.date
    date_display = date_obj.strftime('%B %d, %Y') if date_obj else ''

    return {
        'id': post_obj.id,
        'title': post_obj.title,
        'slug': post_obj.slug,
        'date': date_obj,
        'date_display': date_display,
        'description': post_obj.description or '',
        'excerpt': excerpt,
        'hero_image': post_obj.hero_image,
        'tags': [tag.name for tag in post_obj.tags],
        'content': html,
        'word_count': word_count,
        'reading_time': reading_time,
        'featured': post_obj.featured,
        'published': post_obj.published,
    }


def load_posts(
    content_dir: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """Load all published posts from DB, sorted newest first."""
    from models import Post
    posts = (
        Post.query
        .filter_by(published=True)
        .order_by(Post.date.desc())
        .all()
    )
    return [render_post(p) for p in posts]


def find_post(
    slug: str,
    *,
    posts: Optional[Iterable[Dict[str, Any]]] = None,
) -> Optional[Dict[str, Any]]:
    """Return a post matching ``slug`` from ``posts`` or from DB."""
    if posts is not None:
        for post in posts:
            if post.get('slug') == slug:
                return post
    from models import Post
    post_obj = Post.query.filter_by(slug=slug).first()
    return render_post(post_obj) if post_obj else None


__all__ = [
    'find_post',
    'load_posts',
    'normalize_media_path',
    'render_post',
]
