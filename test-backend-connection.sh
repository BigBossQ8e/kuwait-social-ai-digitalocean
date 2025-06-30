#!/bin/bash

echo "=== Testing Backend Connection ==="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test local backend
echo "1. Testing local backend connection..."
echo ""

# Check if backend is running on port 5000
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/health | grep -q "200"; then
    echo -e "${GREEN}✓${NC} Backend is running on port 5000"
    echo ""
    
    # Test auth endpoints
    echo "2. Testing authentication endpoints..."
    
    # Test login endpoint
    echo -n "   - POST /api/auth/login: "
    LOGIN_RESPONSE=$(curl -s -X POST http://localhost:5000/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"test@example.com","password":"wrongpassword"}' \
        -w "\nHTTP_CODE:%{http_code}")
    
    HTTP_CODE=$(echo "$LOGIN_RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)
    
    if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "400" ]; then
        echo -e "${GREEN}✓${NC} Endpoint accessible (returned $HTTP_CODE)"
    else
        echo -e "${RED}✗${NC} Unexpected response (HTTP $HTTP_CODE)"
    fi
    
    # Test me endpoint (should return 401 without token)
    echo -n "   - GET /api/auth/me: "
    ME_RESPONSE=$(curl -s http://localhost:5000/api/auth/me -w "\nHTTP_CODE:%{http_code}")
    HTTP_CODE=$(echo "$ME_RESPONSE" | grep "HTTP_CODE:" | cut -d':' -f2)
    
    if [ "$HTTP_CODE" = "401" ]; then
        echo -e "${GREEN}✓${NC} Endpoint accessible (returned 401 - auth required)"
    else
        echo -e "${RED}✗${NC} Unexpected response (HTTP $HTTP_CODE)"
    fi
    
else
    echo -e "${RED}✗${NC} Backend is NOT running on port 5000"
    echo ""
    echo -e "${YELLOW}!${NC} To start the backend:"
    echo "   cd backend"
    echo "   python run_dev_server.py"
    echo ""
    echo "   Or with gunicorn:"
    echo "   gunicorn -c gunicorn_config.py wsgi:app"
fi

echo ""
echo "3. Checking backend logs for errors..."
if [ -f "backend/server.log" ]; then
    echo "Recent errors in server.log:"
    tail -n 20 backend/server.log | grep -i "error" || echo "   No recent errors found"
else
    echo "   No server.log file found"
fi

echo ""
echo "4. Checking database connection..."
if [ -f "backend/.env" ]; then
    DB_URL=$(grep "DATABASE_URL" backend/.env | cut -d'=' -f2)
    if [[ $DB_URL == *"sqlite"* ]]; then
        echo -e "${GREEN}✓${NC} Using SQLite database (good for local development)"
        
        # Check if database file exists
        DB_FILE=$(echo $DB_URL | sed 's/sqlite:\/\/\///')
        if [ -f "backend/$DB_FILE" ]; then
            echo -e "${GREEN}✓${NC} Database file exists"
        else
            echo -e "${YELLOW}!${NC} Database file not found. Run: cd backend && python init_local_db.py"
        fi
    else
        echo "   Using PostgreSQL database"
    fi
else
    echo -e "${RED}✗${NC} No .env file found in backend directory"
fi

echo ""
echo "=== Summary ==="
echo ""
echo "If the backend is not running, start it with:"
echo "  cd backend"
echo "  python run_dev_server.py"
echo ""
echo "If you see infinite spinning after login, check:"
echo "1. Backend is running and accessible"
echo "2. Database is properly initialized"
echo "3. Browser console for JavaScript errors"
echo "4. Network tab for failed API calls to /api/auth/me"