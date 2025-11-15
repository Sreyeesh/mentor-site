import os
import shutil
from pathlib import Path

from app import app
from blog import load_posts


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

    posts = load_posts()
    original_base_path = app.config.get('SITE_BASE_PATH', '')
    app.config['SITE_BASE_PATH'] = normalized_base_path

    with app.app_context():
        with app.test_client() as client:
            static_routes = [
                ('/', BUILD_DIR / 'index.html'),
                ('/mentoring/', BUILD_DIR / 'mentoring' / 'index.html'),
                (
                    '/schools-and-programs/',
                    BUILD_DIR / 'schools-and-programs' / 'index.html',
                ),
                ('/about/', BUILD_DIR / 'about' / 'index.html'),
                ('/contact/', BUILD_DIR / 'contact' / 'index.html'),
                ('/blog/', BUILD_DIR / 'blog' / 'index.html'),
            ]
            for route, destination in static_routes:
                response = client.get(route)
                if response.status_code != 200:
                    raise RuntimeError(f'Failed to render {route}.')
                write_file(destination, response.data.decode('utf-8'))
                print(f"✅ Generated {destination.relative_to(BUILD_DIR)}")

            for post in posts:
                slug_route = f"/blog/{post['slug']}/"
                response = client.get(slug_route)
                if response.status_code != 200:
                    raise RuntimeError(f'Failed to render {slug_route}.')
                output_path = BUILD_DIR / 'blog' / post['slug'] / 'index.html'
                write_file(output_path, response.data.decode('utf-8'))
                print(f"✅ Generated blog/{post['slug']}/index.html")

    write_file(BUILD_DIR / '.nojekyll', '')
    app.config['SITE_BASE_PATH'] = original_base_path

    print("\nStatic site generated in 'build' directory.")


if __name__ == '__main__':
    build_static_site()
