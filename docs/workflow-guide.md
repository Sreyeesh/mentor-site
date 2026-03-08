# Workflow Guide (Dev + Prod)

This guide documents the current setup for branch management, environment files, and CI/CD.

## Current Model

- `master` is the production source of truth.
- CI runs on pull requests, not on normal pushes.
- GitHub Pages deploy runs manually.

## Branch Workflow

Use this flow:

1. Create feature branches from `master`.
2. Open PRs into `master` so CI runs.
3. Merge into `master` when CI passes.

## Environment Separation

- `.env.dev`: local development and test values.
- `.env`: production values.

The app env load order in `app.py` is:

1. `ENV_FILE` (if set)
2. `.env.dev` when `APP_ENV`/`FLASK_ENV` starts with `dev`
3. `.env`
4. `.env.dev` fallback if present

## CI/CD Setup

Workflows:

- `.github/workflows/ci.yml`
  - Triggers: `pull_request` to `master`, plus manual dispatch
  - Runs: `flake8`, `pytest`, `python freeze.py`
- `.github/workflows/deploy-pages.yml`
  - Trigger: manual dispatch only (`workflow_dispatch`)
  - Deploy step runs only for `master`

Required GitHub Actions variables:

- `SITE_URL`
- `BASE_PATH`

## Daily Commands

Local dev:

```bash
docker compose --profile dev up toucan-ee-dev
```

Local static preview:

```bash
docker compose --env-file .env.dev build toucan-ee
docker compose --env-file .env.dev up -d toucan-ee
```

Manual deploy to Pages:

1. Open GitHub Actions.
2. Run `Deploy to GitHub Pages`.
3. Select branch `master`.
