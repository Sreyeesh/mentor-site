import os
import shutil
from pathlib import Path

from app import SITE_CONFIG, app
from content.loader import message


BUILD_DIR = Path('build')


def require_site_url_for_static_build() -> None:
    if SITE_CONFIG['site_url']:
        return
    raise SystemExit(message('freeze', 'missing_site_url'))


def write_file(destination: Path, content: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding='utf-8')


def build_static_site() -> None:
    require_site_url_for_static_build()

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
        with app.test_client() as client:
            static_routes = [
                ('/', BUILD_DIR / 'index.html'),
            ]
            for route, destination in static_routes:
                response = client.get(route, follow_redirects=True)
                if response.status_code != 200:
                    raise RuntimeError(
                        message('freeze', 'render_failed', route=route)
                    )
                write_file(destination, response.data.decode('utf-8'))
                print(
                    message(
                        'freeze',
                        'generated',
                        path=destination.relative_to(BUILD_DIR),
                    )
                )

    write_file(BUILD_DIR / '.nojekyll', '')
    app.config['SITE_BASE_PATH'] = original_base_path

    print(f"\n{message('freeze', 'complete')}")


if __name__ == '__main__':
    build_static_site()
