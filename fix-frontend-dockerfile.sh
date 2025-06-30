#!/bin/bash

echo "=== Fixing Frontend Dockerfile on Server ==="
echo ""

# SSH into the server and fix the Dockerfile
ssh root@209.38.176.129 << 'EOF'
cd /root/kuwait-social-ai/frontend-react

echo "1. Backing up current Dockerfile..."
cp Dockerfile Dockerfile.backup

echo ""
echo "2. Fixing the npm install command in Dockerfile..."
sed -i 's/RUN npm ci --only=production/RUN npm ci/' Dockerfile

echo ""
echo "3. Fixing the nginx config path..."
sed -i 's/COPY nginx.conf \/etc\/nginx\/nginx.conf/COPY nginx.digitalocean.conf \/etc\/nginx\/conf.d\/default.conf/' Dockerfile

echo ""
echo "4. Fixing the exposed port..."
sed -i 's/EXPOSE 80/EXPOSE 8080/' Dockerfile

echo ""
echo "5. Fixing the health check port..."
sed -i 's/CMD curl -f http:\/\/localhost\/health/CMD curl -f http:\/\/localhost:8080\/health/' Dockerfile

echo ""
echo "6. Showing the updated Dockerfile..."
echo "----------------------------------------"
cat Dockerfile | grep -E "(RUN npm|COPY nginx|EXPOSE|CMD curl)"
echo "----------------------------------------"

echo ""
echo "=== Dockerfile fixed! Now run ./deploy-frontend.sh ==="
EOF