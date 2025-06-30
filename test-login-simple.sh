#!/bin/bash

echo "=== Testing Login Directly ==="
echo ""

echo "1. Testing login endpoint from local machine:"
response=$(curl -X POST https://kwtsocial.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@kwtsocial.com","password":"Admin123!"}' \
  -s -w "\nHTTP_STATUS:%{http_code}\n" 2>&1)

echo "Response:"
echo "$response"

echo ""
echo "2. Testing with verbose output:"
curl -X POST https://kwtsocial.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@kwtsocial.com","password":"Admin123!"}' \
  -v 2>&1 | grep -E "< HTTP|< |{" | head -20

echo ""
echo "3. Try accessing the app directly:"
echo "   Go to: https://kwtsocial.com"
echo "   Click login and try:"
echo "   Email: admin@kwtsocial.com"
echo "   Password: Admin123!"