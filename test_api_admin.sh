#!/bin/bash

# Test API with admin credentials
echo "Testing Kuwait Social AI API with admin..."
echo "=========================================="

# Try admin login
echo "1. Testing admin login..."
RESPONSE=$(curl -s -X POST https://kwtsocial.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@kuwaitai.com","password":"AdminPassword123!"}')

echo "Response: $RESPONSE"

TOKEN=$(echo $RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get auth token"
    echo "Trying alternative admin..."
    
    RESPONSE=$(curl -s -X POST https://kwtsocial.com/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"admin@socialtest.com","password":"AdminNewPassword123!"}')
    
    echo "Response: $RESPONSE"
    TOKEN=$(echo $RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
fi

if [ -z "$TOKEN" ]; then
    echo "❌ Still no auth token"
    exit 1
fi

echo "✅ Got auth token"

# Test competitor trending endpoint (doesn't require client role)
echo -e "\n2. Testing trending content..."
curl -X GET https://kwtsocial.com/api/competitor/trending \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool