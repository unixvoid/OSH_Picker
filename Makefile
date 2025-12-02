.PHONY: help build run clean local dev

# Variables
IMAGE_NAME := osh-picker
IMAGE_TAG := latest
REGISTRY := 
BUILD_DIR := stage.tmp
DOCKERFILE := Dockerfile
DOCKER_ARGS := sudo

# Targets
help:
	@echo "Available targets:"
	@echo "  make dev         - Run Flask directly (port 5001)"
	@echo "  make build       - Build the Docker image"
	@echo "  make run         - Run the Docker container at port 5000"
	@echo "  make clean       - Clean up build artifacts and containers"

dev:
	@echo "Starting Flask development server on port 5001"
	PORT=5001 python3 app.py

build: clean
	@mkdir -p $(BUILD_DIR)
	@echo "Building Docker image: $(IMAGE_NAME):$(IMAGE_TAG)"
	$(DOCKER_ARGS) docker build \
		-f $(DOCKERFILE) \
		-t $(IMAGE_NAME):$(IMAGE_TAG) \
		-t $(IMAGE_NAME):latest \
		--progress=plain \
		--no-cache \
		.
	@echo "Build complete!"
	@$(DOCKER_ARGS) docker images | grep $(IMAGE_NAME)

run:
	@echo "Starting container: $(IMAGE_NAME):$(IMAGE_TAG) on port 5000"
	$(DOCKER_ARGS) docker run -d \
		-p 5000:5000 \
		--restart unless-stopped \
		--name osh-picker \
		$(IMAGE_NAME):$(IMAGE_TAG)

clean:
	@echo "Cleaning up..."
	@docker ps -a | grep osh-picker-container && docker rm -f osh-picker-container || true
	@rm -rf $(BUILD_DIR)
	@echo "Cleanup complete!"

.DEFAULT_GOAL := help
