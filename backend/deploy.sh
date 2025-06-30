#!/bin/bash

# Kuwait Social AI - Deployment Script
# This script syncs local changes to the production server

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Server configuration
SERVER="root@46.101.180.221"
SSH_KEY="~/.ssh/kuwait-social-ai-1750866399"
REMOTE_PATH="/opt/kuwait-social-ai/backend"
LOCAL_PATH="."

echo -e "${BLUE}Kuwait Social AI - Deployment Script${NC}"
echo "====================================="
echo "Target server: $SERVER"
echo "Remote path: $REMOTE_PATH"
echo ""

# Function to sync files
sync_files() {
    echo -e "${YELLOW}Syncing files to server...${NC}"
    
    # Create remote directory if it doesn't exist
    ssh -i $SSH_KEY $SERVER "mkdir -p $REMOTE_PATH"
    
    # Sync all Python files and configs
    rsync -avz --progress \
        -e "ssh -i $SSH_KEY" \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        --exclude='venv' \
        --exclude='env' \
        --exclude='*.log' \
        --exclude='*.db' \
        --exclude='migrations/versions/*' \
        --include='*/' \
        --include='*.py' \
        --include='*.txt' \
        --include='*.json' \
        --include='*.yaml' \
        --include='*.yml' \
        --include='.env' \
        --include='*.md' \
        --include='*.sh' \
        --include='*config*' \
        $LOCAL_PATH/ $SERVER:$REMOTE_PATH/
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Files synced successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ File sync failed${NC}"
        return 1
    fi
}

# Function to install dependencies
install_dependencies() {
    echo -e "\n${YELLOW}Installing dependencies on server...${NC}"
    
    ssh -i $SSH_KEY $SERVER "cd $REMOTE_PATH && source venv/bin/activate && pip install -r requirements.txt"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Dependencies installed${NC}"
        return 0
    else
        echo -e "${RED}✗ Dependency installation failed${NC}"
        return 1
    fi
}

# Function to run database migrations
run_migrations() {
    echo -e "\n${YELLOW}Running database migrations...${NC}"
    
    ssh -i $SSH_KEY $SERVER "cd $REMOTE_PATH && source venv/bin/activate && flask db upgrade"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Migrations completed${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Migration failed or no migrations to run${NC}"
        return 0  # Don't fail deployment if no migrations
    fi
}

# Function to restart services
restart_services() {
    echo -e "\n${YELLOW}Restarting services...${NC}"
    
    # Restart backend service
    echo -n "  Restarting backend service... "
    ssh -i $SSH_KEY $SERVER "systemctl restart kuwait-backend"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
    
    # Reload nginx (no downtime)
    echo -n "  Reloading nginx... "
    ssh -i $SSH_KEY $SERVER "nginx -t && systemctl reload nginx"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
    
    return 0
}

# Function to check service status
check_services() {
    echo -e "\n${YELLOW}Checking service status...${NC}"
    
    # Check backend
    echo -n "  Backend service: "
    if ssh -i $SSH_KEY $SERVER "systemctl is-active kuwait-backend" 2>/dev/null | grep -q "active"; then
        echo -e "${GREEN}✓ Running${NC}"
    else
        echo -e "${RED}✗ Not running${NC}"
        # Show logs
        echo -e "${YELLOW}  Recent logs:${NC}"
        ssh -i $SSH_KEY $SERVER "journalctl -u kuwait-backend -n 10 --no-pager"
    fi
    
    # Check API endpoint
    echo -n "  API health check: "
    API_RESPONSE=$(ssh -i $SSH_KEY $SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost:5000/api/health" 2>/dev/null)
    if [ "$API_RESPONSE" = "200" ]; then
        echo -e "${GREEN}✓ Responding${NC}"
    else
        echo -e "${RED}✗ Not responding (HTTP $API_RESPONSE)${NC}"
    fi
}

# Main deployment flow
echo -e "${BLUE}Starting deployment...${NC}\n"

# Step 1: Sync files
if ! sync_files; then
    echo -e "${RED}Deployment failed at file sync${NC}"
    exit 1
fi

# Step 2: Install dependencies (optional, ask user)
echo -e "\n${YELLOW}Install/update dependencies?${NC} (y/N)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    install_dependencies
fi

# Step 3: Run migrations (optional, ask user)
echo -e "\n${YELLOW}Run database migrations?${NC} (y/N)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    run_migrations
fi

# Step 4: Restart services
if ! restart_services; then
    echo -e "${RED}Service restart failed${NC}"
    exit 1
fi

# Step 5: Check status
check_services

echo -e "\n${GREEN}✓ Deployment completed successfully!${NC}"
echo -e "${BLUE}Server URL: https://app.kuwaitsa.com${NC}"