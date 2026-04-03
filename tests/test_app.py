from datetime import date

from models import Post, db


def test_home_redirects_to_blog(client):
    """Home page should redirect to /blog/."""
    response = client.get('/')
    assert response.status_code == 301
    assert '/blog/' in response.headers['Location']


def test_blog_index_loads(client):
    response = client.get('/blog/')
    assert response.status_code == 200
    assert b'Writing' in response.data


def test_blog_index_shows_published_posts(client, sample_post, app):
    with app.app_context():
        response = client.get('/blog/')
        assert b'Test Post' in response.data


def test_blog_index_hides_draft_posts(client, app):
    with app.app_context():
        draft = Post(
            title='Draft Post',
            slug='draft-post',
            date=date(2026, 2, 1),
            body='Draft content.',
            draft=True,
        )
        db.session.add(draft)
        db.session.commit()

    response = client.get('/blog/')
    assert b'Draft Post' not in response.data


def test_blog_detail_loads(client, sample_post, app):
    with app.app_context():
        response = client.get('/blog/test-post/')
        assert response.status_code == 200
        assert b'Test Post' in response.data


def test_blog_detail_renders_markdown(client, sample_post, app):
    with app.app_context():
        response = client.get('/blog/test-post/')
        assert b'<h1>' in response.data


def test_blog_detail_draft_returns_404(client, app):
    with app.app_context():
        draft = Post(
            title='Hidden Draft',
            slug='hidden-draft',
            date=date(2026, 3, 1),
            body='Secret.',
            draft=True,
        )
        db.session.add(draft)
        db.session.commit()

    response = client.get('/blog/hidden-draft/')
    assert response.status_code == 404


def test_blog_tag_page(client, sample_post, app):
    with app.app_context():
        response = client.get('/blog/tag/python/')
        assert response.status_code == 200
        assert b'Test Post' in response.data


def test_blog_tag_empty(client, app):
    response = client.get('/blog/tag/nonexistent-tag/')
    assert response.status_code == 200
    assert b'No posts' in response.data


def test_feed_xml(client, sample_post, app):
    with app.app_context():
        response = client.get('/feed.xml')
        assert response.status_code == 200
        assert b'<rss' in response.data
        assert b'Test Post' in response.data


def test_sitemap_endpoint(client):
    response = client.get('/sitemap.xml')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/xml'
    assert b'<url>' in response.data


def test_robots_endpoint(client):
    response = client.get('/robots.txt')
    assert response.status_code == 200
    assert b'Sitemap:' in response.data


def test_static_css(client):
    response = client.get('/static/css/style.css')
    assert response.status_code == 200


def test_404_for_unknown_route(client):
    response = client.get('/does-not-exist/')
    assert response.status_code == 404


def test_about_page_removed(client):
    """The /about/ route no longer exists."""
    response = client.get('/about/')
    assert response.status_code == 404
