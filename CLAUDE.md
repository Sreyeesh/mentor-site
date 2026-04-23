# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Primary interface via Makefile:**
- `make install` — Build all Docker images
- `make run` — Run dev container (Flask on :5000 with hot reload)
- `make test` — Run pytest suite in Docker
- `make freeze` — Generate static build into `build/`
- `make docker-build` / `make docker-up` — Build/run production container (:3000)
- `make authoring` — Start authoring CMS container (:5001)
- `make deploy` — Freeze and deploy via GitHub Pages (`deploy-gh-pages.sh`)
- `make clean` — Remove `build/` and `.pytest_cache`

**Without Docker:**
- `python app.py` — Dev server (Flask :5000)
- `pytest` — Run tests (with coverage)
- `pytest tests/test_foo.py::test_bar` — Run single test
- `flake8 .` — Lint (max 88 chars, excludes .git/__pycache__/.venv)
- `python freeze.py` — Build static site

## Architecture

Three distinct Flask applications share templates and content:

1. **`app.py`** — Main public site. Routes: `/`, `/blog/`, `/blog/<slug>/`, `/sitemap.xml`, `/robots.txt`. Site-wide config lives in the `SITE_CONFIG` dict near the top, populated from env vars. `build_page_context()` assembles the template context passed to every `render_template` call. Posts are loaded once per request via Flask's `g` object.

2. **`freeze.py`** — Static site generator. Uses Flask's test client to render every route to HTML files in `build/`. Respects `GITHUB_PAGES_BASE_PATH` env var (distinct from `BASE_PATH`) to rewrite paths for subdirectory deployments. Production deploys serve this frozen output via Nginx or GitHub Pages.

3. **`author_app.py`** + **`authoring_app/`** — CMS app (port 5001). Uses an application factory (`create_app()` in `authoring_app/__init__.py`). Routes are in `authoring_app/views.py` under a Blueprint at `/authoring`. Handles Markdown post creation/editing and media uploads. Not part of the public site build.

### Blog Engine (`blog/`)
- Posts live as Markdown files in `content/posts/` with YAML front matter (`title`, `slug`, `date`, optional `hero_image`)
- `blog/utils.py` handles parsing, metadata extraction, and rendering (with syntax highlighting and safe HTML)
- Content directory resolves via: `BLOG_CONTENT_DIR` → `AUTHORING_CONTENT_DIR` → `CONTENT_DIR` env vars → default `content/posts/`

### Tests (`tests/`)
- `conftest.py` reloads the `app` module fresh for each test run to avoid import-order side effects — keep this in mind when writing fixtures that patch module-level state
- Test files map roughly 1:1 to source files: `test_app.py`, `test_authoring_app.py`, `test_blog_utils.py`, `test_freeze_utils.py`

### Environment
- Copy `.env.example` to `.env` (or `.env.dev` for dev mode)
- `FLASK_ENV`/`APP_ENV` controls which env file loads
- Key vars: `BASE_PATH` (subdirectory deployments), `GITHUB_PAGES_BASE_PATH` (static build path rewriting), `PLAUSIBLE_SCRIPT_URL` / `PLAUSIBLE_DOMAIN` (optional analytics)

## Git Commits
Use [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): description`
Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Branching Strategy
This project uses **Git Flow**:
- `master` is production — only updated via PR from `dev`
- `dev` is the integration branch — all feature branches merge here via PR
- Branch off `dev` for all work: `git checkout dev && git checkout -b feat/my-feature`
- Keep branches small and focused; merge back to `dev` quickly

**Branch naming convention:** `type/issue-number-short-description`
- Type matches Conventional Commits: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`
- Issue number ties the branch to a GitHub issue
- Examples: `feat/137-email-signup`, `fix/142-freeze-redirect`, `chore/150-cleanup-deps`

## CI/CD
- GitHub Actions runs lint → tests → static build check on PRs to `master`
- Deployment to GitHub Pages is manual (`workflow_dispatch` only)
- Workflows in `.github/workflows/ci.yml` and `deploy-pages.yml`
