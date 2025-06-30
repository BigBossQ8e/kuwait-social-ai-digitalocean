#!/bin/bash

# Quick Duplicate Check for Kuwait Social AI
# Focuses on finding conflicting implementations

SERVER_IP="209.38.176.129"
SERVER_USER="root"

echo "🔍 Checking for Duplicate Implementations..."
echo ""

ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'

cd /var/www/kwtsocial

echo "1. FRONTEND CONFLICTS"
echo "===================="
echo ""

# Check for multiple index.html files
echo "📄 Index.html files:"
find . -name "index.html" -type f 2>/dev/null | grep -v node_modules | while read file; do
    echo "  $file ($(stat -c%s "$file") bytes, modified: $(stat -c%y "$file" | cut -d' ' -f1))"
done
echo ""

# Check for old vs new frontend
echo "📁 Frontend directories:"
ls -la | grep -E "^d.*frontend|^d.*static|^d.*react|^d.*dist" || echo "  No frontend directories in root"
echo ""

# Check static folder contents
echo "📦 Static folder contents:"
if [ -d "static" ]; then
    echo "  Main files/dirs in static/:"
    ls -la static/ | head -10
    echo ""
    echo "  Looking for React build signature:"
    if [ -f "static/index.html" ]; then
        grep -q "Vite" static/index.html && echo "  ✓ Found Vite/React build" || echo "  ✗ Not a Vite/React build"
    fi
else
    echo "  No static directory found"
fi
echo ""

echo "2. BACKEND CONFLICTS"
echo "=================="
echo ""

# Check for duplicate route files
echo "🛣️  Route files:"
find . -name "*route*.py" -o -name "*auth*.py" -o -name "*api*.py" | grep -v venv | grep -v __pycache__ | sort
echo ""

# Check for duplicate model files
echo "📊 Model files:"
find . -name "*model*.py" -o -name "user.py" -o -name "client.py" | grep -v venv | grep -v __pycache__ | sort
echo ""

# Check app initialization files
echo "🚀 App initialization files:"
ls -la app*.py 2>/dev/null || echo "  No app*.py files found"
echo ""

echo "3. CONFIGURATION CONFLICTS"
echo "========================"
echo ""

# Check for multiple config files
echo "⚙️  Configuration files:"
ls -la *.conf *.ini *.env .env 2>/dev/null || echo "  No config files in root"
echo ""

# Check nginx configs
echo "🌐 Nginx configurations:"
docker exec kwtsocial-nginx ls -la /etc/nginx/conf.d/ 2>/dev/null || echo "  Could not check nginx configs"
echo ""

echo "4. POTENTIAL ISSUES"
echo "=================="
echo ""

# Check for test/temp files
echo "🗑️  Temporary/test files:"
find . -maxdepth 3 -name "test*" -o -name "temp*" -o -name "tmp*" -o -name "old*" | grep -v node_modules | grep -v venv | head -10
echo ""

# Check for multiple package files
echo "📦 Package management files:"
ls -la package*.json requirements*.txt Pipfile* 2>/dev/null || echo "  Standard package files only"
echo ""

# Quick size check
echo "5. DISK USAGE"
echo "============"
du -sh * 2>/dev/null | sort -rh | head -10
echo ""

# Docker status
echo "6. DOCKER STATUS"
echo "=============="
docker-compose ps
echo ""

echo "7. RECOMMENDATIONS"
echo "================="
echo ""
echo "✓ Check if static/ contains the latest React build"
echo "✓ Remove any old HTML files in root directory"
echo "✓ Ensure only one frontend implementation is active"
echo "✓ Clean up test/temporary files"
echo "✓ Verify nginx is serving from the correct location"

ENDSSH