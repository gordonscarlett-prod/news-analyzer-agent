#!/usr/bin/env bash
# Redeploy helper — run this ON THE EC2 INSTANCE after the initial setup
# (setup-server.sh) has been done once. Pulls the latest code, reinstalls
# deps if they changed, rebuilds the frontend, and restarts the backend.
#
# Usage: cd /opt/news-analyzer && ./deploy/deploy.sh

set -euo pipefail

APP_DIR="/opt/news-analyzer"
cd "$APP_DIR"

echo "==> Pulling latest code..."
git pull

echo "==> Updating backend dependencies..."
source backend/venv/bin/activate
pip install -q -r backend/requirements.txt
deactivate

echo "==> Rebuilding frontend..."
cd frontend
npm install --silent
npm run build
cd "$APP_DIR"

echo "==> Restarting backend service..."
sudo systemctl restart news-analyzer-backend

echo "==> Reloading nginx..."
sudo nginx -t && sudo systemctl reload nginx

echo "==> Done. Check status with: sudo systemctl status news-analyzer-backend"
