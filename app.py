import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv()

BASE_PATH = os.getenv('BASE_PATH', '')
if BASE_PATH and not BASE_PATH.startswith('/'):
    BASE_PATH = f"/{BASE_PATH}"

app = Flask(__name__)


SITE_CONFIG = {
    'name': os.getenv('SITE_NAME', 'Sreyeesh Garimella'),
    'tagline': os.getenv(
        'SITE_TAGLINE',
        'Mentoring & Coaching in Animation and Video Game Development',
    ),
    'email': os.getenv('SITE_EMAIL', 'toucan.sg@gmail.com'),
    'linkedin_url': os.getenv(
        'SITE_LINKEDIN_URL',
        'https://www.linkedin.com/in/sreyeeshgarimella',
    ),
    'calendly_link': os.getenv(
        'SITE_CALENDLY_LINK',
        'https://calendly.com/toucan-sg/60min',
    ),
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
    'asset_version': os.getenv('ASSET_VERSION', '1'),
    'giscus': {
        'repo': os.getenv('GISCUS_REPO', ''),
        'repo_id': os.getenv('GISCUS_REPO_ID', ''),
        'category': os.getenv('GISCUS_CATEGORY', ''),
        'category_id': os.getenv('GISCUS_CATEGORY_ID', ''),
        'mapping': os.getenv('GISCUS_MAPPING', 'pathname'),
        'strict': os.getenv('GISCUS_STRICT', '1'),
        'reactions_enabled': os.getenv('GISCUS_REACTIONS_ENABLED', '1'),
        'emit_metadata': os.getenv('GISCUS_EMIT_METADATA', '0'),
        'input_position': os.getenv('GISCUS_INPUT_POSITION', 'bottom'),
        'lang': os.getenv('GISCUS_LANG', 'en'),
        'theme_light': os.getenv('GISCUS_THEME_LIGHT', 'light'),
        'theme_dark': os.getenv('GISCUS_THEME_DARK', 'dark'),
        'loading': os.getenv('GISCUS_LOADING', 'lazy'),
    },
}


@app.route('/')
def index():
    return render_template(
        'index.html',
        config=SITE_CONFIG,
        base_path=BASE_PATH,
        current_year=datetime.now().year,
    )


if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    app.run(host=host, port=port, debug=debug)
