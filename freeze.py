import os
import shutil
from datetime import datetime
from pathlib import Path

from flask import render_template, request, url_for

from app import SITE_CONFIG, app
from blog import find_post, load_posts


BUILD_DIR = Path('build')


def write_file(destination: Path, content: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding='utf-8')


def build_static_site() -> None:
    base_path = os.getenv('GITHUB_PAGES_BASE_PATH', '')
    site_url = os.getenv('SITE_URL', '').rstrip('/')

    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    if Path('static').exists():
        shutil.copytree('static', BUILD_DIR / 'static')

    posts = load_posts()

    home_href = f"{base_path}/" if base_path else '/'
    blog_index_href = f"{base_path}/blog/" if base_path else '/blog/'

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
            detail_path = f"{base_path}/blog/{post['slug']}/" if base_path else f"/blog/{post['slug']}/"
            base_url = site_url or 'http://localhost:5000'

            with app.test_request_context(detail_path, base_url=base_url):
                canonical_url = request.base_url
                hero_image_url = None
                if post.get('hero_image'):
                    hero_image_url = url_for('static', filename=post['hero_image'], _external=True)
                detail_html = render_template(
                    'blog/detail.html',
                    post=find_post(post['slug'], posts=posts),
                    posts=posts,
                    config=SITE_CONFIG,
                    current_year=datetime.now().year,
                    base_path=base_path,
                    home_href=home_href,
                    blog_index_href=blog_index_href,
                    canonical_url=canonical_url,
                    hero_image_url=hero_image_url,
                )
            output_path = BUILD_DIR / 'blog' / post['slug'] / 'index.html'
            write_file(output_path, detail_html)
            print(f"✅ Generated blog/{post['slug']}/index.html")

    write_file(BUILD_DIR / '.nojekyll', '')

    print("\nStatic site generated in 'build' directory.")


if __name__ == '__main__':
    build_static_site()
