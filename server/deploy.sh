#!/bin/bash
# Quick deployment script for Local Feather server

SERVER_IP="192.168.1.234"
SERVER_USER="jcz"
SERVER_PATH="~/localfeather"
LOCAL_PATH="."

echo "======================================"
echo "Local Feather Server Deployment"
echo "======================================"
echo ""
echo "Deploying to: $SERVER_USER@$SERVER_IP:$SERVER_PATH"
echo ""

# Check if rsync is available
if ! command -v rsync &> /dev/null; then
    echo "❌ rsync not found. Installing..."
    sudo apt-get install -y rsync
fi

# Deploy files
echo "📦 Copying files to server..."
rsync -av --progress \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='deploy.sh' \
    $LOCAL_PATH/ $SERVER_USER@$SERVER_IP:$SERVER_PATH/

if [ $? -ne 0 ]; then
    echo "❌ Deployment failed"
    exit 1
fi

echo ""
echo "✓ Files deployed successfully!"
echo ""
echo "Next steps on the server ($SERVER_IP):"
echo ""
echo "  ssh $SERVER_USER@$SERVER_IP"
echo "  cd $SERVER_PATH"
echo "  python3 -m venv .venv"
echo "  source .venv/bin/activate"
echo "  pip install -r requirements.txt"
echo "  python run.py"
echo ""
echo "For production setup, see DEPLOYMENT.md"
echo ""
