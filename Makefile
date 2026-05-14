.PHONY: help install run freeze test docker-build docker-up docker-dev authoring quick-rebuild clean down dev-down deploy

DOCKER ?= docker
COMPOSE ?= docker compose

help:
	@echo "Toucan.ee workflow targets:"
	@echo "  make install        # Build all Docker images (no local pip install)"
	@echo "  make run            # Run live dev container (visit http://127.0.0.1:5000/)"
	@echo "  make freeze         # Run python freeze.py inside the dev container"
	@echo "  make test           # Run pytest suite inside the tests container"
	@echo "  make docker-build   # Build production Docker image (runs freeze first)"
	@echo "  make docker-up      # Run production-style container on port 3000"
	@echo "  make docker-dev     # Run live-editing dev container on port 5000"
	@echo "  make authoring      # Start authoring tool container on port 5001"
	@echo "  make down           # Run 'docker compose down' for all services"
	@echo "  make dev-down       # Stop only the toucan-ee-dev container"
	@echo "  make quick-rebuild  # Rebuild+restart static container helper script"
	@echo "  make deploy         # Freeze and deploy static site via deploy-gh-pages.sh"

install:
	$(COMPOSE) build toucan-ee toucan-ee-dev tests authoring-tool

run:
	$(COMPOSE) --profile dev up toucan-ee-dev

freeze:
	$(COMPOSE) --env-file .env --profile dev run --rm toucan-ee-dev python freeze.py

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

authoring:
	$(COMPOSE) --profile authoring up authoring-tool

down:
	$(COMPOSE) down

dev-down:
	$(COMPOSE) --profile dev down toucan-ee-dev

quick-rebuild:
	./quick-rebuild.sh

deploy: freeze
	ENV_FILE=.env ./deploy-gh-pages.sh

clean:
	rm -rf build .pytest_cache
