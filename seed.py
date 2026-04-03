"""Seed the database with initial blog content.

Run once: python seed.py
"""
from datetime import date

from app import app
from models import Post, db

FIRST_POST = Post(
    title="Hello — I'm a Senior Full-Stack Developer and Mentor",
    slug="hello-im-a-senior-fullstack-developer-and-mentor",
    date=date(2026, 4, 3),
    description=(
        "An introduction to who I am, what I build, and why I started writing here."
    ),
    tags="intro, mentoring, software",
    featured=True,
    draft=False,
    body="""\
## Who I am

I'm Sreyeesh Garimella — a senior full-stack developer with over a decade of \
experience building production software across games, animation pipelines, and \
web applications.

I've worked at studios like DNEG, Walt Disney Animation, and Blizzard Entertainment, \
where I shipped tools and systems used by hundreds of artists and engineers daily.

## What I do

I build things end-to-end — from database schemas and REST APIs to front-end \
interfaces and deployment pipelines. My stack of choice is Python on the backend \
and modern JavaScript on the front end, though I'm comfortable reaching for \
whatever the problem demands.

I also mentor engineers — from junior developers learning their first framework \
to experienced engineers who want to level up their architecture instincts or \
move into technical leadership.

## Why this blog

I started writing here because I believe the craft of software development is \
best learned by watching someone work through real problems — not polished \
tutorials, but honest process logs.

Expect posts about:

- Technical deep-dives into tools I'm building
- Lessons from shipping software at scale
- Career advice for developers at all levels
- Notes on mentoring and teaching engineering

## Get in touch

If you'd like to work together or talk about mentoring, reach out at \
[toucan.sg@gmail.com](mailto:toucan.sg@gmail.com).
""",
)


def seed():
    with app.app_context():
        existing = Post.query.filter_by(slug=FIRST_POST.slug).first()
        if existing:
            print(f"Post '{FIRST_POST.slug}' already exists — skipping.")
            return
        db.session.add(FIRST_POST)
        db.session.commit()
        print(f"✅ Seeded post: '{FIRST_POST.title}'")


if __name__ == '__main__':
    seed()
