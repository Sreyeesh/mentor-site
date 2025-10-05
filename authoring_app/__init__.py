from pathlib import Path
import os

from flask import Flask

from .views import bp as authoring_bp


def create_app() -> Flask:
    """Application factory for the authoring tool."""
    app = Flask(__name__, template_folder='templates')
    app.config.from_mapping(
        SECRET_KEY=os.getenv('AUTHORING_SECRET_KEY', 'dev-authoring-secret'),
        CONTENT_DIR=Path(
            os.getenv('AUTHORING_CONTENT_DIR', 'content/posts')
        ).resolve(),
    )

    # Ensure content directory exists so authors can start immediately
    content_dir: Path = app.config['CONTENT_DIR']
    content_dir.mkdir(parents=True, exist_ok=True)

    app.register_blueprint(authoring_bp)

    return app
