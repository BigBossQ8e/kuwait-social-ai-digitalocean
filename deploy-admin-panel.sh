#!/bin/bash

# Deploy admin panel to DigitalOcean server

REMOTE_HOST="root@kwtsocial.com"
REMOTE_PATH="/var/www/html/admin-panel"

echo "======================================"
echo "Deploying Admin Panel to Production"
echo "======================================"

# Create admin-panel directory on server
echo "Creating admin-panel directory on server..."
ssh $REMOTE_HOST "mkdir -p $REMOTE_PATH"

# Copy admin panel files
echo "Copying admin panel files..."
scp -r admin-panel/* $REMOTE_HOST:$REMOTE_PATH/

# Set proper permissions
echo "Setting permissions..."
ssh $REMOTE_HOST "chown -R www-data:www-data $REMOTE_PATH && chmod -R 755 $REMOTE_PATH"

# Update nginx configuration to serve admin panel
echo "Updating nginx configuration..."
ssh $REMOTE_HOST 'cat > /etc/nginx/sites-available/kwtsocial.com' << 'EOF'
server {
    listen 80;
    server_name kwtsocial.com www.kwtsocial.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name kwtsocial.com www.kwtsocial.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/kwtsocial.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kwtsocial.com/privkey.pem;
    
    # Strong SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    
    # Frontend (React app)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Admin Panel (static files)
    location /admin-panel {
        alias /var/www/html/admin-panel;
        try_files $uri $uri/ /admin-panel/index.html;
        
        # Security headers for admin panel
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    gzip_vary on;
    
    # Client body size for file uploads
    client_max_body_size 50M;
}
EOF

# Test nginx configuration
echo "Testing nginx configuration..."
ssh $REMOTE_HOST "nginx -t"

# Reload nginx
echo "Reloading nginx..."
ssh $REMOTE_HOST "systemctl reload nginx"

echo ""
echo "======================================"
echo "Admin Panel Deployment Complete!"
echo "======================================"
echo ""
echo "Admin panel is now available at:"
echo "https://kwtsocial.com/admin-panel/"
echo ""
echo "Test with admin credentials:"
echo "Email: admin@kwtsocial.com"
echo "Password: KuwaitSocial2024!"
echo ""