# Toucan.ee — Sreyeesh Garimella

Personal developer portfolio and blog. Built with Flask in development, deployed as a frozen static site.

→ **Architecture & tech stack:** [`docs/architecture.md`](docs/architecture.md)
→ **Makefile reference:** [`docs/MAKEFILE.md`](docs/MAKEFILE.md)

---

## Quick Start

**Docker (recommended):**
```bash
make run
# → http://localhost:5000
```

**Local Python:**
```bash
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

**Other services:**

| Service | Command | URL |
|---------|---------|-----|
| Dev server | `make run` | http://localhost:5000 |
| Authoring CMS | `make authoring` | http://localhost:5001/authoring/ |
| Production preview | `make docker-up` | http://localhost:3000 |

---

## Writing a Blog Post

**Option 1 — Authoring CMS** (`make authoring` → http://localhost:5001/authoring/)

**Option 2 — Markdown file** in `content/posts/`:

```markdown
---
title: My Post Title
slug: my-post-title
date: 2024-01-15
excerpt: One sentence summary shown in the post list.
hero_image: images/my-image.jpg   # optional
---

Post body in Markdown.
```

---

## Build for Production

```bash
make freeze        # renders all routes to build/
make docker-up     # serve build/ with Nginx at :3000
make deploy        # deploy to GitHub Pages
```

---

## Tests & Lint

```bash
make test          # pytest in Docker
pytest             # local
flake8 .           # lint (max 88 chars)
```

---

## Environment

Copy `.env.example` to `.env` (or `.env.dev` for local dev). Key variables:

| Variable | Purpose |
|----------|---------|
| `SITE_NAME` | Your name |
| `SITE_EMAIL` | Contact email |
| `SITE_URL` | Full public URL (for canonical links) |
| `BASE_PATH` | URL prefix for subdirectory hosting (e.g. `/toucan-ee`) |
| `PLAUSIBLE_SCRIPT_URL` | Optional analytics script URL |
| `PLAUSIBLE_DOMAIN` | Optional Plausible domain |

---

## Branching

Trunk-based development — `master` is always releasable. Use short-lived feature branches and merge via PR. Conventional commits required.
