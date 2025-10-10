import os
from pathlib import Path

from flask import Flask, redirect, url_for

from blog.utils import get_content_dir

from .views import bp as authoring_bp


def create_app() -> Flask:
    """Application factory for the authoring tool."""
    app = Flask(__name__, template_folder='templates')
    app.config.from_mapping(
        SECRET_KEY=os.getenv('AUTHORING_SECRET_KEY', 'dev-authoring-secret'),
        CONTENT_DIR=get_content_dir(
            os.getenv('AUTHORING_CONTENT_DIR')
        ).resolve(),
    )

    # Ensure content directory exists so authors can start immediately
    content_dir: Path = app.config['CONTENT_DIR']
    content_dir.mkdir(parents=True, exist_ok=True)

    app.register_blueprint(authoring_bp)

    @app.route('/')
    def root_redirect() -> str:
        """Provide a friendly landing page for health checks."""

        return redirect(url_for('authoring.dashboard'))

    return app
