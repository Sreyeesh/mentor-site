from __future__ import annotations

from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename

from blog.utils import normalize_media_path, render_post
from models import db, Post, Tag

bp = Blueprint(
    'authoring',
    __name__,
    url_prefix='/authoring',
    template_folder='templates',
)


def get_media_dir() -> Path:
    return Path(current_app.config['MEDIA_UPLOAD_DIR'])


def allowed_media_extensions() -> set[str]:
    return set(current_app.config['ALLOWED_MEDIA_EXTENSIONS'])


def build_media_url(filename: str) -> str:
    prefix = str(current_app.config['MEDIA_URL_PREFIX']).rstrip('/')
    return f'{prefix}/{filename}'


def is_safe_url(target: str) -> bool:
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        test_url.scheme in {'http', 'https'}
        and ref_url.netloc == test_url.netloc
    )


def slugify(value: str) -> str:
    slug = value.strip().lower()
    slug = ''.join(
        char if char.isalnum() or char in {'-', ' '}
        else ' '
        for char in slug
    )
    slug = '-'.join(filter(None, slug.split()))
    return slug


def _post_to_dashboard_dict(post: Post) -> Dict:
    return {
        'id': post.id,
        'title': post.title,
        'slug': post.slug,
        'date': post.date.isoformat() if post.date else '',
        'updated_at': post.updated_at,
        'tags': [tag.name for tag in post.tags],
        'published': post.published,
        'featured': post.featured,
    }


def _post_to_form_dict(post: Post) -> Dict:
    return {
        'post_id': post.id,
        'title': post.title,
        'slug': post.slug,
        'date': post.date.isoformat() if post.date else '',
        'description': post.description or '',
        'excerpt': post.excerpt or '',
        'hero_image': post.hero_image or '',
        'featured': post.featured,
        'published': post.published,
        'tags': ', '.join(tag.name for tag in post.tags),
        'content': post.content or '',
        'original_slug': post.slug,
    }


def _resolve_or_create_tags(tag_names: List[str]) -> List[Tag]:
    result = []
    for name in tag_names:
        tag = Tag.query.filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            db.session.add(tag)
        result.append(tag)
    return result


@bp.route('/')
def dashboard() -> str:
    posts = Post.query.order_by(Post.date.desc()).all()
    return render_template(
        'authoring/index.html',
        posts=[_post_to_dashboard_dict(p) for p in posts],
    )


@bp.route('/posts/new', methods=['GET', 'POST'])
@bp.route('/posts/<slug>/edit', methods=['GET', 'POST'])
def edit_post(slug: Optional[str] = None) -> str:
    post: Optional[Post] = Post.query.filter_by(slug=slug).first() if slug else None

    if request.method == 'POST':
        form = request.form
        title = form.get('title', '').strip()
        slug_value = form.get('slug', '') or slugify(title)
        slug_value = slugify(slug_value)
        description = form.get('description', '').strip()
        excerpt = form.get('excerpt', '').strip()
        hero_image_input = form.get('hero_image', '').strip()
        if hero_image_input.lower() in {'none', 'null'}:
            hero_image_input = ''
        hero_image, _ = normalize_media_path(hero_image_input)
        content = form.get('content', '').strip()
        featured = form.get('featured') == 'on'
        published = form.get('published') == 'on'
        raw_date = form.get('date', '').strip()
        try:
            date_value = date.fromisoformat(raw_date) if raw_date else date.today()
        except ValueError:
            date_value = date.today()
        raw_tags = form.get('tags', '')
        tag_names = [t.strip() for t in raw_tags.split(',') if t.strip()]
        post_id = form.get('post_id', '').strip()
        original_slug = form.get('original_slug') or slug

        errors: List[str] = []
        if not title:
            errors.append('Title is required.')
        if not slug_value:
            errors.append('Slug is required.')
        if not content:
            errors.append('Content is required.')

        existing = Post.query.filter_by(slug=slug_value).first()
        if existing and existing.id != (post.id if post else None):
            errors.append(f'A post with slug "{slug_value}" already exists.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template(
                'authoring/edit.html',
                is_new=post is None,
                post_data={
                    'post_id': post_id,
                    'title': title,
                    'slug': slug_value,
                    'date': raw_date,
                    'description': description,
                    'excerpt': excerpt,
                    'hero_image': hero_image_input,
                    'featured': featured,
                    'published': published,
                    'tags': form.get('tags', ''),
                    'content': content,
                    'original_slug': original_slug,
                },
                media_url_prefix=current_app.config['MEDIA_URL_PREFIX'],
            )

        if post is None:
            from uuid import uuid4
            post = Post(id=post_id or str(uuid4()))
            db.session.add(post)

        post.title = title
        post.slug = slug_value
        post.date = date_value
        post.description = description
        post.excerpt = excerpt
        post.hero_image = hero_image or None
        post.content = content
        post.featured = featured
        post.published = published
        post.updated_at = datetime.utcnow()
        post.tags = _resolve_or_create_tags(tag_names)

        db.session.commit()
        flash(f'Post "{title}" saved successfully.', 'success')
        return redirect(url_for('authoring.dashboard'))

    if post:
        post_data = _post_to_form_dict(post)
    else:
        post_data = {
            'post_id': '',
            'title': '',
            'slug': '',
            'description': '',
            'excerpt': '',
            'hero_image': '',
            'featured': False,
            'published': False,
            'date': date.today().isoformat(),
            'tags': '',
            'content': '',
            'original_slug': '',
        }

    return render_template(
        'authoring/edit.html',
        is_new=post is None,
        post_data=post_data,
        media_url_prefix=current_app.config['MEDIA_URL_PREFIX'],
    )


