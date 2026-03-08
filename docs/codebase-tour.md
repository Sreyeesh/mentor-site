# Codebase Tour

A quick orientation to the codebase. For full tech stack details see [`architecture.md`](architecture.md).

## Architecture at a Glance

- **Main site (`app.py`):** Flask app serving the public portfolio and blog during development.
- **Static build (`freeze.py`):** renders the full site to `build/` for static hosting.
- **Authoring CMS (`author_app.py`, `authoring_app/`):** separate Flask app for writing and managing blog posts.
- **Blog engine (`blog/utils.py`):** Markdown parsing, front-matter handling, excerpts, reading time.

## Main Site Flow (Development)

- Routes in `app.py` render Jinja2 templates for public pages and blog.
- `build_page_context()` assembles common template data: nav links, site config, canonical URL, social image.
- Blog list and detail routes call `blog.load_posts()` / `blog.find_post()` and pass results to templates.
- `SITE_CONFIG` dict near the top of `app.py` controls name, tagline, email, social image — all overridable via env vars.

## Static Build Flow (Production)

- `freeze.py` uses a Flask test client to request every route and write HTML to `build/`.
- Blog posts are rendered to `build/blog/<slug>/index.html`.
- Static assets are copied to `build/static/`.
- `BASE_PATH` / `GITHUB_PAGES_BASE_PATH` control the URL prefix for subdirectory hosting.

## Authoring Tool

- Runs under `/authoring/` on port 5001.
- Reads and writes Markdown from `content/posts/`.
- Supports creating, editing, deleting posts and uploading media to `static/uploads/`.
- Uses the same Markdown parsing as the main site for previews.

## Content Model (Blog)

- Posts: `content/posts/*.md` with front matter `title`, `slug`, `date`, and optional `hero_image`.
- `blog/utils.py` generates HTML, excerpts, and reading-time metadata.

## Deployment and CI

- GitHub Actions: lint + tests + `freeze.py` on PRs to `master`. Manual deploy to GitHub Pages via `workflow_dispatch`.
- Docker production image builds static HTML and serves it via Nginx (`Dockerfile`).
- Docker Compose defines prod, dev Flask, authoring, and test services (`docker-compose.yml`).

## Where to Start

| What | Where |
|------|-------|
| Page templates | `templates/` |
| Site config (name, tagline, etc.) | `SITE_CONFIG` in `app.py` |
| Routes | `app.py` |
| Blog posts | `content/posts/` |
| Blog parsing logic | `blog/utils.py` |
| Static build logic | `freeze.py` |
| Authoring tool | `authoring_app/` |
| Static assets (CSS, JS) | `static/` |
