from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import frontmatter
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from urllib.parse import urljoin, urlparse

from blog.utils import parse_post

bp = Blueprint(
    'authoring',
    __name__,
    url_prefix='/authoring',
    template_folder='templates',
)


def get_content_dir() -> Path:
    return Path(current_app.config['CONTENT_DIR'])


def is_safe_url(target: str) -> bool:
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        test_url.scheme in {'http', 'https'}
        and ref_url.netloc == test_url.netloc
    )


def load_all_posts() -> List[Dict[str, object]]:
    posts: List[Dict[str, str]] = []
    for path in sorted(get_content_dir().glob('*.md')):
        try:
            data = frontmatter.load(path)
            metadata = data.metadata.copy()
            metadata['slug'] = metadata.get('slug') or path.stem
            metadata['title'] = metadata.get('title', path.stem)
            date_value = metadata.get('date')
            if isinstance(date_value, datetime):
                metadata['date'] = date_value.date().isoformat()
            elif date_value is None:
                metadata['date'] = ''
            else:
                metadata['date'] = str(date_value)
            metadata['path'] = path
            metadata['updated_at'] = datetime.fromtimestamp(
                path.stat().st_mtime
            )
            posts.append(metadata)
        except Exception as exc:  # noqa: BLE001
            flash(f'Failed to read {path.name}: {exc}', 'error')
    posts.sort(
        key=lambda item: item.get('date') or datetime.min.isoformat(),
        reverse=True,
    )
    return posts


def slugify(value: str) -> str:
    slug = value.strip().lower()
    slug = ''.join(
        char if char.isalnum() or char in {'-', ' '}
        else ' '
        for char in slug
    )
    slug = '-'.join(filter(None, slug.split()))
    return slug


def load_post(slug: str) -> Optional[frontmatter.Post]:
    path = get_content_dir() / f'{slug}.md'
    if not path.exists():
        return None
    return frontmatter.load(path)


def save_post(
    *,
    slug: str,
    metadata: Dict[str, object],
    content: str,
    original_slug: Optional[str] = None,
) -> str:
    content_dir = get_content_dir()
    target_path = content_dir / f'{slug}.md'

    if original_slug and original_slug != slug:
        old_path = content_dir / f'{original_slug}.md'
        if old_path.exists():
            old_path.unlink()

    post = frontmatter.Post(content, **metadata)
    target_path.write_text(frontmatter.dumps(post), encoding='utf-8')
    return target_path.name


@bp.route('/')
def dashboard() -> str:
    posts = load_all_posts()
    return render_template('authoring/index.html', posts=posts)


@bp.route('/posts/new', methods=['GET', 'POST'])
@bp.route('/posts/<slug>/edit', methods=['GET', 'POST'])
def edit_post(slug: Optional[str] = None) -> str:
    post = load_post(slug) if slug else None

    if request.method == 'POST':
        form = request.form
        title = form.get('title', '').strip()
        slug_value = form.get('slug', '') or slugify(title)
        slug_value = slugify(slug_value)
        description = form.get('description', '').strip()
        excerpt = form.get('excerpt', '').strip()
        content = form.get('content', '').strip()
        featured = form.get('featured') == 'on'
        raw_date = form.get('date', '').strip()
        date_value = raw_date or datetime.now().date().isoformat()

        errors: List[str] = []
        if not title:
            errors.append('Title is required.')
        if not slug_value:
            errors.append('Slug is required.')
        if not content:
            errors.append('Content is required.')

        original_slug = form.get('original_slug') or slug
        content_dir = get_content_dir()
        target_path = content_dir / f'{slug_value}.md'
        if (
            not post
            or (original_slug and slug_value != original_slug)
        ) and target_path.exists():
            errors.append(f'A post with slug "{slug_value}" already exists.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template(
                'authoring/edit.html',
                is_new=post is None,
                post_data=form,
                post=post,
            )

        metadata = {
            'title': title,
            'slug': slug_value,
            'date': date_value,
            'description': description,
            'excerpt': excerpt,
            'hero_image': post.metadata.get('hero_image') if post else None,
            'featured': featured,
        }

        save_post(
            slug=slug_value,
            metadata=metadata,
            content=content,
            original_slug=original_slug,
        )
        flash(f'Post "{title}" saved successfully.', 'success')
        return redirect(url_for('authoring.dashboard'))

    if post:
        metadata = post.metadata
        post_data = {
            'title': metadata.get('title', ''),
            'slug': metadata.get('slug', slug),
            'description': metadata.get('description', ''),
            'excerpt': metadata.get('excerpt', ''),
            'featured': metadata.get('featured', False),
            'date': metadata.get('date', ''),
            'content': post.content,
            'original_slug': slug,
        }
    else:
        post_data = {
            'title': '',
            'slug': '',
            'description': '',
            'excerpt': '',
            'featured': False,
            'date': datetime.now().date().isoformat(),
            'content': '',
            'original_slug': '',
        }

    return render_template(
        'authoring/edit.html',
        is_new=post is None,
        post=post,
        post_data=post_data,
    )


@bp.route('/posts/<slug>/preview')
def preview_post(slug: str) -> str:
    path = get_content_dir() / f'{slug}.md'
    if not path.exists():
        flash(f'Unable to find post "{slug}".', 'error')
        return redirect(url_for('authoring.dashboard'))

    try:
        post_data = parse_post(path)
    except Exception as exc:  # noqa: BLE001
        flash(f'Unable to render preview: {exc}', 'error')
        return redirect(url_for('authoring.dashboard'))

    return render_template(
        'authoring/preview.html',
        post=post_data,
        site_name=current_app.config.get('SITE_NAME', 'Mentor Site'),
    )


@bp.route('/posts/<slug>/delete', methods=['POST'])
def delete_post(slug: str) -> str:
    path = get_content_dir() / f'{slug}.md'
    if path.exists():
        path.unlink()
        flash(f'Post "{slug}" deleted.', 'success')
    else:
        flash(f'Post "{slug}" not found.', 'error')
    return redirect(url_for('authoring.dashboard'))
