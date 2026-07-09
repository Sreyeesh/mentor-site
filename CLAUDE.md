# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run inside Docker via the Makefile — never use local Python or venv directly.

- `make install` — Build all Docker images
- `make run` — Start dev container with hot reload (http://localhost:5000)
- `make test` — Run pytest suite in Docker
- `make freeze` — Generate static build into `build/`
- `make docker-build` / `make docker-up` — Build/run production container (:3000)
- `make authoring` — Start authoring CMS container (:5001)
- `make deploy` — Freeze and deploy via GitHub Pages
- `make clean` — Remove `build/` and `.pytest_cache`

To run a single test: `docker compose run --rm tests pytest tests/test_app.py::test_name`

To lint: `docker compose --profile ci run --rm tests flake8 .`

## Architecture

Three distinct Flask applications share templates and content:

1. **`app.py`** — Main public site. Routes: `/` (construction dashboard), `/about/`, `/blog/`, `/blog/<slug>/`, `/sitemap.xml`, `/robots.txt`. Flask init, the `icon()` Jinja global, `BUILD_METRICS`, `get_posts()`, and the route views only — config and content live in separate modules (below) and are imported in.

   - **`config.py`** — `SITE_CONFIG` (populated from env vars), `NAV_LINKS`, `SITE_LINKS`, and the `build_absolute_url()` / `build_social_image_url()` / `build_page_context()` helpers. `build_page_context()` assembles the template context for every `render_template` call. `app.py` re-exports `SITE_CONFIG` for `freeze.py`.
   - **`content/`** — page-level content as module-level constants (e.g. `content/construction.py`'s `CONSTRUCTION_PAGE`), passed explicitly to templates — keep content out of templates.

2. **`metrics.py`** — Build-time repo metrics for the construction dashboard (total commits, last commit, weekly commit sparkline). Runs `git` via subprocess; every value degrades to `None` (rendered as "n/a") when git or `.git` is missing. `BUILD_METRICS` is captured once at `app.py` import — on a static site, "telemetry" is whatever was true at build time. **Deploy gotcha:** the Pages workflow must check out with `fetch-depth: 0`, or a shallow clone bakes "total commits: 1".

3. **`freeze.py`** — Static site generator. Uses Flask's test client to render every route to HTML files in `build/`. Requires `SITE_URL` to be set; respects `GITHUB_PAGES_BASE_PATH` for subdirectory deployments. Production serves frozen output via Nginx or GitHub Pages.

4. **`author_app.py`** + **`authoring_app/`** — CMS app (port 5001). Application factory in `authoring_app/__init__.py`. Routes in `authoring_app/views.py` under a Blueprint at `/authoring`. Handles Markdown post creation and media uploads. Not included in the public build.

### Current state: construction page

The homepage (`/`) is a Grafana-style "site in transition" dashboard (`construction.html` + `CONSTRUCTION_PAGE` constant + `metrics.py` data) while the site pivots to a DevOps portfolio. The former CV homepage and mentoring holding page are retired.

### Templates

- Site pages (`about.html`, blog templates) extend `base.html` using `{% block content %}`.
- `construction.html` is a **standalone** page — it does not extend `base.html`, has its own `<head>` (noindex, DM Sans + JetBrains Mono fonts), and uses `static/css/construction.css`.
- No inline JavaScript in templates — all JS lives in `static/js/script.js`.

### CSS Architecture

`static/css/style.css` is the main entry point, importing three files:
- `base.css` — reset, CSS variables (colours, fonts), dark mode tokens, layout, nav, footer
- `components-core.css` — buttons, cards, home page, about page, company logos, contact form
- `components-blog.css` — blog-specific styles

`construction.css` is standalone for the dashboard page. Do not duplicate CSS variables — add shared tokens to `base.css`.

### Blog Engine (`blog/`)

- Posts are Markdown files in `content/posts/` with YAML front matter (`title`, `slug`, `date`, optional `hero_image`)
- `blog/utils.py` handles parsing, rendering (with syntax highlighting), and metadata extraction
- Content directory resolves via: `BLOG_CONTENT_DIR` → `AUTHORING_CONTENT_DIR` → `CONTENT_DIR` env vars → default `content/posts/`
- `content/posts/` is currently empty — the engine works but has no published content yet

### Tests (`tests/`)

- `conftest.py` reloads `app` fresh for each test run to avoid import-order side effects
- Test files map 1:1 to source files: `test_app.py`, `test_authoring_app.py`, `test_blog_utils.py`, `test_freeze_utils.py`, `test_metrics.py`

### Environment

- Copy `.env.example` to `.env.dev` for local dev
- Key vars: `SITE_NAME`, `SITE_EMAIL`, `SITE_URL` (required by `freeze.py`), `SITE_GITHUB_URL`, `SITE_LINKEDIN_URL`, `BASE_PATH`, `GITHUB_PAGES_BASE_PATH`

## Git Commits

Use [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): description`  
Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

Never add `Co-Authored-By` trailers or attribution footers to commits or PR bodies.

## Branching Strategy

- `master` is production — only updated via PR from `dev`; release PRs dev→master use **merge commits, never squash** (keeps histories aligned)
- `dev` is the integration branch — all feature branches merge here
- Branch naming: `type/issue-number-short-description` e.g. `feat/137-email-signup`
- **Never** use auto-generated branch names like `claude/identify-project-bRvHV`

## CI/CD

GitHub Actions runs lint → tests → static build on PRs to `master`.  
Deployment to GitHub Pages is manual (`workflow_dispatch`); the deploy checkout uses `fetch-depth: 0` so baked metrics see full history.  
Workflows: `.github/workflows/ci.yml` and `deploy-pages.yml`.
