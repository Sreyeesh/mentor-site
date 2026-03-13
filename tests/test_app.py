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


def test_markdown_posts_available(app):
    """Ensure the blog loader returns a list (even when no posts exist)."""
    with app.app_context():
        posts = load_posts()
    assert isinstance(posts, list)


def test_blog_index(client):
    response = client.get('/blog/')
    assert response.status_code == 200
    assert b'Writing' in response.data


def test_blog_detail(client, app):
    from datetime import date
    from models import db, Post

    slug = 'how-i-teach-game-development'
    with app.app_context():
        post = Post(
            id='test-blog-detail',
            title='How I Teach Game Development',
            slug=slug,
            date=date(2024, 1, 1),
            content='Body text.',
            published=True,
        )
        db.session.add(post)
        db.session.commit()

    try:
        response = client.get(f'/blog/{slug}/')
        assert response.status_code == 200
        assert b'How I Teach Game Development' in response.data
    finally:
        with app.app_context():
            p = Post.query.filter_by(slug=slug).first()
            if p:
                db.session.delete(p)
                db.session.commit()
