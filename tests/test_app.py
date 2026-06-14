from blog import load_posts


def test_home_page(client):
    """Home page serves the Toucan Studios holding page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Toucan Studios' in response.data


def test_home_page_is_holding_page(client):
    """During the build period the homepage is the holding page, not the CV."""
    response = client.get('/')
    body = response.data
    assert b'Launching soon' in body
    assert b'game dev' in body
    assert b'1-on-1 Mentoring' in body
    # The CV must no longer be live on the homepage.
    assert b'Sreyeesh Garimella' not in body
    assert b'DNEG' not in body


def test_home_page_has_og_image(client):
    """og:image meta tag must resolve to a non-empty absolute URL."""
    response = client.get('/')
    html = response.data.decode()
    import re
    match = re.search(
        r'<meta property="og:image" content="([^"]*)"', html
    )
    assert match is not None, 'og:image meta tag missing'
    url = match.group(1)
    assert url, 'og:image content is empty'
    assert url.startswith(('http://', 'https://')), (
        f'og:image must be absolute, got: {url}'
    )


def test_pages_load(client):
    """Blog index renders the post list."""
    response = client.get('/blog/')
    assert response.status_code == 200


def test_about_page_uses_cv_bio(client):
    response = client.get('/about/')
    assert response.status_code == 200
    assert b'Pipeline TD and software developer' in response.data
    assert b'DNEG' in response.data
    assert b'Book a session' not in response.data


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
    assert b'Sreyeesh Garimella' in response.data


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
