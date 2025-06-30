#!/bin/bash

# Cleanup Script for Kuwait Social AI Server
# This will clean up duplicates and unnecessary files

SERVER_IP="209.38.176.129"
SERVER_USER="root"

echo "🧹 Kuwait Social AI Server Cleanup"
echo "=================================="
echo ""
echo "This script will clean:"
echo "- Backup files (.bak, .old)"
echo "- macOS metadata files (._*, .DS_Store)"
echo "- Python cache (__pycache__)"
echo "- Duplicate route files"
echo "- Test files"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled"
    exit 1
fi

ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'

cd /opt/kuwait-social-ai

echo "📁 Creating backup directory for important files..."
BACKUP_DIR="/root/cleanup-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p $BACKUP_DIR

echo ""
echo "1️⃣ Backing up potentially important files..."
# Backup route files before cleaning
cp backend/routes/admin*.py $BACKUP_DIR/ 2>/dev/null || true
cp *.backup $BACKUP_DIR/ 2>/dev/null || true
echo "Backed up to: $BACKUP_DIR"

echo ""
echo "2️⃣ Removing macOS metadata files..."
find . -name '._*' -type f -delete 2>/dev/null
find . -name '.DS_Store' -type f -delete 2>/dev/null
echo "✓ Removed macOS junk files"

echo ""
echo "3️⃣ Cleaning Python cache..."
find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
find . -name '*.pyc' -type f -delete 2>/dev/null
echo "✓ Cleaned Python cache"

echo ""
echo "4️⃣ Removing backup files..."
find . -name '*.bak' -type f -delete 2>/dev/null
find . -name '*.backup' -type f -delete 2>/dev/null
find . -name '*~' -type f -delete 2>/dev/null
echo "✓ Removed backup files"

echo ""
echo "5️⃣ Cleaning duplicate route files..."
cd backend/routes
# Keep only the main admin.py, remove backups
rm -f admin-backup.py admin_old.py 2>/dev/null
echo "✓ Cleaned duplicate routes"

echo ""
echo "6️⃣ Removing test files..."
cd /opt/kuwait-social-ai
# Remove test files from root
rm -f test_*.py 2>/dev/null
echo "✓ Removed test files"

echo ""
echo "7️⃣ Checking remaining issues..."
echo ""
echo "Multiple frontend implementations found:"
echo "- frontend/ (React app - KEEP THIS)"
echo "- admin-panel/ (Old HTML - can be removed if not needed)"
echo "- client-dashboard/ (Check if needed)"
echo ""
echo "Large log file:"
echo "- backend/logs/kuwait-social-ai.log (860K)"
echo ""

echo "📊 Cleanup Summary:"
echo "-----------------"
echo "Space before cleanup:"
BEFORE=$(du -sh /opt/kuwait-social-ai | cut -f1)
echo $BEFORE

# Final cleanup of empty directories
find /opt/kuwait-social-ai -type d -empty -delete 2>/dev/null || true

echo ""
echo "Space after cleanup:"
AFTER=$(du -sh /opt/kuwait-social-ai | cut -f1)
echo $AFTER

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📝 Recommendations:"
echo "1. Remove admin-panel/ if not using old HTML admin"
echo "2. Rotate or truncate large log file"
echo "3. Check if client-dashboard/ is needed"
echo "4. Regular cleanup with: find . -name '__pycache__' -exec rm -rf {} +"

ENDSSH

echo ""
echo "🎯 Next Steps:"
echo "1. Deploy the new bilingual system with: ./deploy-to-kuwait.sh"
echo "2. Consider setting up a cron job for regular cleanup"
echo "3. Add .gitignore to prevent committing cache/temp files"