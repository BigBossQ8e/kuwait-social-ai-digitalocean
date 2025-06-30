#!/bin/bash

echo "=== Kuwait Social AI Deployment Check ==="
echo ""
echo "📍 Checking deployment status..."
echo ""

# Check the correct IP
echo "1. Checking DigitalOcean server (209.38.176.129):"
curl -s -o /dev/null -w "   HTTP Status: %{http_code}\n" http://209.38.176.129

echo ""
echo "2. Checking API endpoint:"
curl -s -o /dev/null -w "   HTTP Status: %{http_code}\n" http://209.38.176.129:5000/api

echo ""
echo "3. Checking frontend:"
curl -s -o /dev/null -w "   HTTP Status: %{http_code}\n" http://209.38.176.129:80

echo ""
echo "📋 Correct Deployment Information:"
echo "   - DigitalOcean IP: 209.38.176.129"
echo "   - Domain: kwtsocial.com (may need DNS update)"
echo "   - Frontend: http://209.38.176.129"
echo "   - Backend API: http://209.38.176.129:5000"

echo ""
echo "🔧 To access your server:"
echo "   ssh root@209.38.176.129"
echo ""
echo "📝 Login Information:"
echo "   - You need to use an EMAIL address to login"
echo "   - Check if an admin account was created during deployment"
echo "   - If not, you may need to create one via SSH"