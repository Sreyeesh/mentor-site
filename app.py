import os
from datetime import datetime

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_migrate import Migrate


def _load_environment() -> None:
    """Load variables from the appropriate .env file.

    Precedence:
        1. ENV_FILE override
        2. .env.dev when FLASK_ENV/APP_ENV indicates development
        3. .env
        4. Fallback to dotenv defaults
    """

    env_file = os.getenv('ENV_FILE')
    env_hint = os.getenv('APP_ENV') or os.getenv('FLASK_ENV')

    if not env_file and env_hint:
        if env_hint.lower().startswith('dev') and os.path.exists('.env.dev'):
            env_file = '.env.dev'

    if not env_file:
        if os.path.exists('.env'):
            env_file = '.env'
        elif os.path.exists('.env.dev'):
            env_file = '.env.dev'

    load_dotenv(env_file)


_load_environment()


def _env(key: str, default: str = '') -> str:
    """Return a stripped environment value with an optional default."""

    value = os.getenv(key)
    if value is None:
        return default
    return value.strip()


BASE_PATH = _env('BASE_PATH')
if BASE_PATH and not BASE_PATH.startswith('/'):
    BASE_PATH = f"/{BASE_PATH}"
LEGACY_BASE_PATH = '/toucan-ee'

POSTS_PER_PAGE = 10

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SECRET_KEY'] = _env('SECRET_KEY', 'dev-secret-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = _env('DATABASE_URL', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import Post, db  # noqa: E402
from admin import init_admin  # noqa: E402
from blog import normalize_media_path  # noqa: E402

db.init_app(app)
migrate = Migrate(app, db)
init_admin(app)


class BasePathMiddleware:
    """Allow serving the Flask app under a sub-path when BASE_PATH is set."""

    def __init__(self, wsgi_app, base_path: str):
        self.wsgi_app = wsgi_app
        self.base_path = base_path

    def __call__(self, environ, start_response):
        base_path = self.base_path
        if not base_path:
            return self.wsgi_app(environ, start_response)

        path_info = environ.get('PATH_INFO', '')
        if path_info.startswith(base_path):
            trimmed = path_info[len(base_path):]
            environ['PATH_INFO'] = trimmed or '/'
        return self.wsgi_app(environ, start_response)


SITE_CONFIG = {
    'name': os.getenv('SITE_NAME', 'Sreyeesh Garimella'),
    'tagline': os.getenv('SITE_TAGLINE', 'Senior Full-Stack Developer & Mentor'),
    'email': os.getenv('SITE_EMAIL', 'toucan.sg@gmail.com'),
    'site_url': os.getenv('SITE_URL', '').rstrip('/'),
    'meta_description': os.getenv(
        'SITE_META_DESCRIPTION',
        (
            'Senior full-stack developer and mentor — writing about software, '
            'tools, and the craft of building things.'
        ),
    ),
    'asset_version': _env('ASSET_VERSION', '1'),
    'plausible_script_url': _env('PLAUSIBLE_SCRIPT_URL'),
    'plausible_domain': _env('PLAUSIBLE_DOMAIN'),
    'social_image': _env('SITE_SOCIAL_IMAGE', 'images/SreyeeshProfilePic.jpg'),
}


def _normalize_base_path(raw: str | None) -> str:
    if not raw:
        return ''
    raw = raw.strip()
    if not raw:
        return ''
    if not raw.startswith('/'):
        raw = f"/{raw}"
    normalized = raw.rstrip('/')
    if normalized == '':
        return ''
    return normalized


def configure_base_path(raw: str | None) -> None:
    normalized = _normalize_base_path(raw)
    app.config['SITE_BASE_PATH'] = normalized
    original_wsgi = app.config.setdefault('_ORIGINAL_WSGI_APP', app.wsgi_app)
    if normalized:
        app.wsgi_app = BasePathMiddleware(original_wsgi, normalized)
    else:
        app.wsgi_app = original_wsgi


configure_base_path(BASE_PATH)


@app.before_request
def _redirect_legacy_base_path():
    """Redirect legacy base path requests when no base path is configured."""

    if _resolve_base_path():
        return

    fallback = LEGACY_BASE_PATH.rstrip('/')
    if not fallback:
        return

    path = request.path or '/'
    if not path.startswith(fallback):
        return

    remainder = path[len(fallback):] or '/'
    query_string = request.query_string.decode('utf-8')
    if query_string:
        remainder = f"{remainder}?{query_string}"
    return redirect(remainder, code=302)


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
        'blog': prefix('/blog/'),
    }


