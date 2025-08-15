#!/bin/bash

# Create data directories if they don't exist (customer_sync mounted from ~/Workspace/customer_sync)
mkdir -p data/analysis data/repos weekly_report

# Build and run with docker-compose
docker-compose up --build

# Alternative: Run specific script
# docker-compose run --rm work-toolkits python scripts/github/repos_by_query.py

# Interactive mode
# docker-compose run --rm -it work-toolkits bash