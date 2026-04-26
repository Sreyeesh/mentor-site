import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, abort, g, redirect, render_template, request, url_for

load_dotenv()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

from blog import find_post, load_posts, normalize_media_path  # noqa: E402

SITE_CONFIG = {
    'name': os.getenv('SITE_NAME', 'Sreyeesh Garimella'),
    'tagline': os.getenv('SITE_TAGLINE', 'Full-Stack Developer · Toucan.ee'),
    'email': os.getenv('SITE_EMAIL', 'toucan.sg@gmail.com'),
    'site_url': os.getenv('SITE_URL', '').rstrip('/'),
    'meta_description': os.getenv(
        'SITE_META_DESCRIPTION',
        'Full-stack developer and technical artist — writing about software, '
        'tools, and the craft of building things.',
    ),
    'asset_version': os.getenv('ASSET_VERSION', '1'),
    'plausible_script_url': os.getenv('PLAUSIBLE_SCRIPT_URL', ''),
    'plausible_domain': os.getenv('PLAUSIBLE_DOMAIN', ''),
    'social_image': os.getenv('SITE_SOCIAL_IMAGE', 'images/SreyeeshProfilePic.jpg'),
    'github_url': os.getenv('SITE_GITHUB_URL', 'https://github.com/Sreyeesh'),
    'linkedin_url': os.getenv(
        'SITE_LINKEDIN_URL', 'https://www.linkedin.com/in/sreyeeshgarimella'
    ),
    'location': os.getenv('SITE_LOCATION', 'Estonia'),
}

NAV_LINKS = [
    {'label': 'Home', 'href': '/'},
    {'label': 'Writing', 'href': '/blog/'},
    {'label': 'About', 'href': '/about/'},
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


def build_page_context(**extra) -> dict:
    return {
        'config': SITE_CONFIG,
        'current_year': datetime.now().year,
        'nav_links': NAV_LINKS,
        'site_links': SITE_LINKS,
        'canonical_url': build_absolute_url(request.path),
        **extra,
    }


NOTION_SIGNUP_URL = (
    'https://observant-toothpaste-fa5.notion.site/'
    '64939681cd2c4a1f899c6ac8d2fe4e74?pvs=105'
)

ABOUT_EXPERIENCE = [
    {
        'company': 'Walt Disney Animation Studios',
        'role': 'Pipeline Technical Director',
        'logo': 'images/Walt_Disney_Animation_Studios_logo.svg.png',
    },
    {
        'company': 'Blizzard Entertainment',
        'role': 'Technical Artist',
        'logo': 'images/Blizzard_Entertainment_Logo_2015.svg.png',
    },
    {
        'company': 'DNEG',
        'role': 'Pipeline Technical Director',
        'logo': 'images/DNEG_Animation_2025.svg.png',
    },
    {
        'company': 'Boulder Media',
        'role': 'Pipeline Developer',
        'logo': 'images/Boulder_Media.png',
    },
]

COMING_SOON_TOPICS = [
    'DevOps workflows and terminal setups that actually work in production',
    'Building tools and automation for creative studios',
    "Full-stack development from a technical director's perspective",
    'Lessons from shipping at Disney, Blizzard, and DNEG',
]


@app.route('/')
def home():
    return render_template(
        'home.html', **build_page_context(page_slug='home', posts=get_posts())
    )


@app.route('/coming-soon/')
def coming_soon():
    return render_template(
        'coming-soon-full.html',
        **build_page_context(),
        signup_url=NOTION_SIGNUP_URL,
        topics=COMING_SOON_TOPICS,
    )


@app.route('/blog/')
def blog_index():
    return redirect('/')


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
        experience=ABOUT_EXPERIENCE,
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
