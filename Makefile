.PHONY: help install run freeze test docker-build docker-up docker-dev authoring quick-rebuild clean down dev-down

DOCKER ?= docker
COMPOSE ?= docker compose

help:
	@echo "Mentor Site workflow targets:"
	@echo "  make install        # Build all Docker images (no local pip install)"
	@echo "  make run            # Run live dev container (visit http://127.0.0.1:5000/)"
	@echo "  make freeze         # Run python freeze.py inside the dev container"
	@echo "  make test           # Run pytest suite inside the tests container"
	@echo "  make docker-build   # Build production Docker image (runs freeze first)"
	@echo "  make docker-up      # Run production-style container on port 3000"
	@echo "  make docker-dev     # Run live-editing dev container on port 5000"
	@echo "  make authoring      # Start authoring tool container on port 5001"
	@echo "  make down           # Run 'docker compose down' for all services"
	@echo "  make dev-down       # Stop only the mentor-site-dev container"
	@echo "  make quick-rebuild  # Rebuild+restart static container helper script"

install:
	$(COMPOSE) build mentor-site mentor-site-dev tests authoring-tool

run:
	$(COMPOSE) --profile dev up mentor-site-dev

freeze:
	$(COMPOSE) --profile dev run --rm mentor-site-dev python freeze.py

test:
	$(COMPOSE) run --rm tests

docker-build: freeze
	$(DOCKER) build \
		--build-arg BASE_PATH=$$(grep -m1 BASE_PATH .env | cut -d'=' -f2-) \
		--build-arg STRIPE_SECRET_KEY=$$(grep -m1 STRIPE_SECRET_KEY .env | cut -d'=' -f2-) \
		--build-arg STRIPE_PUBLISHABLE_KEY=$$(grep -m1 STRIPE_PUBLISHABLE_KEY .env | cut -d'=' -f2-) \
		--build-arg STRIPE_PRICE_ID=$$(grep -m1 STRIPE_PRICE_ID .env | cut -d'=' -f2-) \
		--build-arg STRIPE_PAYMENT_LINK=$$(grep -m1 STRIPE_PAYMENT_LINK .env | cut -d'=' -f2-) \
		--build-arg STRIPE_SUCCESS_URL=$$(grep -m1 STRIPE_SUCCESS_URL .env | cut -d'=' -f2-) \
		--build-arg STRIPE_CANCEL_URL=$$(grep -m1 STRIPE_CANCEL_URL .env | cut -d'=' -f2-) \
		--build-arg STRIPE_ENDPOINT_SECRET=$$(grep -m1 STRIPE_ENDPOINT_SECRET .env | cut -d'=' -f2-) \
		-t mentor-site .

docker-up:
	$(COMPOSE) up --build mentor-site

docker-dev:
	$(COMPOSE) --profile dev up mentor-site-dev

authoring:
	$(COMPOSE) --profile authoring up authoring-tool

down:
	$(COMPOSE) down

dev-down:
	$(COMPOSE) --profile dev down mentor-site-dev

quick-rebuild:
	./quick-rebuild.sh

clean:
	rm -rf build .pytest_cache
