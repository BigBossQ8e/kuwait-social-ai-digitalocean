#!/bin/bash

echo "=== Final Backend Fix for 500 Error ==="
echo ""

ssh root@209.38.176.129 << 'EOF'
cd /root/kuwait-social-ai/backend

echo "1. Installing Python3 if needed:"
which python3 || apt-get update && apt-get install -y python3

echo ""
echo "2. Fixing MAX_CONTENT_LENGTH in config.py:"
sed -i.backup "s/MAX_CONTENT_LENGTH = os.getenv('MAX_CONTENT_LENGTH', '10485760')/MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '10485760'))/g" config/config.py

echo "Checking the fix:"
grep "MAX_CONTENT_LENGTH" config/config.py

echo ""
echo "3. Restart the backend container:"
docker restart kuwait-social-backend

echo ""
echo "4. Wait for startup:"
sleep 10

echo ""
echo "5. Check if backend is healthy:"
docker ps | grep kuwait-social-backend

echo ""
echo "6. Test the login endpoint:"
echo "Testing login with curl..."
response=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@kwtsocial.com","password":"Admin123!"}' \
  -s -w "\nHTTP_STATUS:%{http_code}")

echo "$response"

# Extract HTTP status
http_status=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)

if [ "$http_status" = "200" ]; then
    echo ""
    echo "✅ SUCCESS! Login endpoint is working!"
    echo ""
    echo "You can now login at: https://kwtsocial.com"
    echo "Email: admin@kwtsocial.com"
    echo "Password: Admin123!"
else
    echo ""
    echo "❌ Login still failing. Checking backend logs..."
    docker logs kuwait-social-backend --tail=20 2>&1 | grep -A 10 "ERROR\|Traceback"
fi

echo ""
echo "=== Backend fix complete ==="
EOF