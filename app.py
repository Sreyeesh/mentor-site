import os
from datetime import datetime

from dotenv import load_dotenv
from flask import (
    Flask, abort, g, redirect, render_template, request, url_for,
)
from markupsafe import Markup

load_dotenv()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

from blog import find_post, load_posts, normalize_media_path  # noqa: E402
from metrics import bar_heights, collect_metrics  # noqa: E402

# Captured once at startup / freeze time — the static build bakes these
# values into the HTML, so they are "as of last deploy" by design.
BUILD_METRICS = collect_metrics()
BUILD_METRICS['weekly_bars'] = bar_heights(BUILD_METRICS['weekly_commits'])


def _icon(name, size=16, label=None):
    aria_hidden = 'false' if label else 'true'
    role = ' role="img"' if label else ''
    title = f'<title>{label}</title>' if label else ''
    return Markup(
        f'<svg width="{size}" height="{size}"'
        f' aria-hidden="{aria_hidden}"{role} focusable="false">'
        f'<use href="#{name}"></use>{title}</svg>'
    )


app.jinja_env.globals['icon'] = _icon

SITE_CONFIG = {
    'name': os.getenv('SITE_NAME', 'Sreyeesh Garimella'),
    'brand_name': os.getenv('SITE_BRAND_NAME', 'Toucan Studios'),
    'brand_legal_name': os.getenv('SITE_BRAND_LEGAL_NAME', 'Toucan Studios OÜ'),
    'tagline': os.getenv(
        'SITE_TAGLINE',
        'Pipeline TD and Software Developer',
    ),
    'email': os.getenv('SITE_EMAIL', 'toucan.sg@gmail.com'),
    'phone': os.getenv('SITE_PHONE', '+372 5827 7155'),
    'site_url': os.getenv('SITE_URL', '').rstrip('/'),
    'meta_description': os.getenv(
        'SITE_META_DESCRIPTION',
        'CV and portfolio for Sreyeesh Garimella: Python tooling, workflow '
        'automation, and production technology for animation, games, and beyond.',
    ),
    'asset_version': os.getenv('ASSET_VERSION', '1'),
    'social_image': os.getenv('SITE_SOCIAL_IMAGE', 'images/SreyeeshProfilePic.jpg'),
    'github_url': os.getenv('SITE_GITHUB_URL', 'https://github.com/Sreyeesh'),
    'linkedin_url': os.getenv(
        'SITE_LINKEDIN_URL',
        'https://www.linkedin.com/in/sreyeeshgarimella',
    ),
    'imdb_url': os.getenv('SITE_IMDB_URL', ''),
    'location': os.getenv('SITE_LOCATION', 'Estonia'),
    'launch_date': os.getenv('SITE_LAUNCH_DATE', '2026-05-31'),
}

NAV_LINKS = [
    {'label': 'Home', 'href': '/', 'slug': 'home'},
    {'label': 'Writing', 'href': '/blog/', 'slug': 'blog'},
    {'label': 'About', 'href': '/about/', 'slug': 'about'},
]

SITE_LINKS = {
    'home': '/',
    'blog': '/blog/',
    'about': '/about/',
}


def get_posts():
    if 'posts' not in g:
        g.posts = load_posts()
    return g.posts


def build_absolute_url(path: str) -> str:
    site_url = SITE_CONFIG['site_url']
    normalized = path if path.startswith('/') else f'/{path}'
    if site_url:
        return f'{site_url}{normalized}'
    return f'{request.url_root.rstrip("/")}{normalized}'


def build_social_image_url() -> str:
    social_image = SITE_CONFIG['social_image']
    if social_image.startswith(('http://', 'https://')):
        return social_image
    static_path = url_for('static', filename=social_image)
    return build_absolute_url(static_path)


def build_page_context(**extra) -> dict:
    context = {
        'config': SITE_CONFIG,
        'current_year': datetime.now().year,
        'nav_links': NAV_LINKS,
        'site_links': SITE_LINKS,
        'canonical_url': build_absolute_url(request.path),
        'social_image_url': build_social_image_url(),
    }
    context.update(extra)
    return context


# Rebuild-board content for the construction dashboard. The workstream
# stat panel derives shipped/total from this list — update it here only.
CONSTRUCTION_PAGE = {
    'workstreams': [
        {'label': 'design system', 'state': 'shipped'},
        {'label': 'static build pipeline', 'state': 'shipped'},
        {'label': 'terraform + aws', 'state': 'in progress'},
        {'label': 'cv, devops edition', 'state': 'queued'},
    ],
    'deploy_target': [
        {'label': 'compute', 'value': 'AWS EC2, free tier'},
        {'label': 'provisioning', 'value': 'Terraform'},
        {'label': 'serving', 'value': 'gunicorn + nginx, Docker'},
        {'label': 'current host', 'value': 'GitHub Pages, static'},
    ],
}


@app.route('/')
def home():
    workstreams = CONSTRUCTION_PAGE['workstreams']
    return render_template(
        'construction.html',
        metrics=BUILD_METRICS,
        workstreams=workstreams,
        shipped_count=sum(
            1 for item in workstreams if item['state'] == 'shipped'
        ),
        deploy_target=CONSTRUCTION_PAGE['deploy_target'],
        **build_page_context(page_slug='home'),
    )


@app.route('/privacy/')
def privacy():
    """Standalone privacy notice for the waitlist signup (frozen for Pages)."""
    return render_template(
        'privacy.html',
        **build_page_context(page_slug='privacy'),
    )


@app.route('/blog/')
def blog_index():
    return render_template(
        'blog/list.html',
        **build_page_context(page_slug='blog', posts=get_posts()),
        blog_index_href='/blog/',
    )


@app.route('/blog/<slug>/')
def blog_detail(slug: str):
    post = find_post(slug, posts=get_posts())
    if post is None:
        abort(404)
    hero_value, is_external = normalize_media_path(post.get('hero_image'))
    if is_external:
        hero_url = hero_value
    elif hero_value:
        hero_url = url_for('static', filename=hero_value)
    else:
        hero_url = None
    return render_template(
        'blog/detail.html',
        **build_page_context(page_slug='blog', post=post, hero_image_url=hero_url),
    )


@app.route('/about/')
def about():
    return render_template(
        'about.html',
        **build_page_context(page_slug='about'),
    )


@app.route('/sitemap.xml')
def sitemap():
    posts = get_posts()
    today = datetime.utcnow().date().isoformat()
    urls = [
        {'loc': build_absolute_url(p), 'lastmod': today, 'changefreq': 'weekly'}
        for p in ['/', '/blog/', '/about/']
    ] + [
        {
            'loc': build_absolute_url(f'/blog/{post["slug"]}/'),
            'lastmod': post.get('date'),
            'changefreq': 'monthly',
        }
        for post in posts
    ]
    return (
        render_template('sitemap.xml', urls=urls),
        {'Content-Type': 'application/xml'},
    )


@app.route('/robots.txt')
def robots_txt():
    lines = [
        'User-agent: *',
        'Allow: /',
        f'Sitemap: {build_absolute_url("/sitemap.xml")}',
    ]
    return '\n'.join(lines) + '\n', {'Content-Type': 'text/plain'}


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true',
    )
