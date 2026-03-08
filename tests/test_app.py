from blog import load_posts


def test_home_page(client):
    """Test that the home page loads successfully."""
    response = client.get('/')
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'Full-Stack Developer' in body


def test_home_page_content(client):
    """Test that the page contains expected content."""
    response = client.get('/')
    body = response.get_data(as_text=True)
    assert 'Read the blog' in body
    assert 'Previously worked with' in body


def test_pages_load(client):
    """Ensure top-level pages render."""
    pages = [
        ('/about/', b'full-stack developer'),
        ('/contact/', b'Get in touch'),
    ]
    for path, marker in pages:
        response = client.get(path)
        assert response.status_code == 200
        assert marker in response.data


def test_sitemap_endpoint(client):
    response = client.get('/sitemap.xml')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/xml'
    assert b'<url>' in response.data


def test_robots_endpoint(client):
    response = client.get('/robots.txt')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/plain'
    assert b'Sitemap:' in response.data


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
    assert b'Writing' in response.data


def test_blog_detail(client, tmp_path, monkeypatch):
    post = tmp_path / 'how-i-teach-game-development.md'
    post.write_text(
        "---\n"
        "title: How I Teach Game Development\n"
        "slug: how-i-teach-game-development\n"
        "date: 2024-01-01\n"
        "---\n"
        "\n"
        "Body text.\n"
    )
    monkeypatch.setenv('CONTENT_DIR', str(tmp_path))
    response = client.get('/blog/how-i-teach-game-development/')
    assert response.status_code == 200
    assert b'How I Teach Game Development' in response.data
