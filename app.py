import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, abort, render_template, request, url_for

load_dotenv()


def _env(key: str, default: str = '') -> str:
    """Return a stripped environment value with an optional default."""

    value = os.getenv(key)
    if value is None:
        return default
    return value.strip()


BASE_PATH = _env('BASE_PATH')
if BASE_PATH and not BASE_PATH.startswith('/'):
    BASE_PATH = f"/{BASE_PATH}"

app = Flask(__name__)
from blog import find_post, load_posts  # noqa: E402


SITE_CONFIG = {
    'name': os.getenv('SITE_NAME', 'Sreyeesh Garimella'),
    'tagline': os.getenv(
        'SITE_TAGLINE',
        'Technical Art, Direction, Game Dev & DevOps Tutoring',
    ),
    'email': os.getenv('SITE_EMAIL', 'toucan.sg@gmail.com'),
    'calendly_link': os.getenv(
        'SITE_CALENDLY_LINK',
        'https://calendly.com/toucan-sg/60min',
    ),
    'site_url': os.getenv('SITE_URL', '').rstrip('/'),
    'meta_description': os.getenv(
        'SITE_META_DESCRIPTION',
        (
            'Private tutoring for technical art, direction, game development, '
            'and DevOps/programming — custom curriculum with a veteran mentor.'
        ),
    ),
    'focus_areas': os.getenv(
        'SITE_FOCUS_AREAS',
        (
            'Technical art & tools tutoring,Art direction & cinematic '
            'feedback,Game development & Unreal mentoring,DevOps/'
            'programming automation coaching'
        ),
    ).split(','),
    'asset_version': _env('ASSET_VERSION', '1'),
}


def _normalize_base_path(raw: str | None) -> str:
    if not raw:
        return ''
    raw = raw.strip()
    if not raw:
        return ''
    if not raw.startswith('/'):
        raw = f"/{raw}"
    return raw.rstrip('/')


app.config['SITE_BASE_PATH'] = _normalize_base_path(BASE_PATH)


def _resolve_base_path(override: str | None = None) -> str:
    if override is not None:
        return _normalize_base_path(override)
    return app.config.get('SITE_BASE_PATH', '')


def build_site_links(base_path_override: str | None = None) -> dict:
    base_path_value = _resolve_base_path(base_path_override)

    def prefix(path: str) -> str:
        if path == '/':
            return f"{base_path_value}/" if base_path_value else '/'
        if base_path_value:
            return f"{base_path_value}{path}"
        return path

    return {
        'home': prefix('/'),
        'mentoring': prefix('/mentoring/'),
        'schools': prefix('/schools-and-programs/'),
        'about': prefix('/about/'),
        'blog': prefix('/blog/'),
        'contact': prefix('/contact/'),
    }


def build_primary_nav(base_path_override: str | None = None) -> list:
    links = build_site_links(base_path_override)
    return [
        {'label': 'Home', 'href': links['home']},
        {'label': 'Mentoring', 'href': links['mentoring']},
        {'label': 'For Schools & Programs', 'href': links['schools']},
        {'label': 'About', 'href': links['about']},
        {'label': 'Blog', 'href': links['blog']},
        {
            'label': 'Contact',
            'href': links['contact'],
            'is_cta': True,
        },
    ]


def build_page_context(
    *,
    base_path_override: str | None = None,
    **extra: object,
) -> dict:
    base_path_value = _resolve_base_path(base_path_override)
    context = {
        'config': SITE_CONFIG,
        'current_year': datetime.now().year,
        'base_path': base_path_value,
        'site_links': build_site_links(base_path_override),
        'nav_links': build_primary_nav(base_path_override),
    }
    context.update(extra)
    return context


@app.route('/')
def home():
    return render_template('home.html', **build_page_context(page_slug='home'))


@app.route('/mentoring/')
def mentoring():
    return render_template(
        'mentoring.html',
        **build_page_context(page_slug='mentoring'),
    )


@app.route('/schools-and-programs/')
def schools_and_programs():
    return render_template(
        'schools-and-programs.html',
        **build_page_context(page_slug='schools'),
    )


@app.route('/about/')
def about():
    return render_template(
        'about.html',
        **build_page_context(page_slug='about'),
    )


@app.route('/contact/')
def contact():
    return render_template(
        'contact.html',
        **build_page_context(page_slug='contact'),
    )


@app.route('/blog/')
def blog_index():
    posts = load_posts()
    links = build_site_links()
    return render_template(
        'blog/list.html',
        **build_page_context(
            page_slug='blog',
            posts=posts,
            home_href=links['home'],
            blog_index_href=links['blog'],
        ),
    )


@app.route('/blog/<slug>/')
def blog_detail(slug: str):
    posts = load_posts()
    post = find_post(slug, posts=posts)
    if post is None:
        abort(404)

    links = build_site_links()
    detail_path = f"{links['blog']}{post['slug']}/"

    site_url = SITE_CONFIG.get('site_url', '').rstrip('/')
    if site_url:
        canonical_url = f"{site_url}{detail_path}"
    else:
        canonical_url = request.base_url

    hero_image_url = None
    if post.get('hero_image'):
        hero_asset_path = url_for(
            'static',
            filename=post['hero_image'],
        )
        if site_url:
            hero_image_url = f"{site_url}{hero_asset_path}"
        else:
            hero_image_url = url_for(
                'static',
                filename=post['hero_image'],
                _external=True,
            )

    return render_template(
        'blog/detail.html',
        **build_page_context(
            page_slug='blog',
            post=post,
            posts=posts,
            home_href=links['home'],
            blog_index_href=links['blog'],
            canonical_url=canonical_url,
            hero_image_url=hero_image_url,
        ),
    )


if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    app.run(host=host, port=port, debug=debug)
