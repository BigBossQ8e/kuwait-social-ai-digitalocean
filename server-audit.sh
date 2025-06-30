#!/bin/bash

# Server Audit Script for Kuwait Social AI
# This script checks for duplications, inconsistencies, and provides a clean report

set -e

echo "🔍 Kuwait Social AI Server Audit Tool"
echo "====================================="
echo ""

# Configuration
SERVER_IP="209.38.176.129"
SERVER_USER="root"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Create audit report
AUDIT_DATE=$(date +%Y%m%d-%H%M%S)
REPORT_FILE="server-audit-$AUDIT_DATE.txt"

echo "📝 Generating audit report: $REPORT_FILE"
echo ""

# SSH into server and run audit
ssh $SERVER_USER@$SERVER_IP << 'ENDSSH' > $REPORT_FILE 2>&1

echo "KUWAIT SOCIAL AI - SERVER AUDIT REPORT"
echo "Generated: $(date)"
echo "Server: $(hostname)"
echo "======================================="
echo ""

# 1. Check Docker containers
echo "1. DOCKER CONTAINERS STATUS"
echo "--------------------------"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Size}}"
echo ""

# 2. Check for duplicate files
echo "2. CHECKING FOR DUPLICATE FILES"
echo "------------------------------"
cd /var/www/kwtsocial

# Check for duplicate Python files
echo "Duplicate Python files:"
find . -name "*.py" -type f -exec md5sum {} \; 2>/dev/null | sort | uniq -w32 -d --all-repeated=separate | grep -v __pycache__ || echo "No duplicate Python files found"
echo ""

# Check for backup files
echo "Backup files (.bak, .old, ~):"
find . -name "*.bak" -o -name "*.old" -o -name "*~" -type f 2>/dev/null | grep -v node_modules || echo "No backup files found"
echo ""

# 3. Check directory structure
echo "3. DIRECTORY STRUCTURE"
echo "--------------------"
echo "Main directories:"
ls -la | grep "^d" | awk '{print $9}' | grep -v "^\." | sort
echo ""

echo "Static directory structure:"
if [ -d "static" ]; then
    find static -type d -maxdepth 2 | sort
else
    echo "No static directory found"
fi
echo ""

# 4. Check for multiple frontend implementations
echo "4. FRONTEND IMPLEMENTATIONS CHECK"
echo "--------------------------------"
echo "HTML files in root:"
find . -maxdepth 1 -name "*.html" -type f | sort
echo ""

echo "Frontend directories:"
find . -maxdepth 2 -type d -name "*frontend*" -o -name "*react*" -o -name "*static*" | sort
echo ""

echo "Index files:"
find . -name "index.html" -type f | grep -v node_modules | sort
echo ""

# 5. Check Python imports and dependencies
echo "5. PYTHON DEPENDENCIES"
echo "--------------------"
if [ -f "requirements.txt" ]; then
    echo "requirements.txt exists"
    echo "Total dependencies: $(wc -l < requirements.txt)"
    echo "Duplicate dependencies:"
    sort requirements.txt | uniq -d || echo "No duplicate dependencies"
else
    echo "No requirements.txt found"
fi
echo ""

# 6. Check for conflicting routes
echo "6. API ROUTES CHECK"
echo "-----------------"
echo "Route files:"
find . -path ./venv -prune -o -name "*route*.py" -type f -print | sort
echo ""

echo "Blueprint registrations in app_factory.py:"
if [ -f "app_factory.py" ]; then
    grep -n "register_blueprint" app_factory.py || echo "No blueprints found"
else
    echo "app_factory.py not found"
fi
echo ""

# 7. Check nginx configuration
echo "7. NGINX CONFIGURATION"
echo "--------------------"
docker exec kwtsocial-nginx cat /etc/nginx/conf.d/default.conf | grep -E "location|root|proxy_pass" | grep -v "#"
echo ""

# 8. Database tables check
echo "8. DATABASE TABLES"
echo "-----------------"
docker-compose exec -T postgres psql -U postgres -d kuwait_social_ai -c "\dt" | grep -E "users|posts|translations|clients" || echo "Could not retrieve tables"
echo ""

