#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Kuwait Social AI - Server Sync Check"
echo "===================================="

# Server details
SERVER="root@46.101.180.221"
SSH_KEY="~/.ssh/kuwait-social-ai-1750866399"
REMOTE_PATH="/opt/kuwait-social-ai/backend"
LOCAL_PATH="."

# Files to check (key files we've modified)
FILES_TO_CHECK=(
    "services/ai_service.py"
    "services/container.py"
    "services/__init__.py"
    "services/cache_service.py"
    "services/content_generator.py"
    "services/competitor_analysis_service.py"
    "services/hashtag_strategy_service.py"
    "services/prayer_times_service.py"
    "routes/ai_content.py"
    "config/f&b_config.py"
    ".env"
    "requirements.txt"
)

echo -e "\nChecking files..."
echo "----------------"

DIFFERENCES=0
MISSING_ON_SERVER=0

for file in "${FILES_TO_CHECK[@]}"; do
    echo -n "Checking $file... "
    
    # Check if file exists on server
    if ssh -i $SSH_KEY $SERVER "test -f $REMOTE_PATH/$file" 2>/dev/null; then
        # File exists, compare checksums
        LOCAL_CHECKSUM=$(md5 -q "$file" 2>/dev/null || md5sum "$file" 2>/dev/null | awk '{print $1}')
        REMOTE_CHECKSUM=$(ssh -i $SSH_KEY $SERVER "cd $REMOTE_PATH && (md5sum '$file' 2>/dev/null || md5 -q '$file' 2>/dev/null)" | awk '{print $1}')
        
        if [ "$LOCAL_CHECKSUM" = "$REMOTE_CHECKSUM" ]; then
            echo -e "${GREEN}✓ Synchronized${NC}"
        else
            echo -e "${RED}✗ Different${NC}"
            DIFFERENCES=$((DIFFERENCES + 1))
        fi
    else
        echo -e "${YELLOW}✗ Missing on server${NC}"
        MISSING_ON_SERVER=$((MISSING_ON_SERVER + 1))
    fi
done

echo -e "\n----------------"
echo "Summary:"
echo "  Files checked: ${#FILES_TO_CHECK[@]}"
echo "  Differences: $DIFFERENCES"
echo "  Missing on server: $MISSING_ON_SERVER"

if [ $DIFFERENCES -gt 0 ] || [ $MISSING_ON_SERVER -gt 0 ]; then
    echo -e "\n${YELLOW}Action needed: Files need to be synchronized!${NC}"
    echo -e "Run: ${GREEN}./deploy.sh${NC} to sync files to server"
else
    echo -e "\n${GREEN}All files are synchronized!${NC}"
fi

# Check if services are running
echo -e "\n\nChecking server services..."
echo "-------------------------"

# Check backend service
echo -n "Backend service: "
if ssh -i $SSH_KEY $SERVER "systemctl is-active kuwait-backend" 2>/dev/null | grep -q "active"; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
fi

# Check nginx
echo -n "Nginx service: "
if ssh -i $SSH_KEY $SERVER "systemctl is-active nginx" 2>/dev/null | grep -q "active"; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
fi

# Check Redis
echo -n "Redis service: "
if ssh -i $SSH_KEY $SERVER "systemctl is-active redis" 2>/dev/null | grep -q "active"; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
fi