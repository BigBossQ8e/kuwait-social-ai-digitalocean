#!/bin/bash

echo "=== Restarting Backend with Fixed Structure ==="
echo ""

ssh root@209.38.176.129 << 'EOF'
cd /root/kuwait-social-ai

echo "1. Rebuilding backend image with updated wsgi.py..."
docker build -t kuwait-social-backend ./backend

echo ""
echo "2. Stopping old container..."
docker stop kuwait-social-backend
docker rm kuwait-social-backend

echo ""
echo "3. Running new container..."
docker run -d \
  --name kuwait-social-backend \
  --network kuwait-social-network \
  --network-alias backend \
  -p 5000:5000 \
  --env-file backend/.env \
  -v $(pwd)/backend/uploads:/app/uploads \
  --restart unless-stopped \
  kuwait-social-backend

echo ""
echo "4. Waiting for startup..."
sleep 10

echo ""
echo "5. Checking logs..."
docker logs kuwait-social-backend --tail=30

echo ""
echo "6. Creating database tables..."
docker exec kuwait-social-backend python -c "
import sys
sys.path.insert(0, '/app')
from app_factory import create_app
from models import db

app = create_app('production')
with app.app_context():
    db.create_all()
    print('Database tables created!')
"

echo ""
echo "7. Testing endpoints..."
echo "Root endpoint:"
curl -s http://localhost:5000/ | head -5

echo ""
echo "Login endpoint test:"
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  -w "\nHTTP Status: %{http_code}\n" 2>/dev/null

echo ""
echo "=== Backend restart complete! ==="
EOF