# 9. Check for orphaned files
echo "9. POTENTIALLY ORPHANED FILES"
echo "----------------------------"
echo "JavaScript files not in static/dist:"
find . -name "*.js" -type f | grep -v node_modules | grep -v static/dist | grep -v venv | head -20
echo ""

echo "CSS files not in static/dist:"
find . -name "*.css" -type f | grep -v node_modules | grep -v static/dist | grep -v venv | head -20
echo ""

# 10. Check logs for errors
echo "10. RECENT ERROR LOGS"
echo "-------------------"
echo "Last 10 errors from web container:"
docker logs kwtsocial-web 2>&1 | grep -i error | tail -10 || echo "No recent errors"
echo ""

# 11. File count summary
echo "11. FILE COUNT SUMMARY"
echo "--------------------"
echo "Python files: $(find . -name "*.py" -type f | grep -v venv | grep -v __pycache__ | wc -l)"
echo "JavaScript files: $(find . -name "*.js" -type f | grep -v node_modules | wc -l)"
echo "HTML files: $(find . -name "*.html" -type f | grep -v node_modules | wc -l)"
echo "CSS files: $(find . -name "*.css" -type f | grep -v node_modules | wc -l)"
echo "Total files: $(find . -type f | grep -v node_modules | grep -v venv | grep -v __pycache__ | wc -l)"
echo ""

# 12. Git status
echo "12. GIT STATUS"
echo "-------------"
if [ -d ".git" ]; then
    echo "Git repository found"
    echo "Current branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
    echo "Uncommitted changes:"
    git status --porcelain | head -20 || echo "No uncommitted changes"
else
    echo "Not a git repository"
fi
echo ""

# 13. Memory and disk usage
echo "13. RESOURCE USAGE"
echo "-----------------"
echo "Disk usage:"
df -h | grep -E "/$|/var/www"
echo ""
echo "Directory sizes:"
du -sh * 2>/dev/null | sort -rh | head -10
echo ""

echo "======================================="
echo "AUDIT COMPLETE"
echo "======================================="

ENDSSH

echo ""
echo -e "${GREEN}✓${NC} Audit complete! Report saved to: $REPORT_FILE"
echo ""

# Analyze the report locally
echo "📊 Quick Analysis:"
echo ""

# Check for issues
if grep -q "\.bak\|\.old" $REPORT_FILE; then
    echo -e "${YELLOW}⚠${NC}  Found backup files that should be removed"
fi

if grep -q "No duplicate Python files found" $REPORT_FILE; then
    echo -e "${GREEN}✓${NC} No duplicate Python files detected"
else
    echo -e "${RED}✗${NC} Duplicate Python files detected"
fi

if grep -q "index.html" $REPORT_FILE | grep -v "static/dist"; then
    echo -e "${YELLOW}⚠${NC}  Multiple index.html files found"
fi

echo ""
echo "📋 Recommended Actions:"
echo ""
echo "1. Review the full report: cat $REPORT_FILE"
echo "2. Check for duplicate routes and blueprints"
echo "3. Remove any backup files (.bak, .old, ~)"
echo "4. Ensure only one frontend implementation is active"
echo "5. Clean up any orphaned files"
echo ""

# Create cleanup script
cat > cleanup-suggestions.sh << 'EOF'
#!/bin/bash
# Cleanup suggestions based on audit

echo "🧹 Cleanup Commands (review before running):"
echo ""
echo "# Remove backup files:"
echo "find /var/www/kwtsocial -name '*.bak' -o -name '*.old' -o -name '*~' -type f -delete"
echo ""
echo "# Remove Python cache:"
echo "find /var/www/kwtsocial -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null"
echo ""
echo "# Clean docker logs:"
echo "docker-compose logs --tail=1000 > logs-backup.txt"
echo "truncate -s 0 $(docker inspect --format='{{.LogPath}}' kwtsocial-web)"
echo ""
echo "# Remove orphaned files (check each carefully):"
echo "# Add specific commands after reviewing audit report"
EOF

chmod +x cleanup-suggestions.sh

echo "💡 Cleanup suggestions saved to: cleanup-suggestions.sh"