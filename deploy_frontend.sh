#!/bin/bash

echo "=== Deploying React Frontend to Production ==="
echo "Run this on your production server"
echo ""

# Find the frontend directory
echo "1. Locating frontend directory..."
FRONTEND_DIR=$(find /var/www -name "frontend-react" -type d 2>/dev/null | head -1)
if [ -z "$FRONTEND_DIR" ]; then
    FRONTEND_DIR=$(find /home -name "frontend-react" -type d 2>/dev/null | head -1)
fi

if [ -z "$FRONTEND_DIR" ]; then
    echo "❌ Frontend directory not found!"
    echo "Please specify the path to frontend-react directory"
    exit 1
fi

echo "Found frontend at: $FRONTEND_DIR"
cd "$FRONTEND_DIR"

# Install dependencies
echo ""
echo "2. Installing dependencies..."
npm install

# Build the React app
echo ""
echo "3. Building React application..."
REACT_APP_API_URL=https://kwtsocial.com/api npm run build

# Deploy to web root
echo ""
echo "4. Deploying to web server..."
sudo mkdir -p /var/www/html/app
sudo cp -r build/* /var/www/html/app/

# Update nginx to serve React app
echo ""
echo "5. Updating nginx configuration..."
sudo tee /etc/nginx/sites-available/kwtsocial-react > /dev/null <<'EOF'
location / {
    root /var/www/html/app;
    try_files $uri $uri/ /index.html;
}

location /api {
    proxy_pass http://localhost:5000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
EOF

# Test and reload nginx
echo ""
echo "6. Reloading nginx..."
sudo nginx -t && sudo systemctl reload nginx

echo ""
echo "✅ Frontend deployment complete!"
echo "Visit https://kwtsocial.com to see your React app"