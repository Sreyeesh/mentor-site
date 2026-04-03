import os
import shutil
from math import ceil
from pathlib import Path

from app import app, POSTS_PER_PAGE
from models import Post

BUILD_DIR = Path('build')


def write_file(destination: Path, content: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding='utf-8')


def build_static_site() -> None:
    base_path = os.getenv('GITHUB_PAGES_BASE_PATH', '')
    normalized_base_path = base_path.strip()
    if normalized_base_path and not normalized_base_path.startswith('/'):
        normalized_base_path = f"/{normalized_base_path}"
    normalized_base_path = normalized_base_path.rstrip('/')

    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    if Path('static').exists():
        shutil.copytree('static', BUILD_DIR / 'static')

    original_base_path = app.config.get('SITE_BASE_PATH', '')
    app.config['SITE_BASE_PATH'] = normalized_base_path

    with app.app_context():
        posts = Post.query.filter_by(draft=False).order_by(Post.date.desc()).all()
        total_pages = ceil(len(posts) / POSTS_PER_PAGE) if posts else 1
        all_tags = set()
        for post in posts:
            all_tags.update(post.tag_list())

        with app.test_client() as client:
            # Home redirect
            response = client.get('/', follow_redirects=False)
            write_file(BUILD_DIR / 'index.html', response.data.decode('utf-8'))
            print("✅ Generated index.html (redirect)")

            # Blog index (page 1)
            response = client.get('/blog/')
            if response.status_code != 200:
                raise RuntimeError('Failed to render /blog/.')
            write_file(BUILD_DIR / 'blog' / 'index.html', response.data.decode('utf-8'))
            print("✅ Generated blog/index.html")

            # Paginated blog pages
            for page_num in range(2, total_pages + 1):
                route = f"/blog/page/{page_num}/"
                response = client.get(route)
                if response.status_code != 200:
                    raise RuntimeError(f'Failed to render {route}.')
                write_file(
                    BUILD_DIR / 'blog' / 'page' / str(page_num) / 'index.html',
                    response.data.decode('utf-8'),
                )
                print(f"✅ Generated blog/page/{page_num}/index.html")

            # Individual post pages
            for post in posts:
                route = f"/blog/{post.slug}/"
                response = client.get(route)
                if response.status_code != 200:
                    raise RuntimeError(f'Failed to render {route}.')
                write_file(
                    BUILD_DIR / 'blog' / post.slug / 'index.html',
                    response.data.decode('utf-8'),
                )
                print(f"✅ Generated blog/{post.slug}/index.html")

            # Tag pages
            for tag in sorted(all_tags):
                route = f"/blog/tag/{tag}/"
                response = client.get(route)
                if response.status_code != 200:
                    raise RuntimeError(f'Failed to render {route}.')
                write_file(
                    BUILD_DIR / 'blog' / 'tag' / tag / 'index.html',
                    response.data.decode('utf-8'),
                )
                print(f"✅ Generated blog/tag/{tag}/index.html")

            # RSS feed
            response = client.get('/feed.xml')
            if response.status_code != 200:
                raise RuntimeError('Failed to render /feed.xml.')
            write_file(BUILD_DIR / 'feed.xml', response.data.decode('utf-8'))
            print("✅ Generated feed.xml")

            # Sitemap and robots
            for route, dest in [
                ('/sitemap.xml', BUILD_DIR / 'sitemap.xml'),
                ('/robots.txt', BUILD_DIR / 'robots.txt'),
            ]:
                response = client.get(route)
                if response.status_code != 200:
                    raise RuntimeError(f'Failed to render {route}.')
                write_file(dest, response.data.decode('utf-8'))
                print(f"✅ Generated {dest.name}")

    write_file(BUILD_DIR / '.nojekyll', '')
    app.config['SITE_BASE_PATH'] = original_base_path

    print("\nStatic site generated in 'build' directory.")


if __name__ == '__main__':
    build_static_site()
