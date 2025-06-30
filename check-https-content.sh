#!/bin/bash

echo "=== Checking HTTPS Content ==="
echo ""

echo "1. Testing what's served on HTTPS:"
echo "   - https://kwtsocial.com"
curl -s https://kwtsocial.com | grep -E "<title>|<h1>|Kuwait" | head -5

echo ""
echo "2. Checking nginx configuration details:"
ssh root@209.38.176.129 << 'EOF'
echo "   Active nginx configurations:"
cat /etc/nginx/sites-enabled/kwtsocial.com | grep -E "server_name|proxy_pass|root|location /" -A 2 | head -20

echo ""
echo "   Checking if it's proxying to our containers:"
grep -r "proxy_pass.*8080\|proxy_pass.*5000" /etc/nginx/sites-available/ 2>/dev/null
EOF

echo ""
echo "3. Current access points:"
echo "   - HTTPS Frontend: https://kwtsocial.com"
echo "   - HTTP Frontend: http://209.38.176.129:8080"
echo "   - Backend API: http://209.38.176.129:5000"