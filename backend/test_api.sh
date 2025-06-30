#!/bin/bash

echo "=== Testing Kuwait Social AI API ==="
echo ""

# Test login
echo "1. Testing Login Endpoint"
echo "-------------------------"
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@restaurant.com","password":"password123"}' \
  -s | python3 -m json.tool

echo ""
echo ""

# Test profile without auth (should fail)
echo "2. Testing Profile Endpoint (without auth - should fail)"
echo "-------------------------------------------------------"
curl http://localhost:8000/api/auth/profile -s | python3 -m json.tool

echo ""
echo ""

# Test admin dashboard without auth (should fail)
echo "3. Testing Admin Dashboard (without auth - should fail)"
echo "------------------------------------------------------"
curl http://localhost:8000/api/admin/dashboard -s | python3 -m json.tool