def build_primary_nav(base_path_override: str | None = None) -> list:
    links = build_site_links(base_path_override)
    return [
        {'label': 'Blog', 'href': links['blog']},
    ]


def _build_canonical_url(base_path_value: str) -> str:
    site_url = SITE_CONFIG.get('site_url', '').rstrip('/')
    request_path = request.path or '/'
    if base_path_value and not request_path.startswith(base_path_value):
        if request_path == '/':
            request_path = f"{base_path_value}/"
        else:
            request_path = f"{base_path_value}{request_path}"
    if site_url:
        return f"{site_url}{request_path}"
    return f"{request.url_root.rstrip('/')}{request_path}"


def _build_social_image_url() -> str:
    social_image = SITE_CONFIG.get('social_image') or ''
    if social_image.startswith('http://') or social_image.startswith('https://'):
        return social_image
    image_path = social_image or 'images/SreyeeshProfilePic.jpg'
    asset_path = url_for('static', filename=image_path)
    site_url = SITE_CONFIG.get('site_url', '').rstrip('/')
    if site_url:
        return f"{site_url}{asset_path}"
    return url_for('static', filename=image_path, _external=True)


def build_page_context(
    *,
    base_path_override: str | None = None,
    **extra: object,
) -> dict:
    base_path_value = _resolve_base_path(base_path_override)
    canonical_url = _build_canonical_url(base_path_value)
    social_image_url = _build_social_image_url()
    context = {
        'config': SITE_CONFIG,
        'current_year': datetime.now().year,
        'base_path': base_path_value,
        'site_links': build_site_links(base_path_override),
        'nav_links': build_primary_nav(base_path_override),
        'canonical_url': canonical_url,
        'social_image_url': social_image_url,
    }
    context.update(extra)
    return context


def build_absolute_url(path: str) -> str:
    """Return a fully qualified URL for sitemap/robots usage."""

    site_url = SITE_CONFIG.get('site_url', '').rstrip('/')
    normalized_path = path if path.startswith('/') else f"/{path}"
    if site_url:
        return f"{site_url}{normalized_path}"
    base = request.url_root.rstrip('/')
    return f"{base}{normalized_path}"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def home():
    return redirect(url_for('blog_index'), code=301)


@app.route('/blog/')
def blog_index():
    page = request.args.get('page', 1, type=int)
    if page < 1:
        abort(404)
    pagination = (
        Post.query
        .filter_by(draft=False)
        .order_by(Post.date.desc())
        .paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    )
    if page > 1 and not pagination.items:
        abort(404)
    links = build_site_links()
    return render_template(
        'blog/list.html',
        **build_page_context(
            page_slug='blog',
            posts=pagination.items,
            pagination=pagination,
            blog_index_href=links['blog'],
        ),
    )


@app.route('/blog/page/<int:page>/')
def blog_page(page: int):
    """Canonical paginated blog route for static-site freezing."""
    if page < 2:
        return redirect(url_for('blog_index'), code=301)
    pagination = (
        Post.query
        .filter_by(draft=False)
        .order_by(Post.date.desc())
        .paginate(page=page, per_page=POSTS_PER_PAGE, error_out=False)
    )
    if not pagination.items:
        abort(404)
    links = build_site_links()
    return render_template(
        'blog/list.html',
        **build_page_context(
            page_slug='blog',
            posts=pagination.items,
            pagination=pagination,
            blog_index_href=links['blog'],
        ),
    )


