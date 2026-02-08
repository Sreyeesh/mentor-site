# Mentor Site

A Flask-based mentoring website with two modes of operation:
- Development: a dynamic Flask app for live editing and preview.
- Production: a frozen static build served by GitHub Pages or Nginx.

It also includes a lightweight authoring tool for managing Markdown posts.

## Overview

- Flask app: serves templates, Stripe endpoints, and preview pages during development.
- Static build: `freeze.py` renders the site into `build/` for deployment.
- Authoring tool: a web UI to create and edit Markdown posts in `content/posts/`.
- Payments: optional Stripe checkout and webhook support.
- Backlog doc: `docs/backlog.md`
- Codebase tour: `docs/codebase-tour.md`
- Workflow guide: `docs/workflow-guide.md`

## How It Works

1. `app.py` reads environment variables, builds site config, and serves routes.
2. `freeze.py` uses a Flask test client to render pages into `build/`.
3. GitHub Actions runs CI on pull requests and supports manual Pages deploy from `master`.
4. Stripe POST routes must run on a live Flask backend; static pages call it via `BACKEND_BASE_URL`.

## Project Layout

```
mentor-site/
├── app.py                      # Main Flask app (development + Stripe endpoints)
├── author_app.py               # Authoring tool entry point
├── freeze.py                   # Static site generator
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker services
├── Dockerfile                  # Production container (Nginx + static build)
├── Dockerfile.dev              # Development container
│
├── authoring_app/              # Authoring tool (CMS)
│   ├── views.py                # CRUD routes
│   └── templates/authoring/    # Authoring UI
│
├── blog/                       # Blog utilities
│   └── utils.py                # Post parsing & rendering
│
├── content/posts/              # Markdown blog posts
├── static/                     # CSS, JS, images, uploads
├── templates/                  # Jinja2 templates
├── build/                      # Generated static site
├── tests/                      # Pytest test suite
│
└── .github/workflows/
    ├── ci.yml                  # PR validation (lint, tests, static build check)
    └── deploy-pages.yml        # Manual GitHub Pages deployment
```

## Quick Start (Docker)

```bash
# Clone the repository
git clone <your-repo-url>
cd mentor-site

# Optional: create .env.dev for local development config
# See Environment Configuration below.

# Start the authoring tool
docker compose --profile authoring up authoring-tool
# Open http://localhost:5001/authoring/

# Build and view static site
docker compose up --build mentor-site
# Open http://localhost:3000/
```

## Quick Start (Local Python)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: create .env.dev for local development config
# See Environment Configuration below.

# Run development server
python app.py
# Open http://localhost:5000/
```

## Environment Configuration

The app loads environment variables in this order:

1. `ENV_FILE` if set
2. `.env.dev` if `FLASK_ENV` or `APP_ENV` starts with `dev`
3. `.env`
4. `.env.dev` if it exists

Recommended setup:
- `.env.dev`: local developer defaults
- `.env`: production/CI secrets (do not commit)

Minimal example (placeholders only):

```env
# Site
SITE_NAME=<YOUR_SITE_NAME>
SITE_EMAIL=<YOUR_EMAIL>
SITE_URL=https://your-domain.com
SITE_CALENDLY_LINK=https://calendly.com/your-handle/your-link
BASE_PATH=/mentor-site

# Optional analytics
PLAUSIBLE_SCRIPT_URL=
PLAUSIBLE_DOMAIN=

# Optional Stripe
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_PRICE_ID=
STRIPE_SUCCESS_URL=
STRIPE_CANCEL_URL=
STRIPE_ENDPOINT_SECRET=
BACKEND_BASE_URL=
```

Key variables:

- `BASE_PATH`: URL prefix when hosting under a subdirectory (GitHub Pages often uses `/mentor-site`).
- `BACKEND_BASE_URL`: public host for Stripe POST routes when the frontend is static.
- `AUTHORING_CONTENT_DIR`: override content directory for authoring tool.
- `AUTHORING_MEDIA_URL_PREFIX`: URL prefix for uploaded media (default `/static/uploads`).

## Development Workflows

### Flask dev server

```bash
python app.py
```

Serves the full site at `http://localhost:5000/`.

### Docker dev profile

```bash
docker compose --profile dev up mentor-site-dev
```

Runs the Flask dev server inside the container at `http://localhost:5000/`.

To preview the static/Nginx container with test Stripe links from `.env.dev`:

```bash
docker compose --env-file .env.dev build mentor-site
docker compose --env-file .env.dev up -d mentor-site
```

Without `--env-file .env.dev`, Docker Compose uses `.env` by default.

### Authoring tool

Local Python:
```bash
export AUTHORING_CONTENT_DIR=content/posts   # optional
export AUTHORING_SECRET_KEY=change-me        # optional
python author_app.py
```

Docker:
```bash
docker compose --profile authoring up authoring-tool
```

The UI is available at `http://localhost:5001/authoring/` in Docker.

## Content Workflow

- Create posts in the authoring UI or by adding Markdown files in `content/posts/`.
- Each post requires front matter: `title`, `slug`, and `date`.
- Regenerate the static build after changes:

```bash
python freeze.py
```

## Stripe (Optional)

Stripe is used for hosted checkout and webhooks.

Required for checkout:
- `STRIPE_SECRET_KEY`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_PRICE_ID`
- `STRIPE_SUCCESS_URL`
- `STRIPE_CANCEL_URL`

If the frontend is static (GitHub Pages), set `BACKEND_BASE_URL` so checkout POSTs go to your Flask backend.

## Testing

```bash
pytest
flake8 .
```

Docker tests:
```bash
docker compose run --rm tests
```

## Deployment

### GitHub Pages via Actions

Current workflow setup:

- CI (`.github/workflows/ci.yml`):
  - Runs on pull requests to `dev` and `master`
  - Runs lint, tests, and `python freeze.py`
- Deploy (`.github/workflows/deploy-pages.yml`):
  - Manual trigger only (`workflow_dispatch`)
  - Deploys only when run against `master`

You do not need to commit `build/` to `master` for Actions-based deploys.

### Manual GitHub Pages deploy

`deploy-gh-pages.sh` builds the site locally and pushes `build/` to a Pages branch:

```bash
./deploy-gh-pages.sh
```

It reads `ENV_FILE` (defaults to `.env`) and writes to `gh-pages` unless you override `GITHUB_PAGES_BRANCH`.

### Local production-style container

```bash
./deploy.sh
```

This script builds the production image and serves the static build at `http://localhost:5000/`.
Use `./deploy.sh --with-authoring` to launch the authoring tool alongside it.

## Troubleshooting

- If routes 404 under a subdirectory, set `BASE_PATH=/your-path` and rebuild.
- If Stripe checkout POSTs fail on GitHub Pages, ensure `BACKEND_BASE_URL` points to your Flask backend.
- If the authoring UI can’t save uploads, confirm `static/uploads/` is writable.

## License

This project is private and proprietary. All rights reserved.
