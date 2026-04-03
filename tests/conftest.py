import sys
from pathlib import Path
from datetime import date

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def app():
    """Flask app wired to an in-memory SQLite database."""
    import app as app_module
    flask_app = app_module.app
    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite://',  # in-memory
        WTF_CSRF_ENABLED=False,
    )

    from models import db
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    with app.test_client() as c:
        yield c


@pytest.fixture
def sample_post(app):
    """Insert a published post and return it."""
    from models import Post, db
    post = Post(
        title='Test Post',
        slug='test-post',
        date=date(2026, 1, 15),
        body='# Hello\n\nThis is the body.',
        description='A test post.',
        tags='testing,python',
        draft=False,
    )
    with app.app_context():
        db.session.add(post)
        db.session.commit()
        db.session.refresh(post)
    return post
