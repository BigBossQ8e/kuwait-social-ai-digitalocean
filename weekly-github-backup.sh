#!/bin/bash

# Weekly GitHub Backup Script
# This script automatically commits and pushes changes to GitHub

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Weekly GitHub Backup ===${NC}"
echo "Starting backup at: $(date)"

# Change to script directory
cd "$(dirname "$0")"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Fetch latest from remote
echo -e "${YELLOW}Fetching latest from GitHub...${NC}"
git fetch origin

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo -e "${YELLOW}Found uncommitted changes. Adding all files...${NC}"
    git add -A
    
    # Create commit message with date
    COMMIT_MSG="Weekly backup: $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${YELLOW}Creating commit: $COMMIT_MSG${NC}"
    git commit -m "$COMMIT_MSG"
else
    echo -e "${GREEN}No changes to commit${NC}"
fi

# Push to GitHub
echo -e "${YELLOW}Pushing to GitHub...${NC}"
if git push origin main; then
    echo -e "${GREEN}✅ Backup completed successfully!${NC}"
    echo "Pushed to: $(git remote get-url origin)"
else
    echo -e "${RED}❌ Failed to push to GitHub${NC}"
    echo "You may need to pull changes first with: git pull origin main"
    exit 1
fi

echo -e "${GREEN}Backup finished at: $(date)${NC}"