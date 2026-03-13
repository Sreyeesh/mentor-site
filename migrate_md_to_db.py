"""One-time migration: import Markdown files from content/posts/ into the DB.

Usage:
    python migrate_md_to_db.py

Run this once after switching to the database backend. Safe to run multiple
times — posts with an existing slug are skipped.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import frontmatter

from app import app
from models import db, Post, Tag


def slugify(value: str) -> str:
    slug = value.strip().lower()
    slug = ''.join(
        char if char.isalnum() or char in {'-', ' '} else ' '
        for char in slug
    )
    return '-'.join(filter(None, slug.split()))


def migrate() -> None:
    content_dir = Path('content/posts')
    if not content_dir.exists():
        print("No content/posts directory found — nothing to migrate.")
        return

    md_files = list(content_dir.glob('*.md'))
    if not md_files:
        print("No .md files found — nothing to migrate.")
        return

    with app.app_context():
        db.create_all()
        imported = 0
        skipped = 0

        for path in sorted(md_files):
            try:
                data = frontmatter.load(path)
                meta = data.metadata
                slug = meta.get('slug') or path.stem

                if Post.query.filter_by(slug=slug).first():
                    print(f"  ⏭  Skipped (already exists): {slug}")
                    skipped += 1
                    continue

                raw_date = meta.get('date')
                if isinstance(raw_date, datetime):
                    post_date = raw_date.date()
                elif raw_date:
                    from datetime import date
                    try:
                        post_date = date.fromisoformat(str(raw_date))
                    except ValueError:
                        post_date = None
                else:
                    post_date = None

                raw_tags = meta.get('tags', [])
                if isinstance(raw_tags, str):
                    tag_names = [t.strip() for t in raw_tags.split(',') if t.strip()]
                else:
                    tag_names = [str(t).strip() for t in raw_tags if str(t).strip()]

                tags = []
                for name in tag_names:
                    tag = Tag.query.filter_by(name=name).first()
                    if not tag:
                        tag = Tag(name=name)
                        db.session.add(tag)
                    tags.append(tag)

                post = Post(
                    id=meta.get('id') or None,
                    title=meta.get('title', path.stem),
                    slug=slug,
                    date=post_date,
                    description=meta.get('description', ''),
                    excerpt=meta.get('excerpt', ''),
                    hero_image=meta.get('hero_image') or None,
                    content=data.content,
                    featured=bool(meta.get('featured', False)),
                    published=bool(meta.get('published', True)),
                )
                post.tags = tags
                db.session.add(post)
                db.session.commit()
                print(f"  ✅ Imported: {slug}")
                imported += 1

            except Exception as exc:
                print(f"  ❌ Failed {path.name}: {exc}")
                db.session.rollback()

        print(f"\nDone. {imported} imported, {skipped} skipped.")


if __name__ == '__main__':
    migrate()
