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

## 🗒️ Tomorrow's TODOs

- [ ] Fix link descriptions across the site so previews read clearly.
- [ ] Revisit the landing page layout to resolve the remaining design issues.
- [ ] Refresh the mentoring/tutoring page design for consistency.
- [ ] Update the About page design to match the new aesthetic.

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
mentor-site/
├── app.py                      # Main Flask app (development)
├── author_app.py              # Authoring tool entry point
├── freeze.py                  # Static site generator
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Docker services
├── Dockerfile                 # Production container
├── Dockerfile.dev             # Development container
│
├── authoring_app/             # Blog CMS
│   ├── views.py              # CRUD routes
│   └── templates/authoring/  # CMS UI
│
├── blog/                      # Blog utilities
│   └── utils.py              # Post parsing & rendering
│
├── content/posts/             # Markdown blog posts
├── static/                    # CSS, JS, images, uploads
├── templates/                 # Jinja2 templates
├── build/                     # Generated static site
├── tests/                     # Pytest test suite
│
└── .github/workflows/
    └── deploy-pages.yml       # CI/CD pipeline
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
PLAUSIBLE_SCRIPT_URL=https://plausible.io/js/your-site.js
PLAUSIBLE_DOMAIN=mentor.your-domain.com
STRIPE_SECRET_KEY=sk_test_yourkey
STRIPE_PUBLISHABLE_KEY=pk_test_yourkey
STRIPE_PRICE_ID=price_yourplan
STRIPE_SUCCESS_URL=https://your-domain.com/mentoring/?checkout=success
STRIPE_CANCEL_URL=https://your-domain.com/mentoring/?checkout=cancelled
```

`SITE_URL` should be the fully qualified domain for the deployed site (for example,
`https://mentor.yourdomain.com`). It is used to build canonical URLs and social
share links so networks like LinkedIn and X always receive a complete link to
your posts.

`PLAUSIBLE_SCRIPT_URL` is optional. When it is set, the base template injects the
Plausible analytics loader plus the initialization snippet so you can enable
privacy-friendly tracking without editing templates. Set `PLAUSIBLE_DOMAIN` to
the exact domain you registered with Plausible so the script includes the
required `data-domain` attribute for automatic detection.

`STRIPE_*` values are optional but power the hosted Checkout button on the mentoring
page. Define them when you are ready to accept subscription payments. The success
and cancel URLs must be fully qualified links that Stripe can redirect to. Set
`BACKEND_BASE_URL` to the public host of your live Flask API (for example,
`https://api.your-domain.com`) so static checkout forms submit to the backend.
Leave it empty in local development to keep posting to the same origin.

#### Local vs. production env files

- `.env` — production/CI secrets. Keep this file out of version control.
- `.env.dev` — developer-friendly defaults (Stripe test mode, localhost URLs, etc.). Set
  `ENV_FILE=.env.dev` or `FLASK_ENV=development` before running `flask run` so the app loads
  this file automatically. The Docker `dev` profile already exports `ENV_FILE=.env.dev`, so
  `docker compose --profile dev up mentor-site-dev` uses the test configuration out of the box.

Switch environments by exporting a different `ENV_FILE` value:

```bash
# Local hacking
ENV_FILE=.env.dev flask run

# Production parity build
ENV_FILE=.env python freeze.py
```

#### Deploying to GitHub Pages

Use the helper script to regenerate the static build and push it to your Pages branch:

```bash
# Builds with ENV_FILE=.env and pushes build/ to gh-pages
./deploy-gh-pages.sh

# Target a different branch or env file
ENV_FILE=.env.prod GITHUB_PAGES_BRANCH=production-pages ./deploy-gh-pages.sh
```

The script runs `python freeze.py`, syncs `build/` into a temporary worktree for the target branch,
commits, and pushes to `origin`. Ensure you have access to the remote and that the branch exists
(the script can create it locally if missing but still expects it on the remote).
If you prefer to drop in the Plausible snippet manually, add this block inside
`<head>` of `templates/base.html`:

```html
<!-- Privacy-friendly analytics by Plausible -->
<script async src="https://plausible.io/js/pa-Koa-AcVzVzVMrXEYD5VkD.js"></script>
<script>
  window.plausible = window.plausible || function () {
    (plausible.q = plausible.q || []).push(arguments);
  };
  plausible.init = plausible.init || function (options) {
    plausible.o = options || {};
  };
  plausible.init();
</script>
```

### SEO Essentials

- `sitemap.xml` is generated dynamically from every static page and published blog
  post. Visit `http://localhost:5000/sitemap.xml` (or your deployed URL) to
  confirm the XML output before submitting it to search engines.
- `robots.txt` is also served automatically at `/robots.txt` with a pointer to
  the sitemap. Run `curl http://localhost:5000/robots.txt` to double-check the
  contents in development.
- To connect Google Search Console: add your verified domain (recommended),
  upload the provided DNS TXT record at your registrar, then submit the sitemap
  URL (`https://your-domain.com/sitemap.xml`) once verification succeeds.
- The frontend uses a responsive layout with lightweight CSS/JS; keep static
  assets optimized (images in `static/`) to maintain fast load times on mobile
  devices.

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

