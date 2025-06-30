#!/bin/bash

echo "=== Testing Kuwait Social AI Deployment ==="
echo ""

echo "1. Backend API Health Check:"
curl -s http://209.38.176.129:5000/api/health 2>/dev/null || echo "   No health endpoint, checking root:"
curl -s http://209.38.176.129:5000/ | head -20

echo ""
echo "2. Frontend Status:"
curl -s -o /dev/null -w "   HTTP Status: %{http_code}\n" http://209.38.176.129:8080

echo ""
echo "3. Frontend Login Page:"
curl -s http://209.38.176.129:8080 | grep -E "(title|Kuwait|Login)" | head -5

echo ""
echo "=== Access Points ==="
echo "Frontend: http://209.38.176.129:8080"
echo "Backend API: http://209.38.176.129:5000"
echo ""
echo "Next step: Create admin account with ./create-admin.sh"