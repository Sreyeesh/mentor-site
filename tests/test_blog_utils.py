from __future__ import annotations

from datetime import date

import pytest

from authoring_app import create_app
from blog import load_posts
from models import db, Post


@pytest.fixture()
def app(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{tmp_path}/test.db')
    a = create_app()
    with a.app_context():
        yield a


def test_load_posts_returns_published_posts(app):
    post = Post(
        id='test-1',
        title='Sample',
        slug='sample',
        date=date(2024, 5, 1),
        content='Hello world',
        published=True,
    )
    db.session.add(post)
    db.session.commit()

    posts = load_posts()
    assert len(posts) == 1
    assert posts[0]['slug'] == 'sample'


def test_load_posts_excludes_unpublished(app):
    post = Post(
        id='draft-1',
        title='Draft',
        slug='draft',
        date=date(2024, 5, 1),
        content='Draft content',
        published=False,
    )
    db.session.add(post)
    db.session.commit()

    posts = load_posts()
    assert len(posts) == 0
