import importlib
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
def app():
    """Spin up the Flask app for testing."""

    app_module = _reload_module('app')

    if hasattr(app_module, 'create_app'):
        flask_app = app_module.create_app()
    else:
        flask_app = app_module.app

    flask_app.config.update(TESTING=True)
    yield flask_app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
