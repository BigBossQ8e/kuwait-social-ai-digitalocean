#!/bin/bash

echo "=== Deploying Kuwait Social AI Frontend ==="
echo ""

# SSH into the server and deploy frontend
ssh root@209.38.176.129 << 'EOF'
cd /root/kuwait-social-ai

echo "1. Checking for services on port 80..."
# Check what's using port 80
echo "Services on port 80:"
sudo lsof -i :80 || sudo netstat -tlnp | grep :80 || true

# Stop nginx if running
sudo systemctl stop nginx 2>/dev/null || true
# Force kill any remaining nginx processes
sudo pkill -f nginx || true

# Stop all containers using port 80
echo "Stopping containers using port 80..."
docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Ports}}" | grep ":80->" | awk '{print $1}' | xargs -r docker stop
docker ps -aq --filter "name=kuwait-social-frontend" | xargs -r docker rm -f

# Double check port is free
sleep 2
if sudo lsof -i :80 > /dev/null 2>&1; then
    echo "WARNING: Port 80 is still in use!"
    sudo lsof -i :80
fi

echo ""
echo "2. Building frontend Docker image (no cache)..."
docker build --no-cache -t kuwait-social-frontend ./frontend-react

echo ""
echo "3. Running frontend container..."
docker run -d \
  --name kuwait-social-frontend \
  -p 80:8080 \
  --restart unless-stopped \
  kuwait-social-frontend

echo ""
echo "4. Checking container status..."
sleep 5
docker ps | grep kuwait-social-frontend

echo ""
echo "5. Checking frontend logs..."
docker logs kuwait-social-frontend --tail=20

echo ""
echo "6. Testing frontend access..."
curl -s -o /dev/null -w "Frontend HTTP Status: %{http_code}\n" http://localhost:80

echo ""
echo "=== Frontend deployment complete! ==="
echo "Access the application at: http://209.38.176.129"
echo "Or via domain: https://kwtsocial.com"
EOF