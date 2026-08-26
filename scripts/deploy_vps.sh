#!/bin/bash
# ==============================================================================
# ENNOVERA PL + FPL — VPS AUTOMATED DEPLOYMENT SCRIPT (PORT 8001)
# Target Host: 72.62.35.32
# Service: ennovera-pl.service (Runs on internal port 8001; WC2026 preserved on 8000)
# ==============================================================================

set -e

echo "=================================================================="
echo "DEPLOYING ENNOVERA PL + FPL FASTAPI SERVING LAYER (COMMIT 6963f31)"
echo "=================================================================="

# 1. Navigate to repository directory
REPO_DIR="/var/www/ennovera-pl"
if [ ! -d "$REPO_DIR" ]; then
    REPO_DIR="$(pwd)"
fi
cd "$REPO_DIR"

echo "[1/6] Pulling verified production commit from GitHub..."
git fetch origin main
git checkout main
git pull origin main
DEPLOYED_COMMIT=$(git rev-parse HEAD)
echo "Verified Git Commit: $DEPLOYED_COMMIT"

# 2. Set up Python virtual environment
echo "[2/6] Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# 3. Install required production dependencies
echo "[3/6] Installing dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn pydantic scipy numpy pandas scikit-learn httpx

# 4. Create systemd unit file
echo "[4/6] Creating /etc/systemd/system/ennovera-pl.service..."
cat <<EOF | sudo tee /etc/systemd/system/ennovera-pl.service
[Unit]
Description=Ennovera Premier League and FPL FastAPI Serving Application
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$REPO_DIR
ExecStart=$REPO_DIR/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 2
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# 5. Reload & restart systemd service
echo "[5/6] Starting ennovera-pl systemd service on port 8001..."
sudo systemctl daemon-reload
sudo systemctl enable ennovera-pl
sudo systemctl restart ennovera-pl
sleep 3
sudo systemctl status ennovera-pl --no-pager

# 6. Verify Nginx Reverse Proxy Configuration
echo "[6/6] Configuring Nginx reverse proxy routes..."
NGINX_CONF="/etc/nginx/sites-available/default"
if [ -f "$NGINX_CONF" ]; then
    if ! grep -q "api/v1/pl" "$NGINX_CONF"; then
        sudo cp "$NGINX_CONF" "${NGINX_CONF}.backup_$(date +%Y%m%d_%H%M%S)"
        echo "Adding PL/FPL proxy blocks to Nginx..."
        sudo sed -i '/server {/a \
    location /api/v1/pl/ {\
        proxy_pass http://127.0.0.1:8001/api/v1/pl/;\
        proxy_set_header Host $host;\
        proxy_set_header X-Real-IP $remote_addr;\
    }\
    location /api/v1/fpl/ {\
        proxy_pass http://127.0.0.1:8001/api/v1/fpl/;\
        proxy_set_header Host $host;\
        proxy_set_header X-Real-IP $remote_addr;\
    }\
    location /health {\
        proxy_pass http://127.0.0.1:8001/health;\
        proxy_set_header Host $host;\
        proxy_set_header X-Real-IP $remote_addr;\
    }' "$NGINX_CONF"
        sudo nginx -t && sudo systemctl reload nginx
        echo "Nginx reloaded successfully."
    else
        echo "Nginx already contains PL/FPL proxy rules."
    fi
fi

# 7. Local curl smoke tests
echo "=================================================================="
echo "RUNNING LOCAL VPS SMOKE TESTS"
echo "=================================================================="
curl -s http://127.0.0.1:8001/health | jq . || curl -s http://127.0.0.1:8001/health
echo ""
curl -s "http://127.0.0.1:8001/api/v1/pl/fixtures?gw=1&season=2025-26" | jq '.[0]' || curl -s "http://127.0.0.1:8001/api/v1/pl/fixtures?gw=1&season=2025-26"
echo ""
curl -s "http://127.0.0.1:8001/api/v1/fpl/gameweek/plan?gw=1&season=2025-26" | jq '{season, gameweek, formation, expected_total_points, captain}' || curl -s "http://127.0.0.1:8001/api/v1/fpl/gameweek/plan?gw=1&season=2025-26"
echo ""
echo "=================================================================="
echo "DEPLOYMENT COMPLETE — ENNOVERA PL + FPL IS SERVING ON PORT 8001"
echo "=================================================================="
