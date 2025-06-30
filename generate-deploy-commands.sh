#!/bin/bash

echo "# Admin Panel Deployment Commands"
echo "# Copy and paste these commands on your server"
echo ""
echo "# 1. Create directory"
echo "mkdir -p /var/www/html/admin-panel"
echo ""
echo "# 2. Create index.html"
echo "cat > /var/www/html/admin-panel/index.html << 'ENDOFFILE'"
cat admin-panel/index.html
echo "ENDOFFILE"
echo ""
echo "# 3. Create dashboard.html"
echo "cat > /var/www/html/admin-panel/dashboard.html << 'ENDOFFILE'"
cat admin-panel/dashboard.html
echo "ENDOFFILE"
echo ""
echo "# 4. Set permissions"
echo "chown -R www-data:www-data /var/www/html/admin-panel"
echo "chmod -R 755 /var/www/html/admin-panel"
echo ""
echo "# 5. Test the deployment"
echo "curl -I https://kwtsocial.com/admin-panel/"