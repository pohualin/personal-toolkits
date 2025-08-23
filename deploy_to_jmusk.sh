#!/bin/bash
set -e

echo "Checklist before deployment:"
echo ==============================
echo "1. Ensure .env_jmusk, token.json, and sheet-token.json are up to date."
echo "2. Check for any uncommitted changes in your local repository."
echo "3. ssh jmusk@192.168.2.102"
echo "4. cd Workspace/python/personal-toolkits/ && git pull"
echo ==============================

read -p "Proceed with deployment? (y/n): " confirm
if [[ "$confirm" != "y" ]]; then
    echo "Deployment aborted."
    exit 1
fi

# Copy secrets to remote host
scp \
  .env_jmusk \
  token.json \
  sheet-token.json \
  jmusk@192.168.2.102:/home/jmusk/Workspace/python/personal-toolkits/

# Build and run Docker Compose on remote host
ssh jmusk@192.168.2.102 \
  "cd /home/jmusk/Workspace/python/personal-toolkits \
    && docker compose build \
    && docker compose up -d"