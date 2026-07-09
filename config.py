import os
from datetime import datetime

from flask import request, url_for

SITE_CONFIG = {
    'name': os.getenv('SITE_NAME', 'Sreyeesh Garimella'),
    'brand_name': os.getenv('SITE_BRAND_NAME', 'Toucan Studios'),
    'brand_legal_name': os.getenv('SITE_BRAND_LEGAL_NAME', 'Toucan Studios OÜ'),
    'tagline': os.getenv(
        'SITE_TAGLINE',
        'Pipeline TD and Software Developer',
    ),
    'email': os.getenv('SITE_EMAIL', 'toucan.sg@gmail.com'),
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
