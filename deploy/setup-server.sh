#!/usr/bin/env bash
# One-time EC2 bootstrap — run this ONCE, right after your first SSH login
# to a fresh Ubuntu 24.04 instance. Installs dependencies, clones the repo,
# builds the app, and wires up the systemd service + nginx config.
#
# Edit REPO_URL below before running, then:
#   chmod +x setup-server.sh && ./setup-server.sh

set -euo pipefail

REPO_URL="https://github.com/gordonscarlett-prod/news-analyzer-agent.git"   # <-- EDIT THIS (use a PAT in the URL if the repo is private)
APP_DIR="/opt/news-analyzer"

echo "==> Installing system packages..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip nginx git
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

echo "==> Cloning repo to $APP_DIR..."
sudo mkdir -p "$APP_DIR"
sudo chown "$USER":"$USER" "$APP_DIR"
git clone "$REPO_URL" "$APP_DIR"
cd "$APP_DIR"

echo "==> Setting up backend..."
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
deactivate

if [ ! -f .env ]; then
    cp .env.example .env
    echo "!! Created .env from .env.example — EDIT IT NOW with your real ANTHROPIC_API_KEY, FINNHUB_API_KEY, NEWSAPI_KEY before continuing."
    echo "   Run: nano $APP_DIR/.env"
    read -p "Press Enter once you've saved real keys into .env..."
fi

echo "==> Building frontend..."
cd frontend
npm install
npm run build
cd "$APP_DIR"

echo "==> Installing systemd service..."
sudo cp deploy/news-analyzer-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now news-analyzer-backend

echo "==> Installing nginx config..."
sudo cp deploy/nginx-news-analyzer.conf /etc/nginx/sites-available/news-analyzer
sudo ln -sf /etc/nginx/sites-available/news-analyzer /etc/nginx/sites-enabled/news-analyzer
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

echo "==> Done! Check status:"
echo "    sudo systemctl status news-analyzer-backend"
echo "    curl http://localhost/api/status"
echo "Visit http://<this-instance's-elastic-ip> in a browser."
