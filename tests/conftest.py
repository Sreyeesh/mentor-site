import importlib
import sqlite3
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _reload_module(name: str):
    module = importlib.import_module(name)
    return importlib.reload(module)


@pytest.fixture
def app(tmp_path, monkeypatch):
    """Spin up the Flask app against a per-test SQLite database."""

    db_path = tmp_path / 'test_checkout.sqlite'
    monkeypatch.setenv('DATABASE', str(db_path))
    monkeypatch.setenv('DATABASE_PATH', str(db_path))
    monkeypatch.setenv('DATABASE_URL', f"sqlite:///{db_path}")
    monkeypatch.setenv(
        'SITE_CALENDLY_LINK',
        'https://calendly.com/toucan-sg/consulting-link',
    )
    monkeypatch.setenv('STRIPE_SECRET_KEY', 'sk_test_checkout')
    monkeypatch.setenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_checkout')
    monkeypatch.setenv('STRIPE_PRICE_ID', 'price_test_checkout')
    monkeypatch.setenv(
        'STRIPE_SUCCESS_URL',
        'http://localhost/schedule?session_id={CHECKOUT_SESSION_ID}',
    )
    monkeypatch.setenv(
        'STRIPE_CANCEL_URL',
        'http://localhost/tutoring?checkout=cancelled',
    )
    monkeypatch.setenv('STRIPE_ENDPOINT_SECRET', 'whsec_test_checkout')

    app_module = _reload_module('app')
    db_module = _reload_module('db')

    if hasattr(app_module, 'create_app'):
        flask_app = app_module.create_app()
    else:
        flask_app = app_module.app

    flask_app.config.update(
        TESTING=True,
        DATABASE=str(db_path),
    )

    with flask_app.app_context():
        init_db = getattr(db_module, 'init_db', None)
        if init_db is None:
            raise RuntimeError('db.init_db is required for the tutoring tests.')
        try:
            init_db(str(db_path))
        except TypeError:
            init_db()

    yield flask_app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def fetch_checkout_records(app):
    """Return a helper that reads checkout_sessions rows."""

    db_path = Path(app.config['DATABASE'])

    def _fetch(session_id: str | None = None):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        query = (
            "SELECT session_id, customer_email, payment_status "
            "FROM checkout_sessions"
        )
        params = ()
        if session_id:
            query += " WHERE session_id = ?"
            params = (session_id,)
        rows = conn.execute(query, params).fetchall()
        conn.close()
        return rows

    return _fetch