> **Heads-up:** The containers read `BASE_PATH` from your environment (defaults to `/mentor-site` which matches GitHub Pages). Export `BASE_PATH=/` before running Compose if you want the app served from the root locally.

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
This mounts the repository into the container and now serves the site on `http://127.0.0.1:5000/` by default (the dev service sets `BASE_PATH=/`). Thanks to the bind mount and Flask’s debug reloader, code and template edits reflect instantly without rebuilding the image. If you need to test a different base path, export `BASE_PATH=/your-path` before launching.

### Authoring tool container
Run the Markdown editor without installing Python locally:
```
docker compose --profile authoring up authoring-tool
```
- Uses `Dockerfile.dev` and launches `python author_app.py` inside the container.
- The UI is available at `http://localhost:5001/authoring/`.
- Content is stored in your local `content/` directory via a bind mount, so edits persist outside the container.
- Uploaded media land in `static/uploads/` on your machine, making it easy to reference `/static/uploads/...` paths in posts and commit the assets alongside Markdown.

### Stripe subscriptions (optional)
Add a hosted Stripe Checkout button on `/mentoring/`:

1. Create a recurring product/price in Stripe and note the **price ID**.
2. Populate `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_PRICE_ID`, `STRIPE_SUCCESS_URL`, and `STRIPE_CANCEL_URL` in `.env`.
3. Restart the Flask server (or rebuild the Docker containers) so the new environment variables load.

When those variables are set, visitors see a simple form that posts to `/stripe/create-checkout-session/`. The Flask route creates a Checkout Session, redirects the visitor to Stripe, and then returns them to the URLs you supplied after they confirm or cancel payment. The same endpoint also accepts JSON if you need to trigger Checkout from custom JavaScript.

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
| `BACKEND_BASE_URL` | Fully qualified host for live API endpoints | _(empty => same origin)_ |
| `AUTHORING_CONTENT_DIR` | Filesystem path that stores Markdown posts | `content/posts` |
| `AUTHORING_SECRET_KEY` | Flask secret key for the authoring app | `authoring-dev-secret` |

Set environment variables in `.env` for direct Flask runs or export them before launching Docker containers as needed.

## 🚀 Deployment

This site is deployed to **GitHub Pages** using an automated CI/CD pipeline.

### How it works

1. **Local development**: Make changes using the authoring tool or by editing files directly
2. **Generate static site**: Run `python freeze.py` to build the `build/` directory
3. **Commit changes**: Commit both your source changes and the updated `build/` directory
4. **Push to master**: `git push origin master`
5. **Automatic deployment**: GitHub Actions automatically deploys the `build/` directory to GitHub Pages

### GitHub Actions workflow

The `.github/workflows/deploy-pages.yml` pipeline:
- Runs linting with flake8
- Runs the test suite with pytest
- Generates the static site with `freeze.py`
- Deploys the `build/` directory to GitHub Pages

### Local testing with deploy.sh

Test the production static site locally before deploying:

```bash
./deploy.sh                    # Static site only on http://localhost:5000/
./deploy.sh --with-authoring   # Includes authoring tool
```

### Backend API for Stripe checkout

GitHub Pages only serves static HTML, so Stripe’s POST routes must be hosted on
a separate backend. Deploy `app.py` to a platform that can run Flask (Render,
Railway, Fly.io, a VPS, etc.):

1. Build from `Dockerfile.dev` or run `gunicorn app:app` on your platform.
2. Set environment variables on that service: `BASE_PATH=/mentor-site`,
   `SITE_URL`, `STRIPE_*` keys, `STRIPE_ENDPOINT_SECRET`, etc.
3. Assign a public hostname such as `https://api.toucan.ee`.
4. Add that hostname as `BACKEND_BASE_URL` in GitHub Actions secrets (along with
   your live `STRIPE_*` values).
5. Push to `master` so GitHub Pages rebuilds the static site; the templates now
   POST directly to the backend host, avoiding 405 errors on Pages.

This split keeps GitHub Pages fast while the hosted Flask app powers Stripe
Checkout and webhook endpoints.

### Stripe checkout workflow (local → master → live)

1. **Local sanity checks** – Copy `.env.example` to `.env`, fill in every `STRIPE_*` value, and point `BACKEND_BASE_URL` to your local server (for example `http://localhost:5000`). Run `flask run` and hit any checkout form; it should redirect to Stripe or return JSON when you `POST` via curl. Run `pytest tests/test_checkout_flow.py` for an automated check.
2. **Master / CI builds** – The GitHub Actions workflow reads the same variables from repository secrets. Ensure `BACKEND_BASE_URL` matches your deployed backend host so generated HTML keeps POSTing to Flask instead of GitHub Pages (otherwise you will see 405 errors). The workflow already runs the checkout tests, so a failing Stripe configuration blocks merges.
3. **Live verification** – After Pages finishes publishing, use the live site with Stripe test cards to confirm subscriptions and one-off payments both reach the backend. Because the HTML contains the fully qualified backend URLs, live testing is the only remaining step to guarantee parity with master.

Following this path means every environment (local, master, and live) exercises the same Flask routes, Stripe keys, and redirect URLs before customers ever see the page.

## License
This project is private and proprietary. All rights reserved.
