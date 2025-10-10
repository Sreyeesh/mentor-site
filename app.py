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
        'Mentoring & Coaching in Animation and Video Game Development',
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
            'One-on-one mentoring and coaching in animation and game '
            'development — practical guidance for your projects and '
            'career.'
        ),
    ),
    'focus_areas': os.getenv(
        'SITE_FOCUS_AREAS',
        (
            'Animation workflow & storytelling,Game design '
            'fundamentals,Career guidance in creative industries,'
            'Portfolio and project feedback'
        ),
    ).split(','),
    'asset_version': _env('ASSET_VERSION', '1'),
}


@app.route('/')
def index():
    return render_template(
        'index.html',
        config=SITE_CONFIG,
        base_path=BASE_PATH,
        current_year=datetime.now().year,
    )


def _home_href() -> str:
    return f"{BASE_PATH}/" if BASE_PATH else '/'


def _blog_index_href() -> str:
    return f"{BASE_PATH}/blog/" if BASE_PATH else '/blog/'


@app.route('/blog/')
def blog_index():
    posts = load_posts()
    return render_template(
        'blog/list.html',
        posts=posts,
        config=SITE_CONFIG,
        base_path=BASE_PATH,
        current_year=datetime.now().year,
        home_href=_home_href(),
        blog_index_href=_blog_index_href(),
    )


@app.route('/blog/<slug>/')
def blog_detail(slug: str):
    posts = load_posts()
    post = find_post(slug, posts=posts)
    if post is None:
        abort(404)

    blog_index_href = _blog_index_href()
    canonical_url = request.base_url
    hero_image_url = None
    if post.get('hero_image'):
        hero_image_url = url_for('static', filename=post['hero_image'], _external=True)

    return render_template(
        'blog/detail.html',
        post=post,
        posts=posts,
        config=SITE_CONFIG,
        base_path=BASE_PATH,
        current_year=datetime.now().year,
        home_href=_home_href(),
        blog_index_href=blog_index_href,
        canonical_url=canonical_url,
        hero_image_url=hero_image_url,
    )


if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    app.run(host=host, port=port, debug=debug)
