.PHONY: help install run freeze test docker-build docker-up docker-dev db-init db-migrate db-upgrade clean down dev-down deploy

DOCKER ?= docker
COMPOSE ?= docker compose

help:
	@echo "Blog workflow targets:"
	@echo "  make install        # Build all Docker images"
	@echo "  make run            # Run live dev container (http://127.0.0.1:5000/)"
	@echo "  make freeze         # Generate static site into build/"
	@echo "  make test           # Run pytest suite"
	@echo "  make docker-build   # Build production Docker image"
	@echo "  make docker-up      # Run production container on port 3000"
	@echo "  make docker-dev     # Run dev container on port 5000"
	@echo "  make db-init        # Initialise Flask-Migrate (first time only)"
	@echo "  make db-migrate     # Generate a new migration"
	@echo "  make db-upgrade     # Apply pending migrations"
	@echo "  make down           # Stop all services"
	@echo "  make dev-down       # Stop only the dev container"
	@echo "  make deploy         # Freeze and deploy to GitHub Pages"

install:
	$(COMPOSE) build toucan-ee-dev tests

run:
	$(COMPOSE) --profile dev up toucan-ee-dev

freeze:
	ENV_FILE=.env $(COMPOSE) --profile dev run --rm toucan-ee-dev python freeze.py

test:
	$(COMPOSE) run --rm tests

docker-build: freeze
	$(DOCKER) build \
		--build-arg BASE_PATH=$$(grep -m1 BASE_PATH .env | cut -d'=' -f2-) \
		-t toucan-ee .

docker-up:
	$(COMPOSE) up --build toucan-ee

docker-dev:
	$(COMPOSE) --profile dev up toucan-ee-dev

db-init:
	$(COMPOSE) --profile dev run --rm toucan-ee-dev flask db init

db-migrate:
	$(COMPOSE) --profile dev run --rm toucan-ee-dev flask db migrate -m "$(msg)"

db-upgrade:
	$(COMPOSE) --profile dev run --rm toucan-ee-dev flask db upgrade

down:
	$(COMPOSE) down

dev-down:
	$(COMPOSE) --profile dev down toucan-ee-dev

deploy: freeze
	ENV_FILE=.env ./deploy-gh-pages.sh

clean:
	rm -rf build .pytest_cache
