# Workflow Guide (Dev + Prod)

This guide documents the current setup for branch management, environment files, Stripe config, and CI/CD.

## Current Model

- `master` is the production source of truth.
- `dev` is kept as a mirror of `master` (1:1).
- CI runs on pull requests, not on normal pushes.
- GitHub Pages deploy runs manually.

## Branch Workflow

Use this flow:

1. Create feature branches from `master`.
2. Open PRs into `master` so CI runs.
3. Merge into `master` when CI passes.
4. Sync `dev` from `master` so branches stay identical.

Sync command:

```bash
git push --force-with-lease origin master:dev
```

## Environment Separation

- `.env.dev`: local development and test values (use Stripe test links/keys).
- `.env`: production values (use Stripe live links/keys).

The app env load order in `app.py` is:

1. `ENV_FILE` (if set)
2. `.env.dev` when `APP_ENV`/`FLASK_ENV` starts with `dev`
3. `.env`
4. `.env.dev` fallback if present

## Stripe Setup Notes

- Static pages read `STRIPE_PAYMENT_LINK` from environment during build.
- `docker-compose.yml` now passes Stripe values as build args for `mentor-site`, so `.env` values are available while `freeze.py` renders pages.
- Configure these values in production:
  - `STRIPE_PAYMENT_LINK`
  - `STRIPE_SECRET_KEY` (if API checkout routes are used)
  - `STRIPE_PRICE_ID` (if API checkout routes are used)
  - `STRIPE_SUCCESS_URL`, `STRIPE_CANCEL_URL`, `STRIPE_ENDPOINT_SECRET` as needed

## CI/CD Setup

Workflows:

- `.github/workflows/ci.yml`
  - Triggers: `pull_request` to `dev` and `master`, plus manual dispatch
  - Runs: `flake8`, `pytest`, `python freeze.py`
- `.github/workflows/deploy-pages.yml`
  - Trigger: manual dispatch only (`workflow_dispatch`)
  - Deploy step runs only for `master`

Required GitHub Actions configuration:

- Secrets:
  - `STRIPE_SECRET_KEY`
  - `STRIPE_ENDPOINT_SECRET`
- Variables:
  - `STRIPE_PUBLISHABLE_KEY`
  - `STRIPE_PRICE_ID`
  - `STRIPE_PAYMENT_LINK`
  - `STRIPE_SUCCESS_URL`
  - `STRIPE_CANCEL_URL`
  - `SITE_CALENDLY_LINK`
  - `SITE_URL`
  - `BASE_PATH`

## Daily Commands

Local dev:

```bash
docker compose --profile dev up mentor-site-dev
```

Local static preview with Stripe test link from `.env.dev`:

```bash
docker compose --env-file .env.dev build mentor-site
docker compose --env-file .env.dev up -d mentor-site
```

Note:
- `docker compose up mentor-site` (without `--env-file`) reads `.env` by default.
- Use `--env-file .env.dev` when you want test payment links in the built static output.

Manual deploy to Pages:

1. Open GitHub Actions.
2. Run `Deploy to GitHub Pages`.
3. Select branch `master`.
