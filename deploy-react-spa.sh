#!/bin/bash

echo "=== Deploying React SPA to Production ==="
echo ""

# Configuration
SERVER="root@kuwait-social-ai-1750866347"
LOCAL_BUILD_DIR="./frontend-react/build"
REMOTE_WEB_DIR="/var/www/html"

# Step 1: Build React app locally
echo "1. Building React application..."
cd frontend-react

# Ensure dependencies are installed
npm install

# Build with production API URL
REACT_APP_API_URL=https://kwtsocial.com/api npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    echo "❌ Build failed! Check for errors above."
    exit 1
fi

echo "✅ Build successful!"

# Step 2: Create deployment package
echo ""
echo "2. Creating deployment package..."
cd ..
tar -czf react-build.tar.gz -C frontend-react/build .

# Step 3: Upload to server
echo ""
echo "3. Uploading to production server..."
scp react-build.tar.gz $SERVER:/tmp/

# Step 4: Deploy on server
echo ""
echo "4. Deploying on server..."
ssh $SERVER << 'ENDSSH'
# Backup existing files
echo "Backing up existing files..."
cd /var/www/html
tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz .

# Clean directory (keeping backups)
echo "Cleaning web directory..."
find . -maxdepth 1 ! -name 'backup-*.tar.gz' ! -name '.' -exec rm -rf {} \;

# Extract new build
echo "Extracting new React build..."
tar -xzf /tmp/react-build.tar.gz -C .

# Set correct permissions
echo "Setting permissions..."
chown -R www-data:www-data .
chmod -R 755 .

# Update nginx configuration for SPA
echo "Updating nginx configuration..."
cat > /etc/nginx/sites-available/kwtsocial.com << 'EOF'
server {
    listen 80;
    server_name kwtsocial.com www.kwtsocial.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name kwtsocial.com www.kwtsocial.com;

    ssl_certificate /etc/letsencrypt/live/kwtsocial.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kwtsocial.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # React SPA
    location / {
        root /var/www/html;
        try_files $uri /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Test nginx configuration
echo "Testing nginx configuration..."
nginx -t

# Reload nginx
echo "Reloading nginx..."
systemctl reload nginx

# Clean up
rm /tmp/react-build.tar.gz

echo ""
echo "✅ Deployment complete!"
echo ""
echo "The React SPA is now live at https://kwtsocial.com"
echo ""
echo "Test URLs:"
echo "  - https://kwtsocial.com/ (should redirect to login)"
echo "  - https://kwtsocial.com/login"
echo "  - https://kwtsocial.com/dashboard (requires login)"
echo "  - https://kwtsocial.com/admin (requires admin login)"
ENDSSH

# Clean up local file
rm react-build.tar.gz

echo ""
echo "🎉 React SPA deployment completed!"
echo ""
echo "Next steps:"
echo "1. Test login at https://kwtsocial.com/login"
echo "2. Verify all routes work correctly"
echo "3. Check browser console for any errors"
echo "4. Monitor nginx and backend logs"