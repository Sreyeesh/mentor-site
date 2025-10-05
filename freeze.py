import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import frontmatter
import markdown
from flask import render_template

from app import SITE_CONFIG, app


BUILD_DIR = Path('build')
CONTENT_DIR = Path('content/posts')


def slug_from_filename(path: Path) -> str:
    """Fallback slug generator based on the filename."""
    return path.stem.lower().replace(' ', '-').replace('_', '-')


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

    html = markdown.markdown(
        post_data.content,
        extensions=['fenced_code', 'tables', 'sane_lists'],
    )

    words = post_data.content.split()
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


def load_posts() -> List[Dict[str, Any]]:
    """Load and sort all markdown posts."""
    posts: List[Dict[str, Any]] = []
    if not CONTENT_DIR.exists():
        return posts

    for path in sorted(CONTENT_DIR.glob('*.md')):
        try:
            posts.append(parse_post(path))
        except Exception as exc:  # noqa: BLE001 - surface file errors
            print(f"❌ Failed to parse {path}: {exc}")

    posts.sort(
        key=lambda item: (
            item.get('featured', False),
            item.get('date') or datetime.min,
        ),
        reverse=True,
    )
    return posts


def write_file(destination: Path, content: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding='utf-8')


def build_static_site() -> None:
    base_path = os.getenv('GITHUB_PAGES_BASE_PATH', '')

    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    if Path('static').exists():
        shutil.copytree('static', BUILD_DIR / 'static')

    posts = load_posts()

    home_href = f"{base_path}/" if base_path else '/'
    blog_index_href = (
        f"{base_path}/blog/index.html" if base_path else '/blog/index.html'
    )

    with app.app_context():
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code != 200:
                raise RuntimeError('Failed to render index route.')
            write_file(BUILD_DIR / 'index.html', response.data.decode('utf-8'))
            print('✅ Generated index.html')

        with app.test_request_context('/'):
            blog_index = render_template(
                'blog/list.html',
                posts=posts,
                config=SITE_CONFIG,
                current_year=datetime.now().year,
                base_path=base_path,
                home_href=home_href,
                blog_index_href=blog_index_href,
            )
        write_file(BUILD_DIR / 'blog/index.html', blog_index)
        print('✅ Generated blog/index.html')

        for post in posts:
            if base_path:
                detail_href = f"{base_path}/blog/{post['slug']}/"
            else:
                detail_href = f"/blog/{post['slug']}/"

            with app.test_request_context(f"/blog/{post['slug']}/"):
                detail_html = render_template(
                    'blog/detail.html',
                    post=post,
                    posts=posts,
                    config=SITE_CONFIG,
                    current_year=datetime.now().year,
                    base_path=base_path,
                    home_href=home_href,
                    blog_index_href=blog_index_href,
                    canonical_url=detail_href,
                )
            output_path = BUILD_DIR / 'blog' / post['slug'] / 'index.html'
            write_file(output_path, detail_html)
            print(f"✅ Generated blog/{post['slug']}/index.html")

    write_file(BUILD_DIR / '.nojekyll', '')

    print("\nStatic site generated in 'build' directory.")


if __name__ == '__main__':
    build_static_site()
