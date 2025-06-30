#!/bin/bash

echo "=== Kuwait Social AI Deployment Status ==="
echo ""
echo "📍 Server: 209.38.176.129"
echo "🌐 Domain: kwtsocial.com"
echo ""

# Check services
echo "1. Checking Backend API..."
curl -s -o /dev/null -w "   Backend API: %{http_code}\n" http://209.38.176.129:5000/api

echo ""
echo "2. Checking Frontend..."
curl -s -o /dev/null -w "   Frontend: %{http_code}\n" http://209.38.176.129

echo ""
echo "3. Checking Domain..."
curl -s -o /dev/null -w "   Domain (HTTP): %{http_code}\n" http://kwtsocial.com
curl -s -o /dev/null -w "   Domain (HTTPS): %{http_code}\n" https://kwtsocial.com

echo ""
echo "=== Next Steps ==="
echo ""
echo "1. Deploy Frontend (fix nginx config):"
echo "   ./deploy-frontend.sh"
echo ""
echo "2. Create Admin Account:"
echo "   ./create-admin.sh"
echo ""
echo "3. Access the application:"
echo "   http://209.38.176.129/login"
echo ""
echo "4. Configure DNS (if needed):"
echo "   Point kwtsocial.com to 209.38.176.129"
echo ""
echo "5. Set up SSL certificate:"
echo "   Use Let's Encrypt for HTTPS"