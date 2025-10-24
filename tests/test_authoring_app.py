import io

import pytest

from authoring_app import create_app


@pytest.fixture()
def authoring_client(tmp_path, monkeypatch):
    monkeypatch.setenv('AUTHORING_CONTENT_DIR', str(tmp_path))
    monkeypatch.setenv('AUTHORING_SECRET_KEY', 'test-secret')
    monkeypatch.setenv('AUTHORING_MEDIA_DIR', str(tmp_path / 'uploads'))
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_dashboard_loads(authoring_client):
    response = authoring_client.get('/authoring/')
    assert response.status_code == 200
    assert b'Blog Authoring Tool' in response.data


def test_create_post_writes_markdown(authoring_client, tmp_path):
    payload = {
        'title': 'My First Post',
        'slug': 'my-first-post',
        'date': '2024-01-01',
        'description': 'desc',
        'excerpt': 'excerpt',
        'hero_image': '',
        'content': '# Heading',
        'featured': 'on',
    }
    response = authoring_client.post(
        '/authoring/posts/new',
        data=payload,
        follow_redirects=True,
    )
    assert response.status_code == 200
    saved_file = tmp_path / 'my-first-post.md'
    assert saved_file.exists()
    content = saved_file.read_text(encoding='utf-8')
    assert 'title: My First Post' in content
    assert 'slug: my-first-post' in content
    assert '# Heading' in content
    assert 'tags:' not in content


def test_upload_media_saves_file(authoring_client, tmp_path):
    upload_path = tmp_path / 'uploads'
    assert not any(upload_path.iterdir()) if upload_path.exists() else True

    response = authoring_client.post(
        '/authoring/uploads',
        data={
            'media_file': (io.BytesIO(b'fake image data'), 'photo.jpg'),
            'next': '/authoring/posts/new',
        },
        content_type='multipart/form-data',
        follow_redirects=False,
    )

    assert response.status_code == 302

    saved_file = upload_path / 'photo.jpg'
    assert saved_file.exists()
    assert saved_file.read_bytes() == b'fake image data'
