import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, abort, g, render_template, request, url_for

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
        '1:1 game development mentoring for beginners, hobbyists, and indie '
        'teams. Engine-agnostic. Godot, Unity, Unreal, or your own.',
    ),
    'asset_version': os.getenv('ASSET_VERSION', '1'),
    'plausible_script_url': os.getenv('PLAUSIBLE_SCRIPT_URL', ''),
    'plausible_domain': os.getenv('PLAUSIBLE_DOMAIN', ''),
    'social_image': os.getenv('SITE_SOCIAL_IMAGE', 'images/SreyeeshProfilePic.jpg'),
    'github_url': os.getenv('SITE_GITHUB_URL', ''),
    'linkedin_url': os.getenv('SITE_LINKEDIN_URL', ''),
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


MENTORING_BOOKING_URL = os.getenv(
    'MENTORING_BOOKING_URL',
    'https://cal.com/sreyeesh-dhb2sk/60min',
)

GAMECITY_STUDENT_BOOKING_URL = os.getenv('GAMECITY_STUDENT_BOOKING_URL', '')

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

LANDING_PAGE = {
    'page_title': 'Game Dev Mentoring',
    'eyebrow': '1:1 Game Dev Mentoring',
    'headline': 'Senior guidance for the engineering side of making games.',
    'lede': (
        'For beginners, hobbyists, and small indie teams. Engine-agnostic. '
        'Godot, Unity, Unreal, or your own. Bring what you are stuck on; '
        'leave with a concrete next step.'
    ),
    'cta_label': 'Book a session',
    'cta_meta': '€75 · 60 min · 1:1 video call',
    'cta_meta_short': '€75 · 60 min',
    'trust': 'A decade in production pipelines · replies within 24h',
    'audience_label': "Who it's for",
    'audience_heading': 'This is for you if…',
    'audience': [
        "You're picking your first engine and want to start a real project.",
        "You're building something on the side and stuck on a specific problem.",
        "You're on a small indie team (2–5) and want senior input "
        "without hiring senior.",
        "You can write some code, but the engineering side of "
        "game-making feels overwhelming.",
    ],
    'topics_label': 'What I cover',
    'topics': [
        'Architecture and code structure that scales with your project',
        'Tooling, pipelines, and version control for game projects',
        'Debugging, performance, and keeping scope under control',
    ],
    'steps_label': 'How it works',
    'steps': [
        'Book a 60-minute session and tell me what you are working on.',
        'I meet with you 1:1 over video.',
        'You leave with a concrete next step.',
    ],
    'about_label': 'About',
    'about_body': (
        "I've spent the last decade building production tools and pipelines "
        "for studios. I mentor the engineering side of game-making, the "
        "parts that transfer no matter which engine you pick."
    ),
    'faq_label': 'FAQ',
    'faq': [
        {
            'q': "I'm a complete beginner. Is this for me?",
            'a': 'Yes. A lot of what I do is help people choose an engine, '
                 'scope a first project, and avoid the traps that stall beginners.',
        },
        {
            'q': 'Which engine do you teach?',
            'a': "I'm engine-agnostic. The concepts I focus on (architecture, "
                 'tooling, debugging, scoping) carry across Godot, Unity, Unreal, '
                 "or a custom stack. Bring whatever you're using.",
        },
        {
            'q': 'How long is a session?',
            'a': '60 minutes, 1:1, over video. €75 per session.',
        },
        {
            'q': 'Can I book more than one?',
            'a': "Yes. Most people book a single session first, see if it's "
                 'useful, and come back when they hit the next wall.',
        },
    ],
    'closing_heading': 'Ready when you are.',
    'closing_body': (
        'Book a 60-minute session and come prepared with what you are '
        'working on.'
    ),
}


@app.route('/')
def home():
    return render_template(
        'landing.html',
        **build_page_context(page_slug='home'),
        booking_url=MENTORING_BOOKING_URL,
        gamecity_booking_url=GAMECITY_STUDENT_BOOKING_URL,
        landing=LANDING_PAGE,
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
