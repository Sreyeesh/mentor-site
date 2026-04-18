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
	@echo "  make deploy         # Deploy to GitHub Pages"

install:
	$(COMPOSE) build mentor-site-dev tests

run:
	$(COMPOSE) --profile dev up mentor-site-dev

freeze:
	ENV_FILE=.env $(COMPOSE) --profile dev run --rm mentor-site-dev python freeze.py

test:
	$(COMPOSE) run --rm tests

docker-build:
	$(DOCKER) build -t mentor-site .

docker-up:
	$(COMPOSE) up --build mentor-site

docker-dev:
	$(COMPOSE) --profile dev up mentor-site-dev

db-init:
	$(COMPOSE) --profile dev run --rm mentor-site-dev flask db init

db-migrate:
	$(COMPOSE) --profile dev run --rm mentor-site-dev flask db migrate -m "$(msg)"

db-upgrade:
	$(COMPOSE) --profile dev run --rm mentor-site-dev flask db upgrade

down:
	$(COMPOSE) down

dev-down:
	$(COMPOSE) --profile dev down mentor-site-dev

deploy:
	gh workflow run deploy-pages.yml

clean:
	rm -rf build .pytest_cache
