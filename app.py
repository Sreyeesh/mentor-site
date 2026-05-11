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

MENTORING_BOOKING_URL = os.getenv(
    'MENTORING_BOOKING_URL',
    'https://cal.com/sreyeesh-dhb2sk/60min',
)

NAV_LINKS = [
    {'label': 'Home', 'href': '/'},
    {'label': 'Writing', 'href': '/blog/'},
    {'label': 'About', 'href': '/about/'},
    {
        'label': 'Book a session',
        'href': MENTORING_BOOKING_URL,
        'is_cta': True,
        'external': True,
    },
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
    'eyebrow': '1:1 game dev mentoring',
    'headline': 'Learn the engineering side of game development.',
    'lede': (
        '1:1 mentoring for beginners, hobbyists, and indie developers who '
        'want practical help with architecture, debugging, tools, scope, '
        'and engine decisions.'
    ),
    'cta_primary': 'Book a session',
    'cta_secondary': 'See what I cover',
    'cta_meta': ['EUR 75', '60 minutes', '1:1 video call'],
    'booking': {
        'title': '60 minute mentoring session',
        'subtitle': '1:1 video call. Bring what you are working on.',
        'meta': [
            ('Price', 'EUR 75'),
            ('Duration', '60 minutes'),
            ('Format', '1:1 video call'),
            ('Reply window', 'Within 24 hours'),
        ],
        'bullets': [
            'Pick an engine or unstick a decision',
            'Debug a specific problem you are stuck on',
            'Review architecture, scope, and next steps',
        ],
    },
    'audience_label': 'Who it is for',
    'audience_heading': (
        'Game devs who want senior input on the engineering side.'
    ),
    'audience': [
        {
            'title': 'Beginners choosing direction',
            'body': (
                'You are picking your first engine and want help starting '
                'a real project instead of more tutorials.'
            ),
        },
        {
            'title': 'Builders stuck mid-project',
            'body': (
                'You have something running, you are stuck on a specific '
                'problem, and you want a fresh pair of eyes.'
            ),
        },
        {
            'title': 'Small teams needing review',
            'body': (
                'You are a 2 to 5 person indie team that wants senior '
                'input without hiring a senior full time.'
            ),
        },
    ],
    'topics_label': 'What I cover',
    'topics_heading': (
        'The engineering parts that transfer across engines.'
    ),
    'topics': [
        {
            'title': 'Architecture',
            'body': (
                'Code structure, separation of concerns, and patterns that '
                'hold up as your project grows.'
            ),
        },
        {
            'title': 'Debugging',
            'body': (
                'Reading the problem, isolating the cause, and building '
                'habits that make future bugs cheaper to find.'
            ),
        },
        {
            'title': 'Production habits',
            'body': (
                'Version control, tooling, scope control, and the day to '
                'day routines that keep a project moving.'
            ),
        },
    ],
    'steps_label': 'How it works',
    'steps_heading': (
        'One booking, three steps, a concrete next step in your hand.'
    ),
    'steps': [
        {
            'title': 'Send context',
            'body': (
                'Book a session and tell me what you are working on and '
                'what you are stuck on.'
            ),
        },
        {
            'title': 'Work the problem',
            'body': (
                'We meet 1:1 over video and work the specific thing you '
                'brought, in your code, in your engine.'
            ),
        },
        {
            'title': 'Leave with direction',
            'body': (
                'You leave with a concrete next step, not a generic plan, '
                'and a clear answer to your question.'
            ),
        },
    ],
    'about_label': 'About',
    'about_heading': (
        'I have spent the last decade in production engineering.'
    ),
    'about_body': [
        (
            'I build production tools and pipelines for a living. I have '
            'shipped internal tools, debugged hard problems on tight '
            'deadlines, and watched good projects stall on bad '
            'engineering decisions. Mentoring is how I help people skip '
            'the parts I had to learn the slow way.'
        ),
        (
            'I do not push a single engine or a single methodology. I '
            'help you make the call that fits your project, your skill '
            'level, and the time you actually have.'
        ),
    ],
    'faq_label': 'FAQ',
    'faq_heading': 'Common questions before booking.',
    'faq': [
        {
            'q': 'I am a complete beginner. Is this for me?',
            'a': (
                'Yes. A lot of what I do is help people pick an engine, '
                'scope a first project, and avoid the traps that stall '
                'beginners.'
            ),
        },
        {
            'q': 'Which engines do you cover?',
            'a': (
                'I am engine agnostic. The concepts I focus on '
                '(architecture, debugging, tooling, scoping) carry across '
                'Godot, Unity, Unreal, or a custom stack. Bring whatever '
                'you are using.'
            ),
        },
        {
            'q': 'Can I bring a project I am already working on?',
            'a': (
                'Please do. The sessions work best when there is '
                'something concrete on the screen to look at and debug '
                'together.'
            ),
        },
        {
            'q': 'Do you do code review between sessions?',
            'a': (
                'Not as a default. Each session is a focused 60 minutes. '
                'If you want deeper async review, mention it when you '
                'book and we can talk scope.'
            ),
        },
    ],
    'closing_heading': 'Ready when you are.',
    'closing_body': (
        'Book a 60 minute session and come prepared with what you are '
        'working on.'
    ),
}


@app.route('/')
def home():
    return render_template(
        'landing.html',
        **build_page_context(page_slug='home'),
        booking_url=MENTORING_BOOKING_URL,
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
