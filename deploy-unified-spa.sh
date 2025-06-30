#!/bin/bash

echo "=== Deploying Unified React SPA to Production ==="
echo ""

# Configuration
SERVER="root@209.38.176.129"
LOCAL_BUILD_DIR="./frontend-react/dist"
REMOTE_WEB_DIR="/var/www/html"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Step 1: Check if we're in the right directory
if [ ! -d "frontend-react" ]; then
    print_error "frontend-react directory not found. Please run this script from the digitalocean-latest directory."
    exit 1
fi

# Step 2: Build React app locally
print_status "Building React application..."
cd frontend-react

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    print_warning "Node modules not found. Installing dependencies..."
    npm install
fi

# Build with production API URL
print_status "Building for production..."
VITE_API_URL=https://kwtsocial.com npm run build

# Check if build was successful
if [ ! -d "dist" ]; then
    print_error "Build failed! Check for errors above."
    exit 1
fi

print_status "Build successful!"

# Step 3: Create deployment package
cd ..
print_status "Creating deployment package..."
tar -czf react-spa-${TIMESTAMP}.tar.gz -C frontend-react/dist .

# Step 4: Upload to server
print_status "Uploading to production server..."
scp react-spa-${TIMESTAMP}.tar.gz $SERVER:/tmp/

# Step 5: Deploy on server and update nginx
print_status "Deploying on server..."
ssh $SERVER << ENDSSH
set -e

# Colors for server output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}[✓]${NC} Connected to production server"

# Backup existing files
echo -e "${GREEN}[✓]${NC} Backing up existing files..."
cd /var/www/html
if [ -n "\$(ls -A 2>/dev/null)" ]; then
    tar -czf backup-${TIMESTAMP}.tar.gz * || true
    echo -e "${GREEN}[✓]${NC} Backup created: backup-${TIMESTAMP}.tar.gz"
fi

# Clean directory (keeping only backups)
echo -e "${GREEN}[✓]${NC} Cleaning web directory..."
find . -maxdepth 1 ! -name 'backup-*.tar.gz' ! -name '.' -exec rm -rf {} \; || true

# Extract new build
echo -e "${GREEN}[✓]${NC} Extracting new React build..."
tar -xzf /tmp/react-spa-${TIMESTAMP}.tar.gz -C .

# Set correct permissions
echo -e "${GREEN}[✓]${NC} Setting permissions..."
chown -R www-data:www-data .
chmod -R 755 .

# Update nginx configuration for SPA
echo -e "${GREEN}[✓]${NC} Updating nginx configuration..."
cat > /etc/nginx/sites-available/kwtsocial.com << 'EOF'
server {
    listen 80;
    server_name kwtsocial.com www.kwtsocial.com;
    return 301 https://\$server_name\$request_uri;
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

    # React SPA root
    root /var/www/html;
    index index.html;

    # Handle React routes
    location / {
        try_files \$uri /index.html;
    }

    # Backend API proxy
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Disable buffering for SSE
        proxy_buffering off;
        proxy_cache off;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Disable caching for index.html
    location = /index.html {
        add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0";
    }

    # Disable caching for service worker
    location = /service-worker.js {
        add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0";
    }
}
EOF

# Test nginx configuration
echo -e "${GREEN}[✓]${NC} Testing nginx configuration..."
nginx -t

if [ \$? -eq 0 ]; then
    # Reload nginx
    echo -e "${GREEN}[✓]${NC} Reloading nginx..."
    systemctl reload nginx
    
    # Clean up
    rm /tmp/react-spa-${TIMESTAMP}.tar.gz
    
    echo -e "${GREEN}[✓]${NC} Deployment complete!"
else
    echo -e "${RED}[✗]${NC} Nginx configuration test failed!"
    exit 1
fi

# Display test URLs
echo ""
echo "====================================="
echo "🎉 React SPA deployed successfully!"
echo "====================================="
echo ""
echo "Test URLs:"
echo "  - https://kwtsocial.com/ (redirects to login)"
echo "  - https://kwtsocial.com/login (universal login)"
echo "  - https://kwtsocial.com/dashboard (client/owner dashboard)"
echo "  - https://kwtsocial.com/admin (admin dashboard)"
echo ""
echo "User flows:"
echo "  - Client: Login → Dashboard"
echo "  - Admin: Login → Admin Panel"
echo "  - Owner: Login → Owner Dashboard"
echo ""
ENDSSH

# Clean up local file
rm react-spa-${TIMESTAMP}.tar.gz

echo ""
print_status "Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Test login at https://kwtsocial.com/login"
echo "2. Verify role-based routing works correctly"
echo "3. Check browser console for any errors"
echo "4. Monitor nginx access and error logs"
echo ""
echo "To view logs on server:"
echo "  - Nginx access: tail -f /var/log/nginx/access.log"
echo "  - Nginx errors: tail -f /var/log/nginx/error.log"
echo "  - Backend logs: systemctl status gunicorn"