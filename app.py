from flask import Flask, render_template
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Support optional base path for GitHub Pages (e.g., "/<repo-name>")
BASE_PATH = os.getenv('BASE_PATH', '')
if BASE_PATH and not BASE_PATH.startswith('/'):
    BASE_PATH = '/' + BASE_PATH

# Fix static file serving - ensure static files are always served from /static
app = Flask(__name__)

# Site settings from environment variables
SITE_CONFIG = {
    'name': os.getenv('SITE_NAME', 'Sreyeesh Garimella'),
    'tagline': os.getenv('SITE_TAGLINE', 'Mentoring & Coaching in Animation and Video Game Development'),
    'email': os.getenv('SITE_EMAIL', 'toucan.sg@gmail.com'),
    'calendly_link': os.getenv('SITE_CALENDLY_LINK', 'https://calendly.com/toucan-sg/60min'),
    'meta_description': os.getenv('SITE_META_DESCRIPTION', 'One-on-one mentoring and coaching in animation and game development — practical guidance for your projects and career.'),
    'focus_areas': os.getenv('SITE_FOCUS_AREAS', 'Animation workflow & storytelling,Game design fundamentals,Career guidance in creative industries,Portfolio and project feedback').split(','),
    'asset_version': os.getenv('ASSET_VERSION', '1')
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
