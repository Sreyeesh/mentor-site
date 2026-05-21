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
    'plausible_script_url': os.getenv('PLAUSIBLE_SCRIPT_URL', ''),
    'plausible_domain': os.getenv('PLAUSIBLE_DOMAIN', ''),
    'social_image': os.getenv('SITE_SOCIAL_IMAGE', 'images/SreyeeshProfilePic.jpg'),
    'github_url': os.getenv('SITE_GITHUB_URL', ''),
    'linkedin_url': os.getenv(
        'SITE_LINKEDIN_URL',
        'https://www.linkedin.com/in/sreyeeshgarimella',
    ),
    'imdb_url': os.getenv('SITE_IMDB_URL', ''),
    'location': os.getenv('SITE_LOCATION', 'Estonia'),
    'launch_date': os.getenv('SITE_LAUNCH_DATE', '2026-05-31'),
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


CV_PAGE = {
    'page_title': 'CV and Portfolio',
    'eyebrow': 'CV / Portfolio',
    'headline': 'Pipeline TD and software developer for production technology.',
    'tagline': (
        'Python tooling, workflow automation, and technical mentoring for '
        'animation, games, and beyond.'
    ),
    'summary': (
        'Pipeline TD with VFX and feature animation studio experience in '
        'Python tool development, Linux, and DCC pipelines including Maya, '
        'Katana, Houdini, and Nuke. Experienced in sprint-based development, '
        'code reviews, stakeholder documentation, and mentoring Assistant TDs.'
    ),
    'fit': [
        'Pipeline TD / production technology roles',
        'Python tooling and workflow automation',
        'Internal tools, workflow automation, and support engineering',
        'Creative technology for animation, VFX, and games',
    ],
    'experience': [
        {
            'role': 'Technical Mentor and Production Workflow Specialist',
            'company': 'Toucan Studios OÜ',
            'period': 'Jun 2023 - present',
            'location': 'Estonia',
            'summary': (
                'Technical mentoring and production workflow support for '
                'junior developers and creative technology learners.'
            ),
            'highlights': [
                'Mentored junior developers on Python, Git, pipeline standards, '
                'and technical problem-solving.',
                'Delivered formal tutorials and documentation to support team '
                'growth.',
                'Led sprint-style development cycles and tracked tasks to '
                'deliver tooling on schedule.',
            ],
        },
        {
            'role': 'Lighting TD / Pipeline Support',
            'company': 'DNEG',
            'period': '2022 - 2023',
            'location': 'Remote',
            'summary': (
                'Python tooling and production support for Maya, Katana, USD '
                'shot workflows, RenderMan, and ShotGrid pipeline work.'
            ),
            'highlights': [
                'Built Python tooling in Maya and Katana supporting USD shot '
                'workflows and RenderMan rendering.',
                'Collaborated with R&D and creative supervisors on show-specific '
                'tool development.',
                'Gathered and actioned stakeholder feedback on pipeline tasks.',
                'Provided face-to-face technical support to artists and bridged '
                'technical and non-technical teams.',
            ],
        },
        {
            'role': 'Production Show Technician - In-Game Cinematics',
            'company': 'Blizzard Entertainment',
            'period': 'May 2021 - Nov 2021',
            'location': 'Remote',
            'summary': (
                'Lighting, rendering, and publishing workflow support for '
                'in-game cinematics production.'
            ),
            'highlights': [
                'Developed Python and Lua tools integrated with ShotGrid.',
                'Supported lighting, rendering, and publishing workflows.',
                'Mentored artists on workflow issues and supported technical '
                'handoffs between TDs and production.',
            ],
        },
        {
            'role': 'Render Wrangler',
            'company': 'Boulder Media',
            'period': 'Nov 2019 - Jan 2021',
            'location': 'Dublin, Ireland',
            'summary': 'Render farm operations and production continuity.',
            'highlights': [
                'Managed render farm operations under tight deadlines.',
                'Coordinated with artists and production to resolve issues.',
            ],
        },
        {
            'role': 'Assistant Technical Director',
            'company': 'Walt Disney Animation Studios',
            'period': 'Jul 2019 - Aug 2019',
            'location': 'Burbank, CA',
            'summary': (
                'Pipeline workflow, DCC troubleshooting, and technical '
                'production systems support.'
            ),
            'highlights': [
                'Supported technical production systems across shot and asset '
                'work.',
                'Helped troubleshoot DCC and pipeline workflow issues.',
            ],
        },
        {
            'role': 'Pipeline TD',
            'company': 'Encore VFX',
            'period': 'Dec 2018 - Feb 2019',
            'location': 'Burbank, CA',
            'summary': 'Pipeline and technical operations support for VFX work.',
            'highlights': [
                'Supported pipeline and technical operations on VFX productions.',
                'Resolved DCC and workflow issues for artists.',
            ],
        },
        {
            'role': 'Render Wrangler',
            'company': 'FuseFX',
            'period': 'Aug 2018 - Dec 2018',
            'location': 'Los Angeles, CA',
            'summary': 'Render farm support across VFX productions.',
            'highlights': [
                'Diagnosed rendering failures.',
                'Maintained production render pipelines.',
            ],
        },
        {
            'role': 'Render Wrangler',
            'company': 'CoSA VFX',
            'period': 'Dec 2016 - Aug 2018',
            'location': 'Los Angeles, CA',
            'summary': 'Render farm management for VFX productions.',
            'highlights': [
                'Delivered two years of render farm management.',
                'Supported V-Ray and Redshift rendering workflows.',
            ],
        },
    ],
    'credits': [
        'Blizzard Entertainment',
        'DNEG Animation',
        'Walt Disney Animation Studios',
        'Boulder Media',
        'GameCityKajaani',
    ],
    'skills': [
        {
            'group': 'Languages and systems',
            'items': ['Python', 'Linux', 'Lua', 'Git', 'Sprint development'],
        },
        {
            'group': 'DCC and pipeline',
            'items': [
                'Maya',
                'Houdini',
                'Katana',
                'Nuke',
                'ShotGrid / Flow',
            ],
        },
        {
            'group': 'Rendering and data',
            'items': ['USD / Alembic', 'RenderMan', 'Deadline', 'V-Ray', 'Redshift'],
        },
        {
            'group': 'Production practice',
            'items': [
                'Tool development',
                'Code review',
                'Pipeline workflows',
                'Mentoring',
                'Documentation',
            ],
        },
    ],
    'education': [
        {
            'school': 'California State University, Northridge',
            'credential': 'Art & Animation',
            'period': '2010 - 2012',
        },
        {
            'school': 'College of the Canyons',
            'credential': 'Associate of Arts, Animation',
            'period': '2007 - 2010',
        },
        {
            'school': 'iAnimate.net',
            'credential': 'Character Animation',
            'period': '2013',
        },
    ],
    'links_heading': 'Links',
    'contact_heading': 'Available for production technology work',
    'contact_body': (
        'I am open to industry and adjacent technical roles involving Python, '
        'workflow automation, production support, internal tools, or technical '
        'mentoring.'
    ),
}


@app.route('/')
def home():
    return render_template(
        'landing.html',
        **build_page_context(page_slug='home', main_class='cv-page-main'),
        cv=CV_PAGE,
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
