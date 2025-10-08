# Mentor Site

Mentor Site is a Flask-based mentoring website that can run dynamically for local development and freeze into a static site for deployment. The repository also bundles a Markdown authoring tool so you can draft and manage blog posts without hand-editing files.

## What's inside
- `app.py` – Flask entry point used during interactive development.
- `freeze.py` – Static site generator that exports `build/` with production-ready HTML.
- `author_app.py` & `authoring_app/` – Flask blueprint and views for the authoring tool.
- `blog/` – Helpers for loading Markdown content and rendering blog posts.
- `content/` – Source Markdown posts; what the authoring tool reads and writes.
- `deploy.sh`, `docker-compose.yml`, `Dockerfile*` – Container workflows for the static site and authoring tool.
- `tests/` – Pytest suite covering the site, blog utilities, and authoring flows.

## Prerequisites
- Python 3.11
- pip (ships with Python)
- Docker and Docker Compose v2 (optional, required for container workflows)
- Git

## Local development (Python)
1. Clone the repository and create a virtual environment:
   ```bash
   git clone <your-repo-url>
   cd mentor-site
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies and create a working `.env`:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   ```
   Update `.env` with site content (name, email, Calendly link, etc.). Leave `BASE_PATH` empty for local development so the app serves from the root (`/`).
3. Run the Flask app:
   ```bash
   python app.py
   ```
   The site is available at `http://localhost:5000/`. If you set `BASE_PATH`, the app will serve from that prefix instead (for example `/mentor-site`).

### Generate the static site
Run the freezer to build production output:
```bash
python freeze.py
```
The generated HTML and assets are written to `build/`. Commit the updated `build/` directory when you want to publish changes (GitHub Pages serves from it).

### Quick rebuild helper
To rebuild and restart the production-style container locally without remembering Docker commands:
```bash
./quick-rebuild.sh
```
The script stops any running containers, rebuilds the static-site image, and brings it up on `http://localhost:3000/`.

## Docker workflows
The repository ships with Compose services for both the static site and the authoring tool.

### Static site via Nginx
```
docker compose up --build mentor-site
```
- Uses the production `Dockerfile` which freezes the site during the image build.
- Serves on `http://localhost:3000/` (mapped to container port 80).
- Stop with `docker compose down`.

### Live-editing profile
If you want to iterate on templates without rebuilding:
```
docker compose --profile dev up mentor-site-dev
```
This mounts the repository into the container and serves the site on `http://localhost:3001/`.

### Authoring tool container
Run the Markdown editor without installing Python locally:
```
docker compose --profile authoring up authoring-tool
```
- Uses `Dockerfile.dev` and launches `python author_app.py` inside the container.
- The UI is available at `http://localhost:5001/authoring/`.
- Content is stored in your local `content/` directory via a bind mount, so edits persist outside the container.

### Combined workflow script
`deploy.sh` wraps these commands, handles port checks, and optionally starts the authoring tool:
```
./deploy.sh          # static site only on http://localhost:5000/
./deploy.sh --with-authoring
./deploy.sh --authoring-port 6001
```
Use this when you want a production-like static container plus the authoring UI in one step.

## Authoring tool (Python)
You can also run the authoring app directly within your virtual environment:
```bash
export AUTHORING_CONTENT_DIR=content/posts   # optional, defaults to this path
export AUTHORING_SECRET_KEY=change-me        # optional
python author_app.py
```
Open `http://localhost:5000/authoring/` to create, edit, preview, or delete Markdown posts. Files are stored under `content/posts/` using the slug as the filename.

## Content workflow
- Draft posts in the authoring UI or add Markdown files under `content/posts/` manually. Each file needs front matter (`title`, `slug`, `date`).
- Run `python freeze.py` (or rebuild the Docker image) after content or template changes to refresh `build/`.
- Commit both the Markdown source and the regenerated `build/` output.

## Testing and quality checks
All tests use Pytest:
```bash
pytest
pytest -k authoring        # run only the authoring tool tests
```
Linting is configured with Flake8:
```bash
flake8 .
```
Add new tests alongside existing modules under `tests/` when you change behaviour.

## Environment variables
The `.env.example` file documents every supported key. Common ones are listed below:

| Variable | Purpose | Default |
| --- | --- | --- |
| `SITE_NAME` | Display name used across templates | `Sreyeesh Garimella` |
| `SITE_EMAIL` | Contact email surfaced on the site | `toucan.sg@gmail.com` |
| `SITE_CALENDLY_LINK` | Calendly CTA URL | `https://calendly.com/toucan-sg/60min` |
| `SITE_META_DESCRIPTION` | SEO description injected into templates | preset marketing copy |
| `SITE_FOCUS_AREAS` | Comma-separated list rendered as focus areas | preset sample values |
| `BASE_PATH` | Optional URL prefix when hosting under a subdirectory | empty |
| `AUTHORING_CONTENT_DIR` | Filesystem path that stores Markdown posts | `content/posts` |
| `AUTHORING_SECRET_KEY` | Flask secret key for the authoring app | `authoring-dev-secret` |
| `GISCUS_*` | Settings for the Giscus comments widget | see `.env.example` |

Set environment variables in `.env` for direct Flask runs or export them before launching Docker containers as needed.

## Repository structure
```
.
├── app.py
├── author_app.py
├── authoring_app/
│   ├── __init__.py
│   ├── templates/
│   └── views.py
├── blog/
│   ├── __init__.py
│   └── utils.py
├── content/
│   └── posts/
├── docker-compose.yml
├── deploy.sh
├── freeze.py
├── quick-rebuild.sh
├── requirements.txt
├── static/
│   ├── css/
│   ├── images/
│   └── js/
├── templates/
│   ├── blog/
│   └── index.html
└── tests/
    ├── conftest.py
    ├── test_app.py
    ├── test_authoring_app.py
    ├── test_blog_utils.py
    └── test_freeze_utils.py
```

## Deployment
- `deploy.sh` builds and runs the static site locally using Docker (and can include the authoring tool).
- `.github/workflows/deploy-pages.yml` publishes the static `build/` directory to GitHub Pages when `master` is updated.
- You can host the `build/` directory on any static file host (S3, Netlify, GitHub Pages, etc.).

## License
This project is private and proprietary. All rights reserved.
