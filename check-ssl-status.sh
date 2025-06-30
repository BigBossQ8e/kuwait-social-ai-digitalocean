#!/bin/bash

echo "=== Checking SSL/HTTPS Status ==="
echo ""

# Check SSL locally first
echo "1. Testing HTTPS access from local:"
echo "   - Testing https://kwtsocial.com"
curl -s -o /dev/null -w "     Status: %{http_code}, SSL: %{ssl_verify_result}\n" https://kwtsocial.com || echo "     Connection failed"

echo ""
echo "   - Testing https://209.38.176.129"
curl -k -s -o /dev/null -w "     Status: %{http_code}, SSL: %{ssl_verify_result}\n" https://209.38.176.129 || echo "     Connection failed"

echo ""
echo "2. Checking SSL configuration on server:"
ssh root@209.38.176.129 << 'EOF'
echo "   a) Checking for SSL certificates:"
if [ -d "/etc/letsencrypt/live" ]; then
    echo "      Let's Encrypt certificates found:"
    ls -la /etc/letsencrypt/live/
else
    echo "      No Let's Encrypt certificates found"
fi

echo ""
echo "   b) Checking nginx SSL configuration:"
grep -r "ssl_certificate\|listen.*443\|ssl" /etc/nginx/sites-available/ 2>/dev/null | head -20

echo ""
echo "   c) Checking if port 443 is open:"
sudo netstat -tlnp | grep :443 || echo "      Port 443 is not listening"

echo ""
echo "   d) Checking nginx sites enabled:"
ls -la /etc/nginx/sites-enabled/

echo ""
echo "   e) Testing nginx configuration:"
sudo nginx -t

echo ""
echo "   f) Checking for Certbot:"
which certbot && certbot --version || echo "      Certbot not installed"
EOF

echo ""
echo "=== SSL Status Summary ==="
echo "Domain: kwtsocial.com"
echo "IP: 209.38.176.129"