@bp.route('/uploads', methods=['POST'])
def upload_media() -> str:
    next_url = request.form.get('next') or url_for('authoring.dashboard')
    if not is_safe_url(next_url):
        next_url = url_for('authoring.dashboard')

    upload = request.files.get('media_file')
    if upload is None or not upload.filename:
        flash('Please choose a file to upload.', 'error')
        return redirect(next_url)

    filename = secure_filename(upload.filename)
    if not filename:
        flash('The selected filename is not valid.', 'error')
        return redirect(next_url)

    extension = Path(filename).suffix.lower().lstrip('.')
    if extension not in allowed_media_extensions():
        allowed_list = ', '.join(sorted(allowed_media_extensions()))
        flash(
            f'Unsupported file type "{extension}". Allowed: {allowed_list}.',
            'error',
        )
        return redirect(next_url)

    media_dir = get_media_dir()
    media_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    candidate = filename
    counter = 1
    while (media_dir / candidate).exists():
        candidate = f'{stem}-{counter}{suffix}'
        counter += 1

    (media_dir / candidate).parent.mkdir(parents=True, exist_ok=True)
    upload.save(media_dir / candidate)

    media_url = build_media_url(candidate)
    flash(
        f'Uploaded successfully! Use "{media_url}" in your post.',
        'success',
    )
    return redirect(next_url)


@bp.route('/posts/<slug>/preview')
def preview_post(slug: str) -> str:
    post_obj = Post.query.filter_by(slug=slug).first()
    if not post_obj:
        flash(f'Unable to find post "{slug}".', 'error')
        return redirect(url_for('authoring.dashboard'))

    post_data = render_post(post_obj)
    hero_image_url = _resolve_hero_image_url(post_obj.hero_image)

    return render_template(
        'authoring/preview.html',
        post=post_data,
        hero_image_url=hero_image_url,
        site_name=current_app.config.get('SITE_NAME', 'Toucan.ee'),
    )


@bp.route('/posts/<slug>/delete', methods=['POST'])
def delete_post(slug: str) -> str:
    post_obj = Post.query.filter_by(slug=slug).first()
    if post_obj:
        db.session.delete(post_obj)
        db.session.commit()
        flash(f'Post "{slug}" deleted.', 'success')
    else:
        flash(f'Post "{slug}" not found.', 'error')
    return redirect(url_for('authoring.dashboard'))


def _resolve_hero_image_url(hero_image: str | None) -> str | None:
    normalized, is_external = normalize_media_path(hero_image)
    if not normalized:
        return None
    if is_external:
        return normalized
    return url_for('static', filename=normalized)
