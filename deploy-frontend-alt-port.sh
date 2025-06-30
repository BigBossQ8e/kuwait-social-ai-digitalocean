#!/bin/bash

echo "=== Deploying Kuwait Social AI Frontend (Alternative Port 8080) ==="
echo ""

# SSH into the server and deploy frontend
ssh root@209.38.176.129 << 'EOF'
cd /root/kuwait-social-ai

echo "1. Stopping existing frontend container..."
docker stop kuwait-social-frontend 2>/dev/null || true
docker rm kuwait-social-frontend 2>/dev/null || true

echo ""
echo "2. Running frontend container on port 8080..."
docker run -d \
  --name kuwait-social-frontend \
  -p 8080:8080 \
  --restart unless-stopped \
  kuwait-social-frontend

echo ""
echo "3. Checking container status..."
sleep 5
docker ps | grep kuwait-social-frontend

echo ""
echo "4. Checking frontend logs..."
docker logs kuwait-social-frontend --tail=20

echo ""
echo "5. Testing frontend access..."
curl -s -o /dev/null -w "Frontend HTTP Status: %{http_code}\n" http://localhost:8080

echo ""
echo "6. Setting up nginx proxy from port 80 to 8080..."
# Create nginx site configuration
sudo tee /etc/nginx/sites-available/kuwait-social > /dev/null << 'NGINX'
server {
    listen 80;
    server_name kwtsocial.com www.kwtsocial.com 209.38.176.129;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
NGINX

# Enable the site
sudo ln -sf /etc/nginx/sites-available/kuwait-social /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true

# Test and reload nginx
sudo nginx -t && sudo systemctl reload nginx

echo ""
echo "=== Frontend deployment complete! ==="
echo "Frontend is running on port 8080, proxied through nginx on port 80"
echo "Access the application at:"
echo "  - http://209.38.176.129"
echo "  - https://kwtsocial.com"
EOF