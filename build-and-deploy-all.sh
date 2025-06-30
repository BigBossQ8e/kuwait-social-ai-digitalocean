#!/bin/bash

echo "=== Building and Deploying Kuwait Social AI ==="
echo ""

# SSH into the server and build/deploy everything
ssh root@209.38.176.129 << 'EOF'
cd /root/kuwait-social-ai

echo "1. Creating Docker network..."
docker network create kuwait-social-network 2>/dev/null || true

echo ""
echo "2. Building backend Docker image..."
docker build -t kuwait-social-backend ./backend

echo ""
echo "3. Building frontend Docker image..."
docker build -t kuwait-social-frontend ./frontend-react

echo ""
echo "4. Stopping existing containers..."
docker stop kuwait-social-backend kuwait-social-frontend 2>/dev/null || true
docker rm kuwait-social-backend kuwait-social-frontend 2>/dev/null || true

echo ""
echo "5. Running backend container..."
docker run -d \
  --name kuwait-social-backend \
  --network kuwait-social-network \
  --network-alias backend \
  -p 5000:5000 \
  -v $(pwd)/backend/.env:/app/.env:ro \
  --restart unless-stopped \
  kuwait-social-backend

echo ""
echo "6. Waiting for backend to be ready..."
sleep 10

echo ""
echo "7. Running frontend container..."
docker run -d \
  --name kuwait-social-frontend \
  --network kuwait-social-network \
  -p 8080:8080 \
  --restart unless-stopped \
  kuwait-social-frontend

echo ""
echo "8. Checking container status..."
docker ps | grep -E "kuwait-social-(backend|frontend)"

echo ""
echo "9. Testing services..."
echo "Backend API:"
curl -s http://localhost:5000/api 2>/dev/null || echo "  Backend not responding yet"
echo ""
echo "Frontend:"
curl -s -o /dev/null -w "  Status: %{http_code}\n" http://localhost:8080

echo ""
echo "10. Starting system nginx..."
sudo systemctl start nginx

echo ""
echo "11. Final status check..."
sleep 5
echo "Running containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(NAMES|kuwait-social)"

echo ""
echo "=== Deployment complete! ==="
echo ""
echo "Access the application at:"
echo "  - http://209.38.176.129"
echo "  - https://kwtsocial.com"
echo ""
echo "API endpoints:"
echo "  - http://209.38.176.129:5000/api"
echo ""
echo "To create an admin account, run: ./create-admin.sh"
EOF