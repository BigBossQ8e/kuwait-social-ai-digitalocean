#!/bin/bash

# Kuwait Social AI - Sync to Production Script
# This syncs your local files to the production server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Kuwait Social AI - Sync to Production"
echo "========================================"

# Server details
SERVER="root@46.101.180.221"
SSH_KEY="$HOME/.ssh/kuwait-social-ai-1750866399"
REMOTE_PATH="/opt/kuwait-social-ai/backend"
LOCAL_PATH="./backend"

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${RED}❌ SSH key not found at: $SSH_KEY${NC}"
    exit 1
fi

# Files to sync
echo -e "\n${YELLOW}Files that will be synced:${NC}"
echo "- services/ai_service.py"
echo "- services/content_generator.py"
echo "- config/f_b_config.py"
echo "- requirements.txt"
echo "- All other changed files"

# Confirm before syncing
echo -e "\n${YELLOW}This will sync files to: $SERVER:$REMOTE_PATH${NC}"
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Sync cancelled."
    exit 1
fi

# Create backup on server
echo -e "\n📦 Creating backup on server..."
ssh -i "$SSH_KEY" "$SERVER" "cd /opt/kuwait-social-ai && tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz backend/"

# Sync files
echo -e "\n📤 Syncing files to production..."
rsync -avz --progress \
    --exclude='venv/' \
    --exclude='venv_old_py39/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.git/' \
    --exclude='*.db' \
    --exclude='.env' \
    --exclude='.env.local' \
    --exclude='uploads/' \
    --exclude='instance/' \
    --exclude='logs/' \
    -e "ssh -i $SSH_KEY" \
    "$LOCAL_PATH/" "$SERVER:$REMOTE_PATH/"

echo -e "\n${GREEN}✅ Files synced successfully!${NC}"

# Post-sync actions
echo -e "\n📋 Post-sync actions needed:"
echo "1. SSH to server: ssh -i $SSH_KEY $SERVER"
echo "2. Add Anthropic API key to .env:"
echo "   echo 'ANTHROPIC_API_KEY=sk-ant-api03-...' >> $REMOTE_PATH/.env"
echo "3. Update packages:"
echo "   cd $REMOTE_PATH && python3 -m pip install -r requirements.txt --upgrade"
echo "4. Restart service:"
echo "   systemctl restart kuwait-backend"
echo "5. Check status:"
echo "   systemctl status kuwait-backend"

echo -e "\n${GREEN}✅ Sync complete!${NC}"