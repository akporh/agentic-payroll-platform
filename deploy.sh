#!/bin/bash
# Usage: ./deploy.sh <droplet-ip>
# Run this from your local machine to deploy/update the app on the Droplet.
# Requires: ssh access to root@<droplet-ip>, Docker + Docker Compose installed on Droplet.

set -e

DROPLET_IP=${1:?Usage: ./deploy.sh <droplet-ip>}
REMOTE="root@$DROPLET_IP"
APP_DIR="/opt/payroll"

echo "==> Pushing latest code to Droplet..."
ssh "$REMOTE" "
  if [ ! -d $APP_DIR ]; then
    git clone https://github.com/akporh/agentic-payroll-platform.git $APP_DIR
  else
    cd $APP_DIR && git pull origin feature/sequential-executor-pension-nhf-fix
  fi
"

echo "==> Ensuring .env exists on Droplet..."
ssh "$REMOTE" "
  if [ ! -f $APP_DIR/.env ]; then
    echo 'ERROR: .env file missing at $APP_DIR/.env'
    echo 'Copy .env.production.example to $APP_DIR/.env and fill in real values.'
    exit 1
  fi
"

echo "==> Building and restarting containers..."
ssh "$REMOTE" "
  cd $APP_DIR
  docker compose pull db  2>/dev/null || true
  docker compose build --no-cache
  docker compose up -d
"

echo "==> Deploy complete. App running at http://$DROPLET_IP"
