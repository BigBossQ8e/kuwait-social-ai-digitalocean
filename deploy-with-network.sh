#!/bin/bash

echo "=== Deploying Kuwait Social AI with Docker Network ==="
echo ""

# SSH into the server and deploy with network
ssh root@209.38.176.129 << 'EOF'
cd /root/kuwait-social-ai

echo "1. Creating Docker network..."
docker network create kuwait-social-network 2>/dev/null || true

echo ""
echo "2. Stopping existing containers..."
docker stop kuwait-social-backend kuwait-social-frontend 2>/dev/null || true
docker rm kuwait-social-backend kuwait-social-frontend 2>/dev/null || true

echo ""
echo "3. Running backend container on network..."
docker run -d \
  --name kuwait-social-backend \
  --network kuwait-social-network \
  --network-alias backend \
  -p 5000:5000 \
  -v $(pwd)/backend/.env:/app/.env:ro \
  --restart unless-stopped \
  kuwait-social-backend

echo ""
echo "4. Waiting for backend to be ready..."
sleep 10

echo ""
echo "5. Running frontend container on network..."
docker run -d \
  --name kuwait-social-frontend \
  --network kuwait-social-network \
  -p 8080:8080 \
  --restart unless-stopped \
  kuwait-social-frontend

echo ""
echo "6. Checking container status..."
docker ps | grep -E "kuwait-social-(backend|frontend)"

echo ""
echo "7. Checking backend logs..."
docker logs kuwait-social-backend --tail=10

echo ""
echo "8. Checking frontend logs..."
docker logs kuwait-social-frontend --tail=10

echo ""
echo "9. Testing services..."
echo "Backend API:"
curl -s -o /dev/null -w "  Status: %{http_code}\n" http://localhost:5000/api
echo ""
echo "Frontend:"
curl -s -o /dev/null -w "  Status: %{http_code}\n" http://localhost:8080

echo ""
echo "10. Configuring system nginx..."
# Start nginx if not running
sudo systemctl start nginx 2>/dev/null || true

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
    
    location /api {
        proxy_pass http://localhost:5000;
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

# Remove conflicting configurations
sudo rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
sudo rm -f /etc/nginx/sites-enabled/kuwait-social 2>/dev/null || true

# Enable the site
sudo ln -sf /etc/nginx/sites-available/kuwait-social /etc/nginx/sites-enabled/

# Test and reload nginx
sudo nginx -t && sudo systemctl reload nginx

echo ""
echo "=== Deployment complete! ==="
echo "Services are running:"
echo "  - Backend API: http://209.38.176.129:5000/api"
echo "  - Frontend: http://209.38.176.129"
echo "  - Domain: https://kwtsocial.com"
echo ""
echo "Both containers are connected via Docker network 'kuwait-social-network'"
EOF