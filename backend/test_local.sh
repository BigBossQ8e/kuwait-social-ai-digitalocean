#!/bin/bash

echo "Testing local backend with SQLite database..."
echo ""

# Test login
echo "1. Testing login endpoint:"
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@restaurant.com","password":"password123"}' \
  -w "\nStatus: %{http_code}\nTime: %{time_total}s\n"

echo ""
echo "2. Testing health check:"
curl http://localhost:5000/api/health \
  -w "\nStatus: %{http_code}\n"

echo ""
echo "Local database file:"
ls -la kuwait_social_test.db