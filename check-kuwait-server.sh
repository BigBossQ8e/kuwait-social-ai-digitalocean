#!/bin/bash

# Check Kuwait Social AI Production Server
# Updated with correct paths

SERVER_IP="209.38.176.129"
SERVER_USER="root"
APP_DIR="/opt/kuwait-social-ai"

echo "🔍 Checking Kuwait Social AI Production Server"
echo "============================================="
echo ""

ssh $SERVER_USER@$SERVER_IP << ENDSSH

echo "1. APPLICATION LOCATION"
echo "---------------------"
echo "App directory: $APP_DIR"
cd $APP_DIR 2>/dev/null || { echo "ERROR: Cannot access $APP_DIR"; exit 1; }
echo "Current directory: $(pwd)"
echo ""

echo "2. DIRECTORY STRUCTURE"
echo "--------------------"
ls -la | grep -E "^d" | grep -v "^\." | awk '{print "  " \$9}'
echo ""

echo "3. FRONTEND STATUS"
echo "-----------------"
# Check for frontend directory
if [ -d "frontend" ]; then
    echo "Frontend directory exists"
    echo "Contents:"
    ls -la frontend/ | head -10
    echo ""
    if [ -f "frontend/index.html" ]; then
        echo "Frontend type check:"
        grep -q "Vite\|React" frontend/index.html && echo "  ✓ React/Vite app detected" || echo "  → Static HTML"
        echo "  Modified: $(stat -c%y frontend/index.html 2>/dev/null | cut -d' ' -f1)"
    fi
elif [ -d "static" ]; then
    echo "Static directory exists"
    ls -la static/ | head -10
fi
echo ""

echo "4. BACKEND STATUS"
echo "----------------"
if [ -d "backend" ]; then
    echo "Backend directory exists"
    echo "Python files:"
    find backend -name "*.py" -maxdepth 2 | head -10
    echo ""
    echo "Routes directory:"
    ls -la backend/routes/ 2>/dev/null | grep -E "\.py$" | awk '{print "  " \$9}'
fi
echo ""

echo "5. RUNNING SERVICES"
echo "------------------"
# Check systemd service
echo "SystemD service:"
systemctl status kuwait-social-ai-* --no-pager 2>/dev/null | head -5 || echo "  No systemd service found"
echo ""

# Check gunicorn
echo "Gunicorn processes:"
ps aux | grep gunicorn | grep -v grep | wc -l | xargs echo "  Running workers:"
echo ""

# Check Docker containers
echo "Docker containers:"
docker ps --format "  {{.Names}}: {{.Status}}" | grep kuwait || echo "  Using native services"
echo ""

echo "6. NGINX CONFIGURATION"
echo "--------------------"
if [ -f /etc/nginx/sites-enabled/kuwait-social-ai ]; then
    echo "Nginx config found:"
    grep -E "root|proxy_pass|server_name" /etc/nginx/sites-enabled/kuwait-social-ai | head -10
else
    echo "Checking default nginx:"
    ls -la /etc/nginx/sites-enabled/
fi
echo ""

echo "7. CURRENT DEPLOYMENT"
echo "-------------------"
# Check what's being served
echo "Testing endpoints:"
echo -n "  Homepage: "
curl -s http://localhost/ -o /dev/null -w "%{http_code}\n" 2>/dev/null || echo "Failed"
echo -n "  API Health: "
curl -s http://localhost:5000/api/health -o /dev/null -w "%{http_code}\n" 2>/dev/null || echo "Failed"
echo -n "  Login page: "
curl -s http://localhost/login -o /dev/null -w "%{http_code}\n" 2>/dev/null || echo "Failed"
echo ""

echo "8. RECENT CHANGES"
echo "----------------"
echo "Recently modified files:"
find . -type f -mtime -7 -name "*.py" -o -name "*.html" -o -name "*.js" 2>/dev/null | grep -v "__pycache__" | head -10
echo ""

echo "9. POTENTIAL ISSUES"
echo "------------------"
# Check for duplicates
echo "Duplicate HTML files:"
find . -name "index.html" -type f 2>/dev/null | head -5
echo ""
echo "Backup files:"
find . -maxdepth 3 -name "*.bak" -o -name "*.old" -o -name "*~" 2>/dev/null | head -5
echo ""

ENDSSH

echo ""
echo "✅ Check complete!"
echo ""
echo "Key locations on this server:"
echo "- Application: /opt/kuwait-social-ai/"
echo "- Frontend: /opt/kuwait-social-ai/frontend/"
echo "- Backend: /opt/kuwait-social-ai/backend/"
echo "- Nginx config: /etc/nginx/sites-enabled/kuwait-social-ai"