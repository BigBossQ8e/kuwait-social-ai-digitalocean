#!/bin/bash

echo "=== Kuwait Social AI Deployment Check ==="
echo ""
echo "📍 Checking deployment status..."
echo ""

# Check if the domain is accessible
echo "1. Checking domain (https://kwtsocial.com):"
curl -s -o /dev/null -w "   HTTP Status: %{http_code}\n" https://kwtsocial.com

echo ""
echo "2. Checking API endpoint:"
curl -s -o /dev/null -w "   HTTP Status: %{http_code}\n" https://kwtsocial.com/api

echo ""
echo "3. Checking login page:"
curl -s -o /dev/null -w "   HTTP Status: %{http_code}\n" https://kwtsocial.com/login

echo ""
echo "📋 Deployment Information:"
echo "   - Domain: kwtsocial.com"
echo "   - Droplet IP: 46.101.180.221"
echo "   - Expected endpoints:"
echo "     • Frontend: https://kwtsocial.com"
echo "     • API: https://kwtsocial.com/api"
echo "     • Login: https://kwtsocial.com/login"

echo ""
echo "🔧 If you see the default Vite page, the frontend needs to be rebuilt:"
echo "   1. SSH into droplet: ssh root@46.101.180.221"
echo "   2. Navigate to: cd /root/kuwait-social-ai"
echo "   3. Rebuild: docker-compose down && docker-compose up -d --build"
echo ""
echo "📝 Default admin credentials (from DEPLOYMENT_SUMMARY.md):"
echo "   - Username: admin"
echo "   - Password: KuwaitSocialAdmin123!"