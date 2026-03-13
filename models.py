"""SQLAlchemy models for the blog."""
from __future__ import annotations

import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

post_tags = db.Table(
    'post_tags',
    db.Column('post_id', db.String(36), db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
)


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f'<Tag {self.name}>'


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(500), nullable=False)
    slug = db.Column(db.String(500), unique=True, nullable=False)
    date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, default='')
    excerpt = db.Column(db.Text, default='')
    hero_image = db.Column(db.String(500), nullable=True)
    content = db.Column(db.Text, default='')
    featured = db.Column(db.Boolean, default=False, nullable=False)
    published = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    tags = db.relationship('Tag', secondary=post_tags, lazy='joined', backref='posts')

    def __repr__(self) -> str:
        return f'<Post {self.slug}>'
