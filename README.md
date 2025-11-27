# Mentor Site

A professional Flask-based mentoring website with hybrid architecture: dynamic development mode for live editing and static site generation for fast, secure production hosting. Includes a built-in content management system (CMS) for creating and managing blog posts without manual file editing.

## 🌟 Features

- **Hybrid Architecture**: Dynamic Flask app for development, frozen static HTML for production
- **Built-in CMS**: Web-based authoring tool for blog post management
- **Markdown Content**: Write in Markdown with YAML front matter
- **Media Management**: Upload and manage images, videos, and audio files
- **Static Site Generation**: One-command freeze to production-ready HTML
- **Docker Support**: Complete containerized workflows for development and deployment
- **CI/CD Ready**: GitHub Actions pipeline for automated deployment
- **SEO Optimized**: Meta descriptions, canonical URLs, and social sharing support

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (optional, for containerized workflows)
- Git

### Fastest Start (Docker)

```bash
# Clone the repository
git clone <your-repo-url>
cd mentor-site

# Copy environment template
cp .env.example .env

# Start the authoring tool
docker-compose --profile authoring up authoring-tool
# Open http://localhost:5001/authoring/ to create content

# Build and view static site
docker-compose up --build mentor-site
# Open http://localhost:3000/
```

### Local Python Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run development server
python app.py
# Open http://localhost:5000/
```

## 📋 Table of Contents

- [Project Structure](#-project-structure)
- [Development Workflows](#-development-workflows)
- [Authoring Tool Guide](#-authoring-tool-guide)
- [Static Site Generation](#-static-site-generation)
- [Docker Workflows](#-docker-workflows)
- [Testing](#-testing)
- [Environment Configuration](#-environment-configuration)
- [Deployment](#-deployment)
- [Content Management](#-content-management)

## 📁 Project Structure

```
.
├── app.py                     # Flask application entry point
├── deploy.sh                  # Local deployment script
├── docker-compose.yml         # Docker Compose setup
├── Dockerfile                 # Docker configuration
├── .env                       # Environment variables (local)
├── .env.example              # Environment variables template
├── .flake8                    # Flake8 configuration
├── freeze.py                  # Static site generator
├── .github/
│   └── workflows/
│       └── deploy-pages.yml   # GitHub Actions deployment
├── .gitignore                 # Git ignore rules
├── pytest.ini                # Pytest configuration
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css         # Main stylesheet
│   ├── images/
│   │   ├── GameCity.png      # Game development image
│   │   └── SreyeeshProfilePic.jpg  # Profile image
│   └── js/
│       └── script.js         # JavaScript functionality
├── templates/
│   └── index.html            # Main site template
└── tests/
    └── test_app.py           # Test suite

9 directories, 19 files
```

## 🛠️ Development

### Environment Setup
Create a `.env` file for local development:
```env
SITE_NAME=Sreyeesh Garimella
SITE_EMAIL=toucan.sg@gmail.com
SITE_CALENDLY_LINK=https://calendly.com/toucan-sg/consulting-link
SITE_URL=https://your-domain.com
BASE_PATH=/mentor-site
FLASK_DEBUG=True
```

`SITE_URL` should be the fully qualified domain for the deployed site (for example,
`https://mentor.yourdomain.com`). It is used to build canonical URLs and social
share links so networks like LinkedIn and X always receive a complete link to
your posts.

### Running Tests
```bash
pytest
```

### Code Quality
```bash
# Linting
flake8 .

# Type checking (if using mypy)
mypy .
```

### Static Site Generation
```bash
# Generate static files
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

### Run tests in Docker
Execute the test suite in an isolated container:
```
docker compose run --rm tests
```
The command uses the same image as the development container, mounts your working copy, installs dependencies from the image layer, and runs `pytest`.

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
| `SITE_CALENDLY_LINK` | Calendly CTA URL | `https://calendly.com/toucan-sg/consulting-link` |
| `SITE_META_DESCRIPTION` | SEO description injected into templates | preset marketing copy |
| `SITE_FOCUS_AREAS` | Comma-separated list rendered as focus areas | preset sample values |
| `BASE_PATH` | Optional URL prefix when hosting under a subdirectory | empty |
| `AUTHORING_CONTENT_DIR` | Filesystem path that stores Markdown posts | `content/posts` |
| `AUTHORING_SECRET_KEY` | Flask secret key for the authoring app | `authoring-dev-secret` |

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
