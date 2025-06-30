#!/bin/bash

# Create a test user through the API
echo "Creating test user..."

# Register a new client
RESPONSE=$(curl -s -X POST https://kwtsocial.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@fbrestaurant.com",
    "password": "Test123!",
    "company_name": "Test F&B Restaurant",
    "contact_name": "Test Owner",
    "phone": "+96599999999",
    "business_type": "restaurant"
  }')

echo "Registration response: $RESPONSE"

# Try to login
echo -e "\nTrying to login..."
LOGIN_RESPONSE=$(curl -s -X POST https://kwtsocial.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@fbrestaurant.com",
    "password": "Test123!"
  }')

echo "Login response: $LOGIN_RESPONSE"

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ ! -z "$TOKEN" ]; then
    echo -e "\n✅ Successfully logged in!"
    echo "Token: ${TOKEN:0:20}..."
    
    # Test trending endpoint
    echo -e "\nTesting trending endpoint..."
    curl -X GET https://kwtsocial.com/api/competitor/trending \
      -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -30
else
    echo "❌ Failed to get token"
fi