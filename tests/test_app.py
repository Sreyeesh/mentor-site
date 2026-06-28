from blog import load_posts


def test_home_page(client):
    """Home page serves the 'under construction' placeholder."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Under construction' in response.data


def test_subscribe_stores_email(client, tmp_path, monkeypatch):
    """A valid email is appended to the subscribers file with a timestamp."""
    subs = tmp_path / 'subscribers.csv'
    monkeypatch.setenv('SUBSCRIBERS_FILE', str(subs))

    response = client.post(
        '/subscribe', data={'email': 'Dev@Studio.com', 'consent': 'yes'}
    )

    assert response.status_code == 302
    assert 'subscribed=ok' in response.headers['Location']
    assert subs.exists()
    stored = subs.read_text()
    assert 'dev@studio.com' in stored  # normalised to lowercase
    assert 'consent' in stored  # consent recorded with the signup

    # Personal data file must be owner read/write only (rw-------).
    import stat
    assert stat.S_IMODE(subs.stat().st_mode) == 0o600


def test_subscribe_requires_consent(client, tmp_path, monkeypatch):
    """A valid email without consent is rejected and nothing is written."""
    subs = tmp_path / 'subscribers.csv'
    monkeypatch.setenv('SUBSCRIBERS_FILE', str(subs))

    response = client.post('/subscribe', data={'email': 'dev@studio.com'})

    assert response.status_code == 302
    assert 'subscribed=invalid' in response.headers['Location']
    assert not subs.exists()


def test_subscribe_rejects_invalid_email(client, tmp_path, monkeypatch):
    """An invalid email is rejected and nothing is written."""
    subs = tmp_path / 'subscribers.csv'
    monkeypatch.setenv('SUBSCRIBERS_FILE', str(subs))

    response = client.post(
        '/subscribe', data={'email': 'not-an-email', 'consent': 'yes'}
    )

    assert response.status_code == 302
    assert 'subscribed=invalid' in response.headers['Location']
    assert not subs.exists()


def test_subscribe_defangs_csv_formula_injection(client, tmp_path, monkeypatch):
    """An email starting with a formula char is stored as text, not a formula."""
    subs = tmp_path / 'subscribers.csv'
    monkeypatch.setenv('SUBSCRIBERS_FILE', str(subs))

    # '=cmd@x.co' passes the shape check but is a spreadsheet-injection payload.
    response = client.post(
        '/subscribe', data={'email': '=cmd@x.co', 'consent': 'yes'}
    )

    assert response.status_code == 302
    assert 'subscribed=ok' in response.headers['Location']
    stored = subs.read_text()
    assert "'=cmd@x.co" in stored  # quote-prefixed so it is treated as text
    assert ',=cmd@x.co' not in stored  # never written as a bare formula


def test_subscribe_rejects_overlong_email(client, tmp_path, monkeypatch):
    """An address past the RFC length cap is rejected and nothing is written."""
    subs = tmp_path / 'subscribers.csv'
    monkeypatch.setenv('SUBSCRIBERS_FILE', str(subs))

    huge = ('a' * 250) + '@x.co'  # > 254 chars
    response = client.post(
        '/subscribe', data={'email': huge, 'consent': 'yes'}
    )

    assert response.status_code == 302
    assert 'subscribed=invalid' in response.headers['Location']
    assert not subs.exists()


def test_privacy_page_renders(client):
    """The privacy notice page is served and covers consent + rights."""
    response = client.get('/privacy/')
    assert response.status_code == 200
    body = response.data
    assert b'privacy notice' in body.lower()
    assert b'consent' in body.lower()
    assert b'Formspree' in body


def test_home_page_is_construction_placeholder(client):
    """The homepage is the neutral placeholder, not mentoring or the CV."""
    body = client.get('/').data
    assert b'Under construction' in body
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
