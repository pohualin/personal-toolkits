#!/bin/bash
set -e

# Build the Docker image
docker compose build

# Run the container
docker compose up -d

# Show running containers
# docker compose ps

# Show logs
# docker compose logs -f