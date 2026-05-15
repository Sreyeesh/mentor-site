# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run inside Docker via the Makefile — never use local Python or venv directly.

**Exception — Claude Code on the web:** Docker is not available in remote cloud sessions. Use `pytest` and `flake8` directly instead (dependencies are pre-installed by the SessionStart hook in `.claude/hooks/session-start.sh`).

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

1. **`app.py`** — Main public site. Routes: `/`, `/coming-soon/`, `/about/`, `/blog/<slug>/`, `/sitemap.xml`, `/robots.txt`. Site-wide config lives in `SITE_CONFIG` near the top, populated from env vars. `build_page_context()` assembles the template context for every `render_template` call. Page-level content data (`ABOUT_EXPERIENCE`, `COMING_SOON_TOPICS`) is defined as module-level constants and passed explicitly to templates — keep content out of templates.

2. **`freeze.py`** — Static site generator. Uses Flask's test client to render every route to HTML files in `build/`. Respects `GITHUB_PAGES_BASE_PATH` env var for subdirectory deployments. Production serves frozen output via Nginx or GitHub Pages.

3. **`author_app.py`** + **`authoring_app/`** — CMS app (port 5001). Application factory in `authoring_app/__init__.py`. Routes in `authoring_app/views.py` under a Blueprint at `/authoring`. Handles Markdown post creation and media uploads. Not included in the public build.

### Templates

- Most pages extend `base.html` using `{% block content %}`.
- `coming-soon-full.html` is a **standalone** page — it does not extend `base.html` and has its own CSS (`static/css/coming-soon.css`).
- No inline JavaScript in templates — all JS lives in `static/js/script.js`.

### CSS Architecture

`static/css/style.css` is the main entry point, importing three files:
- `base.css` — reset, CSS variables (colours, fonts), dark mode tokens, layout, nav, footer
- `components-core.css` — buttons, cards, home page, about page, company logos, contact form
- `components-blog.css` — blog-specific styles

`coming-soon.css` imports `base.css` directly and adds only page-specific styles. Do not duplicate CSS variables — add shared tokens to `base.css`.

### Blog Engine (`blog/`)

- Posts are Markdown files in `content/posts/` with YAML front matter (`title`, `slug`, `date`, optional `hero_image`)
- `blog/utils.py` handles parsing, rendering (with syntax highlighting), and metadata extraction
- Content directory resolves via: `BLOG_CONTENT_DIR` → `AUTHORING_CONTENT_DIR` → `CONTENT_DIR` env vars → default `content/posts/`

### Tests (`tests/`)

- `conftest.py` reloads `app` fresh for each test run to avoid import-order side effects
- Test files map 1:1 to source files: `test_app.py`, `test_authoring_app.py`, `test_blog_utils.py`, `test_freeze_utils.py`

### Environment

- Copy `.env.example` to `.env.dev` for local dev
- Key vars: `SITE_NAME`, `SITE_EMAIL`, `SITE_LOCATION`, `SITE_GITHUB_URL`, `SITE_LINKEDIN_URL`, `BASE_PATH`, `GITHUB_PAGES_BASE_PATH`, `PLAUSIBLE_SCRIPT_URL`

## Git Commits

Use [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): description`  
Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Branching Strategy

- `master` is production — only updated via PR from `dev`
- `dev` is the integration branch — all feature branches merge here
- Branch naming: `type/issue-number-short-description` e.g. `feat/137-email-signup`
- **Never** use auto-generated branch names like `claude/identify-project-bRvHV`

## CI/CD

GitHub Actions runs lint → tests → static build on PRs to `master`.  
Deployment to GitHub Pages is manual (`workflow_dispatch`).  
Workflows: `.github/workflows/ci.yml` and `deploy-pages.yml`.
