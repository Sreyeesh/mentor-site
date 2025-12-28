.PHONY: help install run freeze test docker-build docker-up docker-dev authoring quick-rebuild clean

DOCKER ?= docker
COMPOSE ?= docker compose

help:
	@echo "Mentor Site workflow targets:"
	@echo "  make install        # Build all Docker images (no local pip install)"
	@echo "  make run            # Run live dev container (visit http://127.0.0.1:5000/)"
	@echo "  make freeze         # Run freeze.py inside the dev container"
	@echo "  make test           # Run pytest suite inside the tests container"
	@echo "  make docker-build   # Build production Docker image"
	@echo "  make docker-up      # Run production-style container on port 3000"
	@echo "  make docker-dev     # Run live-editing dev container on port 5000"
	@echo "  make authoring      # Start authoring tool container on port 5001"
	@echo "  make quick-rebuild  # Rebuild+restart static container helper script"

install:
	$(COMPOSE) build mentor-site mentor-site-dev tests authoring-tool

run:
	$(COMPOSE) --profile dev up mentor-site-dev

freeze:
	$(COMPOSE) run --rm mentor-site-dev python freeze.py

test:
	$(COMPOSE) run --rm tests

docker-build:
	$(DOCKER) build -t mentor-site .

docker-up:
	$(COMPOSE) up --build mentor-site

docker-dev:
	$(COMPOSE) --profile dev up mentor-site-dev

authoring:
	$(COMPOSE) --profile authoring up authoring-tool

quick-rebuild:
	./quick-rebuild.sh

clean:
	rm -rf build .pytest_cache
