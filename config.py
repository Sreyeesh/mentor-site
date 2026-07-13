import os
from datetime import datetime

from flask import request, url_for

from content.loader import load_toml


SITE_CONTENT = load_toml('site.toml')
SITE_DEFAULTS = SITE_CONTENT['site']


def site_value(key: str, env_var: str) -> str:
    return os.getenv(env_var, SITE_DEFAULTS.get(key, ''))


SITE_CONFIG = {
    'name': site_value('name', 'SITE_NAME'),
    'brand_name': site_value('brand_name', 'SITE_BRAND_NAME'),
    'brand_legal_name': site_value(
        'brand_legal_name',
        'SITE_BRAND_LEGAL_NAME',
    ),
    'tagline': site_value('tagline', 'SITE_TAGLINE'),
    'email': site_value('email', 'SITE_EMAIL'),
    'site_url': site_value('site_url', 'SITE_URL').rstrip('/'),
    'meta_description': site_value(
        'meta_description',
        'SITE_META_DESCRIPTION',
    ),
    'asset_version': site_value('asset_version', 'ASSET_VERSION'),
    'social_image': site_value('social_image', 'SITE_SOCIAL_IMAGE'),
    'github_url': site_value('github_url', 'SITE_GITHUB_URL'),
    'linkedin_url': site_value('linkedin_url', 'SITE_LINKEDIN_URL'),
    'imdb_url': site_value('imdb_url', 'SITE_IMDB_URL'),
    'location': site_value('location', 'SITE_LOCATION'),
}

NAV_LINKS = SITE_CONTENT['nav_links']
SITE_LINKS = SITE_CONTENT['site_links']


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
