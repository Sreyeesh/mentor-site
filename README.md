# Toucan.ee — Sreyeesh Garimella

DevOps/cloud portfolio and blog for Sreyeesh Garimella. Built with Flask in development, deployed as a frozen static site. The homepage is currently a Grafana-style "under construction" dashboard while the site is rebuilt around infrastructure and ops work.

→ **Architecture & tech stack:** [`docs/architecture.md`](docs/architecture.md)
→ **Makefile reference:** [`docs/MAKEFILE.md`](docs/MAKEFILE.md)

---

## Quick Start

All commands run inside Docker via the Makefile — never use local Python or a venv directly.

```bash
make run
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
make test                                          # pytest in Docker
docker compose --profile ci run --rm tests flake8 .   # lint (max 88 chars)
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

---

## Branching

Trunk-based development with short-lived branches:

- **`master`** — production; only updated via release PR from `dev` (merge commit, never squash).
- **`dev`** — integration branch; all feature branches merge here.
- **Feature branches** — branch off `dev`, named `type/issue-number-short-description` (e.g. `docs/317-update-readme`).

[Conventional commits](https://www.conventionalcommits.org/) required (`type(scope): description`).
