#!/bin/bash

echo "=== Checking Port Usage on Server ==="
echo ""

ssh root@209.38.176.129 << 'EOF'
echo "1. Checking what's using port 80..."
sudo lsof -i :80 || sudo netstat -tlnp | grep :80

echo ""
echo "2. Checking what's using port 8080..."
sudo lsof -i :8080 || sudo netstat -tlnp | grep :8080

echo ""
echo "3. Checking running containers..."
docker ps

echo ""
echo "4. Checking nginx processes..."
ps aux | grep nginx | grep -v grep
EOF