# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Primary interface via Makefile:**
- `make install` — Build dev and test Docker images
- `make run` — Run dev container (Flask on :5000 with hot reload)
- `make test` — Run pytest suite in Docker
- `make freeze` — Generate static build into `build/`
- `make docker-build` / `make docker-up` — Build/run production container (:3000)
- `make db-init` — Initialise Flask-Migrate (first time only)
- `make db-migrate msg="description"` — Generate a new migration
- `make db-upgrade` — Apply pending migrations
- `make deploy` — Freeze and deploy via GitHub Pages

**Without Docker:**
- `python app.py` — Dev server (Flask :5000); creates `instance/blog.db` on first run
- `python seed.py` — Insert the starter blog post (safe to re-run; skips if already exists)
- `python -m pytest` — Run tests (use `python -m pytest`, not bare `pytest`, to use the correct Python env)
- `python -m pytest tests/test_foo.py::test_bar` — Run a single test
- `flake8 .` — Lint (max 88 chars)
- `python freeze.py` — Build static site

## Architecture

The project is a **blog-only Flask site** backed by SQLite, deployed as a frozen static site.

### Three entry points

1. **`app.py`** — Public site. All routes live here. `SITE_CONFIG` dict near the top controls site name, tagline, email, and SEO defaults.

2. **`freeze.py`** — Static site generator. Uses Flask's test client to render every route to HTML in `build/`. The deployed site (GitHub Pages / Nginx) serves only this frozen output — no database or Python at runtime.

3. **`seed.py`** — One-time DB seeder. Inserts the initial "Hello, I'm a senior full-stack developer and mentor" post. Safe to re-run.

### Data layer

- **`models.py`** — Single `Post` model (SQLAlchemy). Tags stored as a comma-separated string in `Post.tags`. Computed properties (`rendered_body`, `reading_time`, `computed_excerpt`, `date_display`, `tag_list()`) live on the model and call into `blog/utils.py`.
- **`admin.py`** — Flask-Admin wired to `Post`. Accessible at `/admin/`. Draft posts (`Post.draft = True`) are hidden from all public routes.
- **`instance/blog.db`** — SQLite database. Created automatically on first `python app.py` run. Not used in production (freeze renders everything ahead of time).
- **`migrations/`** — Alembic migrations managed via Flask-Migrate.

### Blog rendering (`blog/utils.py`)

Thin module — no DB access. Provides:
- `render_body(markdown_text)` → HTML (used by `Post.rendered_body`)
- `reading_time(text)` → int minutes
- `auto_excerpt(text, words=50)` → str
- `normalize_media_path(value)` → `(path, is_external)` tuple — strips `static/` prefix, passes through external URLs unchanged

### Routes

| Route | Notes |
|---|---|
| `GET /` | 301 redirect to `/blog/` |
| `GET /blog/` | Paginated post list (`POSTS_PER_PAGE = 10`) |
| `GET /blog/page/<n>/` | Paginated blog (canonical route for freeze) |
| `GET /blog/<slug>/` | Post detail; 404 for draft posts |
| `GET /blog/tag/<tag>/` | Posts filtered by tag |
| `GET /feed.xml` | RSS 2.0 feed (latest 20 published posts) |
| `GET /sitemap.xml` | XML sitemap including tag pages |
| `GET /robots.txt` | Robots file |
| `GET /admin/` | Flask-Admin (dev only — not frozen) |

### freeze.py behaviour

Queries the DB directly (inside `app.app_context()`) to enumerate all slugs, tags, and page counts before rendering. Renders home redirect, all blog pages, tag pages, feed, sitemap, and robots. Copies `static/` verbatim into `build/static/`.

### Environment

- Copy `.env.example` to `.env.dev` for local dev
- Key vars: `SECRET_KEY`, `DATABASE_URL` (defaults to `sqlite:///blog.db`), `SITE_URL` (must be set to production domain for correct canonical URLs and OG tags), `BASE_PATH` (subdirectory deployments)
- `APP_ENV=development` triggers `.env.dev` loading

## Git Commits
Use [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): description`
Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Branching Strategy
- `master` is the trunk — always kept releasable
- Feature branches → merge to `dev` for testing → merge to `master`
- Keep branches small and focused

## CI/CD
- GitHub Actions: lint → tests → static build check on PRs to `master`
- Deployment to GitHub Pages is manual (`workflow_dispatch` only)
- Workflows in `.github/workflows/ci.yml` and `deploy-pages.yml`
