import pytest

import app as app_module
from app import app
from blog import load_posts


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    """Test that the home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Sreyeesh Garimella' in response.data
    assert b'Mentoring' in response.data


def test_home_page_content(client):
    """Test that the page contains expected content."""
    response = client.get('/')
    assert b'Get Free 30-Min Strategy Call' in response.data
    assert b'Services' in response.data
    assert b'Contact' in response.data


def test_static_files(client):
    """Test that static files are accessible."""
    response = client.get('/static/css/style.css')
    assert response.status_code == 200


def test_404_page(client):
    """Test that 404 pages are handled properly."""
    response = client.get('/nonexistent-page')
    assert response.status_code == 404


def test_markdown_posts_available():
    """Ensure the blog loader returns a list (even when no posts exist)."""
    posts = load_posts()
    assert isinstance(posts, list)


def test_blog_index(client):
    response = client.get('/blog/')
    assert response.status_code == 200
    assert b'Your creative career playbook' in response.data


def test_blog_detail(client):
    response = client.get('/blog/how-i-teach-game-development/')
    assert response.status_code == 200
    assert b'How I Teach Game Development' in response.data


def test_blog_detail_comments_placeholder(client):
    response = client.get('/blog/how-i-teach-game-development/')
    assert b'Join the discussion' in response.data
    assert b'giscus-placeholder' in response.data


def test_blog_detail_giscus_embed(monkeypatch, client):
    monkeypatch.setitem(
        app_module.SITE_CONFIG,
        'giscus',
        {
            'repo': 'octocat/example',
            'repo_id': 'R_123',
            'category': 'Announcements',
            'category_id': 'DIC_456',
            'mapping': 'pathname',
            'strict': '1',
            'reactions_enabled': '1',
            'emit_metadata': '0',
            'input_position': 'bottom',
            'lang': 'en',
            'theme_light': 'light',
            'theme_dark': 'dark',
            'loading': 'lazy',
            'enabled': True,
        },
    )

    response = client.get('/blog/how-i-teach-game-development/')
    assert b'https://giscus.app/client.js' in response.data
    assert b'const config =' in response.data
