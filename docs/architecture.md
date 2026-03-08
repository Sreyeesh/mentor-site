# Architecture & Tech Stack

## Tech Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Language | Python | 3.11 | Runtime |
| Web framework | Flask | 2.3.3 | Routing, templating, dev server |
| Templating | Jinja2 | (Flask built-in) | HTML templates |
| Blog engine | python-frontmatter + markdown | 1.0.0 / 3.5.2 | Parses Markdown posts with YAML front matter |
| Production server | Gunicorn + Nginx | 21.2.0 | WSGI server + static file serving |
| Static site generator | `freeze.py` (custom) | — | Renders all routes to `build/` via Flask test client |
| Testing | pytest + pytest-cov | 7.4.3 / 4.1.0 | Test suite with coverage reporting |
| Linting | flake8 | 6.1.0 | Code style enforcement (max 88 chars) |
| Environment | python-dotenv | 1.0.0 | Loads `.env` / `.env.dev` |
| Containers | Docker + Docker Compose | — | Dev, production, authoring, and test services |
| Analytics | Plausible (optional) | — | Privacy-friendly analytics via `PLAUSIBLE_SCRIPT_URL` |
| CI/CD | GitHub Actions | — | Lint → test → freeze on PRs; manual deploy to Pages |

---

## Three Flask Applications

The project contains three distinct Flask apps that share templates and content:

### 1. Main site — `app.py`

Public-facing site. Routes:

| Route | Purpose |
|-------|---------|
| `/` | Home — developer intro, latest posts |
| `/about/` | Bio and background |
| `/blog/` | Post index |
| `/blog/<slug>/` | Individual post |
| `/contact/` | Contact page |
| `/sitemap.xml` | XML sitemap |
| `/robots.txt` | Robots file |

Site-wide configuration lives in `SITE_CONFIG` at the top of `app.py`. All values are overridable via environment variables.

`BASE_PATH` middleware strips a configurable URL prefix so the app can be hosted under a subdirectory (e.g. GitHub Pages at `/repo-name/`).

`build_page_context()` assembles the common template context: nav links, site config, canonical URL, and social image.

### 2. Static site generator — `freeze.py`

Renders the full site to static HTML for production:

1. Deletes and recreates `build/`
2. Copies `static/` → `build/static/`
3. Uses Flask's test client to GET every route and write the response to `build/<path>/index.html`
4. Iterates over all blog posts and renders each to `build/blog/<slug>/index.html`
5. Writes `build/.nojekyll` (GitHub Pages compatibility)

The output in `build/` is self-contained and deployable to any static host.

### 3. Authoring CMS — `author_app.py` + `authoring_app/`

A separate Flask app on port 5001. Provides a web UI for:
- Creating, editing, and deleting Markdown blog posts
- Uploading media to `static/uploads/`
- Previewing posts using the same Markdown rendering as the main site

Not part of the public site — runs only when explicitly started.

---

## Blog Content Model

Posts are Markdown files in `content/posts/` (directory configurable via `CONTENT_DIR` env var):

```markdown
---
title: Post Title
slug: post-slug
date: 2024-01-15
excerpt: One sentence summary shown in listings.
hero_image: images/my-image.jpg   # optional, relative to static/
---

Post body in Markdown.
Code blocks get syntax highlighting.
```

Parsed by `blog/utils.py` → HTML. Reading time is auto-calculated (word count ÷ 200).

---

## Request Flows

**Development:**
```
Browser
  └─→ Flask app.py :5000
        ├─→ Jinja2 template → HTML response
        └─→ blog/utils.py (for /blog/* routes)
```

**Production:**
```
make freeze
  └─→ freeze.py uses Flask test client
        └─→ Renders all routes → build/

Deploy build/ to static host
  └─→ Nginx (Docker) or GitHub Pages serves static HTML
```

---

## Docker Services

| Service | Port | Dockerfile | Purpose |
|---------|------|-----------|---------|
| `toucan-ee` | 3000 | `Dockerfile` | Nginx serving frozen `build/` |
| `toucan-ee-dev` | 5000 | `Dockerfile.dev` | Flask dev server with hot reload |
| `authoring-tool` | 5001 | `Dockerfile.dev` | Authoring CMS |
| `tests` | — | `Dockerfile.dev` | pytest in isolation |

---

## Project Layout

```
toucan-ee/
├── app.py                    # Main Flask app (public site)
├── author_app.py             # Authoring CMS entry point
├── freeze.py                 # Static site generator
├── requirements.txt          # Python dependencies
├── Makefile                  # Task runner
├── docker-compose.yml        # Service definitions
├── Dockerfile                # Production image (Nginx + static build)
├── Dockerfile.dev            # Dev image (Flask + authoring)
│
├── blog/                     # Blog engine
│   ├── __init__.py           # Exports: load_posts, find_post, normalize_media_path
│   └── utils.py              # Markdown parsing, front-matter, excerpts, reading time
│
├── authoring_app/            # Authoring CMS
│   ├── views.py              # CRUD routes for posts and media
│   └── templates/authoring/  # CMS UI templates
│
├── content/posts/            # Markdown blog posts
├── templates/                # Jinja2 site templates
├── static/                   # CSS, JS, images, uploaded media
├── build/                    # Generated static site (gitignored)
├── tests/                    # pytest test suite
│
└── .github/workflows/
    ├── ci.yml                # PR validation: lint → tests → freeze
    └── deploy-pages.yml      # Manual GitHub Pages deployment
```
