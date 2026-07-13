from blog import load_posts


def test_home_page(client):
    """Home page serves the site transition placeholder."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Site in transition' in response.data
    assert b'Changing' in response.data
    assert b'direction.' in response.data


def test_home_page_is_construction_placeholder(client):
    """The homepage is the pivot placeholder, not mentoring or the CV."""
    body = client.get('/').data
    assert b'Site in transition' in body
    assert b'<img' not in body
    assert body.count(b'mailto:') == 1
    assert b'Open to DevOps and platform work.' in body
    assert b'<built-in method copy' not in body
    # It must not be the old mentoring waitlist or CV/portfolio homepage.
    assert b'1-on-1 Mentoring' not in body
    assert b'waitlist' not in body
    assert b'Selected credits' not in body


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
