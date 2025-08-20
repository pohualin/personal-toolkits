#!/bin/bash
set -e

# Copy secrets to remote host
scp .env_jmusk token.json sheet-token.json jmusk@192.168.2.102:/home/jmusk/Workspace/python/personal-toolkits/

# Build and run Docker Compose on remote host
ssh jmusk@192.168.2.102 "cd /home/jmusk/Workspace/python/personal-toolkits && docker compose build && docker compose up -d"