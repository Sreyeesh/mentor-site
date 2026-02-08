# Codebase Tour

This document provides a high-level tour of the Mentor Site codebase: the major services, core flows, and where to look when changing behavior.

## Architecture at a Glance

- **Flask site (dev + Stripe endpoints):** dynamic app used for local development and Stripe POST routes. `app.py`
- **Static build (prod):** rendered HTML for static hosting, generated into `build/`. `freeze.py`
- **Authoring tool (CMS):** separate Flask app for editing blog posts and uploading media. `author_app.py`, `authoring_app/`
- **Blog utilities:** Markdown parsing, front-matter handling, excerpts, reading time. `blog/utils.py`
- **SQLite storage:** persists Stripe checkout session status. `db.py`

## Main Site Flow (Development)

- Routes in `app.py` render Jinja templates for the main pages and blog.
- `build_page_context()` prepares nav, canonical URLs, social image, and checkout endpoints.
- Blog list/detail pages call `blog.utils.load_posts()` and render templates.

## Static Build Flow (Production)

- `freeze.py` uses a Flask test client to request each route and write HTML into `build/`.
- Blog post pages are rendered to `build/blog/<slug>/index.html`.
- Static assets are copied into `build/static/`.
- `GITHUB_PAGES_BASE_PATH`/`BASE_PATH` control the URL prefix for subpath hosting.

## Payments / Stripe

- **Subscription checkout:** `POST /stripe/create-checkout-session/` uses Stripe's REST API.
- **One-time checkout:** `POST /create-checkout-session` uses the Stripe SDK.
- `schedule` route verifies payment and controls Calendly visibility; status is stored in SQLite. `db.py`
- If the site is static, `BACKEND_BASE_URL` should point to a live Flask backend for Stripe POSTs.

## Authoring Tool

- Runs under `/authoring/` and reads Markdown from `content/posts/`.
- Supports creating, editing, deleting posts and uploading media to `static/uploads/`.
- Preview uses the same Markdown parsing logic as the site.

## Content Model (Blog)

- Posts live in `content/posts/*.md` with front matter: `title`, `slug`, `date`, and optional `hero_image`.
- `blog/utils.py` generates HTML, excerpts, and reading-time metadata.

## Deployment and CI

- GitHub Actions: lint + tests → `freeze.py` → publish `build/` to GitHub Pages. `.github/workflows/deploy-pages.yml`
- Docker production image builds static HTML and serves it via Nginx. `Dockerfile`
- Docker Compose supports prod static, dev Flask, and authoring profiles. `docker-compose.yml`

## Where to Start

- Page templates: `templates/`
- Static assets: `static/`
- Blog posts: `content/posts/`
- Main routes: `app.py`
- Static build logic: `freeze.py`
- Authoring tool: `authoring_app/`