@app.route('/blog/<slug>/')
def blog_detail(slug: str):
    post = Post.query.filter_by(slug=slug, draft=False).first_or_404()

    links = build_site_links()
    detail_path = f"{links['blog']}{post.slug}/"

    site_url = SITE_CONFIG.get('site_url', '').rstrip('/')
    if site_url:
        canonical_url = f"{site_url}{detail_path}"
    else:
        canonical_url = request.base_url

    hero_value, is_external = normalize_media_path(post.hero_image)
    hero_asset_path = None
    hero_image_url = None
    if hero_value:
        if is_external:
            hero_image_url = hero_value
        else:
            hero_asset_path = url_for('static', filename=hero_value)
            hero_image_url = (
                f"{site_url}{hero_asset_path}"
                if site_url
                else url_for('static', filename=hero_value, _external=True)
            )

    related_posts = (
        Post.query
        .filter(Post.draft.is_(False), Post.slug != slug)
        .order_by(Post.date.desc())
        .limit(3)
        .all()
    )

    return render_template(
        'blog/detail.html',
        **build_page_context(
            page_slug='blog',
            post=post,
            related_posts=related_posts,
            blog_index_href=links['blog'],
            canonical_url=canonical_url,
            hero_image_url=hero_image_url,
            hero_asset_path=hero_asset_path,
            social_image_url=hero_image_url or _build_social_image_url(),
        ),
    )


@app.route('/blog/tag/<tag>/')
def blog_tag(tag: str):
    tag = tag.strip().lower()
    all_posts = (
        Post.query
        .filter_by(draft=False)
        .order_by(Post.date.desc())
        .all()
    )
    posts = [p for p in all_posts if tag in [t.lower() for t in p.tag_list()]]
    links = build_site_links()
    return render_template(
        'blog/tag.html',
        **build_page_context(
            page_slug='blog',
            posts=posts,
            tag=tag,
            blog_index_href=links['blog'],
        ),
    )


@app.route('/feed.xml')
def feed():
    posts = (
        Post.query
        .filter_by(draft=False)
        .order_by(Post.date.desc())
        .limit(20)
        .all()
    )
    links = build_site_links()
    response = make_response(
        render_template(
            'feed.xml',
            posts=posts,
            blog_href=build_absolute_url(links['blog']),
            site_url=SITE_CONFIG.get('site_url', '').rstrip('/'),
            config=SITE_CONFIG,
            now=datetime.utcnow(),
        )
    )
    response.headers['Content-Type'] = 'application/rss+xml; charset=utf-8'
    return response


@app.route('/sitemap.xml')
def sitemap():
    posts = Post.query.filter_by(draft=False).order_by(Post.date.desc()).all()
    links = build_site_links()
    urls = []

    static_pages = [links['blog']]
    for page in static_pages:
        urls.append(
            {
                'loc': build_absolute_url(page),
                'lastmod': datetime.utcnow().date().isoformat(),
                'changefreq': 'daily',
                'priority': '1.0',
            }
        )

    for post in posts:
        post_path = f"{links['blog']}{post.slug}/"
        last_modified = post.updated_at or post.date
        if hasattr(last_modified, 'date'):
            last_modified = last_modified.date()
        urls.append(
            {
                'loc': build_absolute_url(post_path),
                'lastmod': last_modified,
                'changefreq': 'monthly',
                'priority': '0.8',
            }
        )

    # Tag pages
    all_tags: set[str] = set()
    for post in posts:
        all_tags.update(post.tag_list())
    for tag in sorted(all_tags):
        urls.append(
            {
                'loc': build_absolute_url(f"{links['blog']}tag/{tag}/"),
                'lastmod': datetime.utcnow().date().isoformat(),
                'changefreq': 'weekly',
                'priority': '0.5',
            }
        )

    response = make_response(render_template('sitemap.xml', urls=urls))
    response.headers['Content-Type'] = 'application/xml'
    return response


@app.route('/robots.txt')
def robots_txt():
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {build_absolute_url('/sitemap.xml')}",
    ]
    response = make_response("\n".join(lines) + "\n")
    response.headers['Content-Type'] = 'text/plain'
    return response


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    app.run(host=host, port=port, debug=debug)
