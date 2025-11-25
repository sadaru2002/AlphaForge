#!/bin/bash
# AlphaForge Docker Deployment Script
# Usage: ./deploy_docker.sh [USER@HOST] [SSH_KEY_PATH]

set -e

# Configuration
REMOTE_HOST=${1:-"ubuntu@161.118.218.33"}
SSH_KEY=${2:-"~/.ssh/id_rsa"}
REMOTE_DIR="/opt/alphaforge"

echo "=================================="
echo "🚀 AlphaForge Docker Deployment"
echo "=================================="
echo "Target: $REMOTE_HOST"
echo "SSH Key: $SSH_KEY"
echo "=================================="

# 1. Check SSH connection
echo "📡 Checking connection..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$REMOTE_HOST" "echo '✅ Connection successful'" || {
    echo "❌ Failed to connect to $REMOTE_HOST"
    exit 1
}

# 2. Install Docker on Remote (if missing)
echo "🐳 Checking Docker installation..."
ssh -i "$SSH_KEY" "$REMOTE_HOST" "command -v docker >/dev/null 2>&1 || { 
    echo 'Installing Docker...';
    curl -fsSL https://get.docker.com -o get-docker.sh;
    sudo sh get-docker.sh;
    sudo usermod -aG docker \$USER;
    rm get-docker.sh;
    echo 'Docker installed.';
}"

# 3. Prepare Remote Directory
echo "📁 Preparing remote directory..."
ssh -i "$SSH_KEY" "$REMOTE_HOST" "sudo mkdir -p $REMOTE_DIR && sudo chown -R \$USER:\$USER $REMOTE_DIR"

# 4. Sync Files
echo "🔄 Syncing files..."
rsync -avz -e "ssh -i $SSH_KEY" \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude '.git' \
    --exclude 'trading_signals.db' \
    ./ "$REMOTE_HOST:$REMOTE_DIR/"

# 5. Deploy with Docker Compose
echo "🚀 Deploying container..."
ssh -i "$SSH_KEY" "$REMOTE_HOST" "cd $REMOTE_DIR && docker compose up -d --build"

echo "=================================="
echo "✅ Deployment Complete!"
echo "=================================="
echo "Backend: http://${REMOTE_HOST#*@}:5000"
echo "Health Check: http://${REMOTE_HOST#*@}:5000/health"
