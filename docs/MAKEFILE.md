## Makefile workflow

This project ships with a Makefile that wraps the most common Docker Compose commands so you don’t need to remember long CLI flags. From the repo root, run `make help` to see a quick summary:

```
$ make help
Mentor Site workflow targets:
  make install        # Build all Docker images (no local pip install)
  make run            # Run live dev container (visit http://127.0.0.1:5000/)
  make freeze         # Run python freeze.py inside the dev container
  make test           # Run pytest suite inside the tests container
  make docker-build   # Build production Docker image (runs freeze first)
  make docker-up      # Run production-style container on port 3000
  make docker-dev     # Run live-editing dev container on port 5000
  make authoring      # Start authoring tool container on port 5001
  make down           # Run 'docker compose down' for all services
  make dev-down       # Stop only the mentor-site-dev container
  make quick-rebuild  # Rebuild+restart static container helper script
```

### Target reference

| Target          | Command run under the hood | When to use it |
|-----------------|----------------------------|----------------|
| `make install`  | `docker compose build mentor-site mentor-site-dev tests authoring-tool` | Build all container images so subsequent runs start instantly. No local pip install needed. |
| `make run` / `make docker-dev` | `docker compose --profile dev up mentor-site-dev` | Launch the Flask dev server with live reload on port 5000. Uses `.env.dev` by default. |
| `make freeze`   | `docker compose --profile dev run --rm mentor-site-dev python freeze.py` | Generate the static site inside the dev container. Automatically runs before `make docker-build`. |
| `make test`     | `docker compose run --rm tests` | Execute the Pytest suite inside the dedicated test container. |
| `make docker-build` | `docker build -t mentor-site .` (after `make freeze`) | Create the production image. Runs `freeze.py` beforehand to ensure `build/` is current. |
| `make docker-up` | `docker compose up --build mentor-site` | Run the production-style nginx container locally on port 3000. Good for staging/testing the static build. |
| `make authoring` | `docker compose --profile authoring up authoring-tool` | Start the CMS/authoring tool on port 5001 to edit blog posts via the UI. |
| `make down`     | `docker compose down` | Stop every running service defined in `docker-compose.yml`. |
| `make dev-down` | `docker compose --profile dev down mentor-site-dev` | Stop just the dev server while leaving other profiles untouched. |
| `make quick-rebuild` | `./quick-rebuild.sh` | Helper script that rebuilds the static container quickly (provided separately). |
| `make clean`    | `rm -rf build .pytest_cache` | Remove generated static files and pytest cache. |

### Tips
1. **Auto-freeze on builds**: You rarely need to call `make freeze` manually—`make docker-build` already depends on it and will refresh `build/` automatically.
2. **Profiles keep things isolated**: Dev (`--profile dev`) and authoring (`--profile authoring`) containers stay separate. Use `make authoring` to run the CMS alongside the dev server if needed.
3. **Hot reload**: The `mentor-site-dev` service mounts the repo and uses Flask’s debug reload, so saving local files reloads the app instantly.
4. **Environment files**: `.env` holds production values; `.env.dev` contains local/test defaults and is consumed automatically by the dev container. Update `.env.dev` for local experiments.

Feel free to extend the Makefile with additional shortcuts if your workflow grows—just keep each target mapped to a single Compose action so teammates can reason about it quickly.
