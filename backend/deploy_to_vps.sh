#!/bin/bash
# AlphaForge Backend Deployment Script for Oracle VPS
# Run this script on your VPS after uploading files

set -e  # Exit on any error

echo "=================================="
echo "🚀 AlphaForge Backend Deployment"
echo "=================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install Python 3.11 and pip
echo "🐍 Installing Python 3.11..."
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install system dependencies
echo "📚 Installing system dependencies..."
sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
sudo apt install -y postgresql postgresql-contrib  # Optional: if using PostgreSQL

# Create application directory
echo "📁 Setting up application directory..."
APP_DIR="/opt/alphaforge"
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

# Navigate to app directory
cd $APP_DIR

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements_alphaforge.txt

# Create .env file (you'll need to edit this)
echo "⚙️ Creating environment file..."
cat > .env << 'EOL'
# AlphaForge Production Environment

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
OANDA_API_KEY=your_oanda_api_key_here
OANDA_ACCOUNT_ID=your_oanda_account_id_here
OANDA_BASE_URL=https://api-fxpractice.oanda.com/v3

# Database (SQLite for now)
DATABASE_URL=sqlite:///./trading_signals.db

# Server Configuration
BACKEND_PORT=5000
BACKEND_HOST=0.0.0.0
ENVIRONMENT=production

# Trading Parameters
SYMBOLS=GBPUSD,XAUUSD,USDJPY
RISK_PER_TRADE=0.01
MAX_DAILY_RISK=0.03
MIN_CONFIDENCE=70

# CORS
FRONTEND_URL=http://161.118.218.33:3000
EOL

echo ""
echo "⚠️  IMPORTANT: Edit /opt/alphaforge/.env with your actual API keys!"
echo ""

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/alphaforge.service > /dev/null << 'EOL'
[Unit]
Description=AlphaForge Trading API Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/alphaforge
Environment="PATH=/opt/alphaforge/venv/bin"
ExecStart=/opt/alphaforge/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
echo "🚀 Starting AlphaForge service..."
sudo systemctl enable alphaforge
sudo systemctl start alphaforge

# Check status
echo ""
echo "✅ Deployment complete!"
echo ""
echo "Service status:"
sudo systemctl status alphaforge --no-pager

echo ""
echo "=================================="
echo "📝 Next Steps:"
echo "=================================="
echo "1. Edit .env file: nano /opt/alphaforge/.env"
echo "2. Add your API keys"
echo "3. Restart service: sudo systemctl restart alphaforge"
echo "4. Check logs: sudo journalctl -u alphaforge -f"
echo "5. Test API: curl http://localhost:5000/health"
echo ""
echo "Backend will be accessible at: http://161.118.218.33:5000"
echo "=================================="
