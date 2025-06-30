#!/bin/bash

# Verify Current Implementation Status
# This script checks what's actually running in production

SERVER_IP="209.38.176.129"
SERVER_USER="root"

echo "✅ Verifying Kuwait Social AI Implementation"
echo "=========================================="
echo ""

# Test endpoints and features
echo "1. TESTING ENDPOINTS"
echo "-------------------"

# Health check
echo -n "API Health: "
curl -s https://kwtsocial.com/api/health | jq -r '.status' 2>/dev/null || echo "FAILED"

# Check for React app
echo -n "React App: "
curl -s https://kwtsocial.com | grep -q "Vite" && echo "ACTIVE" || echo "NOT FOUND"

# Check for old landing page
echo -n "Old Landing Page: "
curl -s https://kwtsocial.com | grep -q "sections-wrapper" && echo "STILL ACTIVE" || echo "REMOVED"

# Check authentication
echo -n "Auth Endpoint: "
curl -s -X POST https://kwtsocial.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test","password":"test"}' | grep -q "error" && echo "WORKING" || echo "FAILED"

# Check translations endpoint
echo -n "Translations API: "
curl -s https://kwtsocial.com/api/translations?locale=en -o /dev/null -w "%{http_code}" | grep -q "200\|404" && echo "EXISTS" || echo "NOT DEPLOYED"

echo ""
echo "2. SERVER IMPLEMENTATION CHECK"
echo "-----------------------------"

ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'

cd /var/www/kwtsocial

# Check what's in static
echo "Static folder check:"
if [ -d "static" ]; then
    if [ -f "static/index.html" ]; then
        echo -n "  - Frontend type: "
        if grep -q "Vite" static/index.html; then
            echo "React (Vite build)"
            echo "  - Build date: $(stat -c%y static/index.html | cut -d' ' -f1)"
            echo "  - Asset files: $(find static/assets -name "*.js" 2>/dev/null | wc -l) JS, $(find static/assets -name "*.css" 2>/dev/null | wc -l) CSS"
        else
            echo "Static HTML"
            echo "  - Contains: $(grep -o 'section-' static/index.html | sort -u | wc -l) sections"
        fi
    else
        echo "  - No index.html in static/"
    fi
else
    echo "  - No static directory"
fi

echo ""
echo "Active Python modules:"
find . -name "*.py" -newer requirements.txt 2>/dev/null | grep -v venv | grep -v __pycache__ | wc -l | xargs echo "  - Recently modified Python files:"

echo ""
echo "Database tables:"
docker-compose exec -T postgres psql -U postgres -d kuwait_social_ai -c "\dt" 2>/dev/null | grep -c translations | xargs echo "  - Translation tables:"

echo ""
echo "Running containers:"
docker-compose ps --services | while read service; do
    echo "  - $service: $(docker-compose ps -q $service | xargs docker inspect -f '{{.State.Status}}')"
done

echo ""
echo "Nginx serving from:"
docker exec kwtsocial-nginx cat /etc/nginx/conf.d/default.conf | grep -A1 "location /" | grep root | sed 's/.*root/  -/'

ENDSSH

echo ""
echo "3. FEATURE DETECTION"
echo "-------------------"

# Check for language switcher
echo -n "Language Switcher: "
curl -s https://kwtsocial.com | grep -q -E "AR|EN|العربية|English" && echo "PRESENT" || echo "NOT FOUND"

# Check for i18n
echo -n "i18n Support: "
curl -s https://kwtsocial.com | grep -q "i18n" && echo "ACTIVE" || echo "NOT DETECTED"

# Check login form
echo -n "Login Form: "
curl -s https://kwtsocial.com/login 2>/dev/null | grep -q "password" && echo "ACCESSIBLE" || echo "REDIRECT/404"

echo ""
echo "4. RECOMMENDATIONS"
echo "-----------------"

# Analyze results
if curl -s https://kwtsocial.com | grep -q "Vite"; then
    echo "✅ React app is deployed and active"
else
    echo "❌ React app NOT detected - old HTML may still be active"
fi

if curl -s https://kwtsocial.com | grep -q "sections-wrapper"; then
    echo "⚠️  Old landing page HTML detected - needs removal"
fi

if curl -s https://kwtsocial.com/api/translations?locale=en -o /dev/null -w "%{http_code}" | grep -q "200"; then
    echo "✅ Translation API is working"
else
    echo "❌ Translation API not accessible"
fi

echo ""
echo "5. NEXT STEPS"
echo "------------"
echo "1. If old HTML is active: Deploy React build to static/"
echo "2. If translations API missing: Deploy backend updates"
echo "3. Clear browser cache and test language switching"
echo "4. Check admin panel at /admin after login"