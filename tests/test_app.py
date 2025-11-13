import pytest

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
    assert b'break into game development' in response.data.lower()
    assert b'Book a Free 30-Min Strategy Call' in response.data


def test_home_page_content(client):
    """Test that the page contains expected content."""
    response = client.get('/')
    assert b'Who This Is For' in response.data
    assert b'Mentoring Tracks' in response.data
    assert b'FAQ' in response.data


def test_new_pages_load(client):
    """Ensure the new top-level pages render."""
    pages = [
        ('/mentoring/', b'Toucan Creator Mentorship'),
        ('/schools-and-programs/', b'For Schools & Programs'),
        ('/about/', b'Teaching philosophy'),
        ('/contact/', b'Book a free 30-minute strategy call.'),
    ]
    for path, marker in pages:
        response = client.get(path)
        assert response.status_code == 200
        assert marker in response.data


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
