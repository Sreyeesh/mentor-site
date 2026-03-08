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
- `make deploy` — Deploy via GitHub Pages

**Without Docker:**
- `python app.py` — Dev server (Flask :5000)
- `pytest` — Run tests (with coverage)
- `pytest tests/test_foo.py::test_bar` — Run single test
- `flake8 .` — Lint (max 88 chars, excludes .git/__pycache__/.venv)
- `python freeze.py` — Build static site

## Architecture

The project has three distinct Flask applications that share templates and content:

1. **`app.py`** — Main site. Serves all public routes (home, about, blog, contact). Static site config lives in `SITE_CONFIG` dict near the top.

2. **`freeze.py`** — Static site generator. Uses Flask's test client to render every route to HTML files in `build/`. Production deploys are this frozen output served by Nginx or GitHub Pages.

3. **`author_app.py`** + **`authoring_app/views.py`** — Separate CMS app (port 5001 in Docker). Provides a web UI for creating/editing Markdown blog posts and uploading media. Not part of the public site.

### Blog Engine (`blog/`)
- Posts live as Markdown files in `content/posts/` with YAML front matter (`title`, `slug`, `date`, optional `hero_image`)
- `blog/utils.py` handles parsing, metadata extraction, and rendering (with syntax highlighting and safe HTML)
- Content directory is configurable via env vars

### Environment
- Copy `.env.example` to `.env` (or `.env.dev` for dev mode)
- `FLASK_ENV`/`APP_ENV` controls which env file loads
- Key vars: `BASE_PATH` (for subdirectory deployments), `PLAUSIBLE_SCRIPT_URL` (optional analytics)

## Git Commits
Use [Conventional Commits](https://www.conventionalcommits.org/): `type(scope): description`
Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Branching Strategy
This project uses **trunk-based development**:
- `master` is the trunk — always kept releasable
- Work in short-lived feature branches, merge to `master` via PR as soon as possible
- Branches should be small and focused; avoid long-running branches
- Feature flags preferred over long-lived feature branches

## CI/CD
- GitHub Actions runs lint → tests → static build check on PRs to `master`
- Deployment to GitHub Pages is manual (`workflow_dispatch` only)
- Workflows in `.github/workflows/ci.yml` and `deploy-pages.yml`
