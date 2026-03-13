import os
from pathlib import Path

from flask import Flask, redirect, url_for

from models import db

from .views import bp as authoring_bp


def create_app() -> Flask:
    """Application factory for the authoring tool."""
    project_root = Path(__file__).resolve().parent.parent
    static_root = project_root / 'static'
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder=str(static_root),
    )

    default_media_dir = static_root / 'uploads'

    app.config.from_mapping(
        SECRET_KEY=os.getenv('AUTHORING_SECRET_KEY', 'dev-authoring-secret'),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///blog.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        STATIC_ROOT=static_root.resolve(),
        MEDIA_UPLOAD_DIR=Path(
            os.getenv('AUTHORING_MEDIA_DIR', default_media_dir)
        ).resolve(),
        MEDIA_URL_PREFIX=os.getenv(
            'AUTHORING_MEDIA_URL_PREFIX',
            '/static/uploads',
        ),
        ALLOWED_MEDIA_EXTENSIONS={
            'png',
            'jpg',
            'jpeg',
            'gif',
            'webp',
            'svg',
            'mp4',
            'mov',
            'webm',
            'ogv',
            'mp3',
            'wav',
        },
        SITE_NAME=os.getenv('SITE_NAME', 'Toucan.ee Preview'),
    )

    media_dir: Path = app.config['MEDIA_UPLOAD_DIR']
    media_dir.mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    app.register_blueprint(authoring_bp)

    @app.route('/')
    def root_redirect() -> str:
        return redirect(url_for('authoring.dashboard'))

    return app
