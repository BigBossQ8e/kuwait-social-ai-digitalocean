#!/bin/bash

# Test Competitor Analysis API

echo "Testing Kuwait Social AI Competitor Analysis..."
echo "============================================"

# First get an auth token (using test client credentials)
echo "1. Getting auth token..."
TOKEN=$(curl -s -X POST https://kwtsocial.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test1@example.com","password":"TestPass123!"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get auth token"
    exit 1
fi

echo "✅ Got auth token"

# Test competitor analysis endpoint
echo -e "\n2. Testing competitor analysis..."
curl -X POST https://kwtsocial.com/api/competitor/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "your_instagram": "testrestaurant",
    "competitor_handles": "slider_station,pick_kw",
    "restaurant_type": "casual"
  }' | python3 -m json.tool

echo -e "\n3. Testing trending content..."
curl -X GET https://kwtsocial.com/api/competitor/trending \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo -e "\nTesting complete!"