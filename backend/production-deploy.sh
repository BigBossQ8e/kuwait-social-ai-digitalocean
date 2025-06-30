#!/bin/bash

echo "=== Production Deployment Script ==="
echo ""
echo "Run this on your production server (kwtsocial.com)"
echo ""

# 1. Install Redis (if not installed)
echo "1. Installing Redis..."
sudo apt update
sudo apt install -y redis-server
sudo systemctl enable redis
sudo systemctl start redis

# 2. Navigate to backend
cd /var/www/kuwait-social-ai/backend || cd /home/kuwait-social-ai/backend

# 3. Update .env file
echo ""
echo "2. Updating .env file..."
if [ ! -f ".env" ]; then
    if [ -f ".env.production" ]; then
        cp .env.production .env
        echo "   ✓ Created .env from .env.production"
    else
        echo "   ✗ No .env file found!"
        exit 1
    fi
fi

# Add memory storage for rate limiting (fallback if Redis fails)
if ! grep -q "RATELIMIT_STORAGE_URL" .env; then
    echo "RATELIMIT_STORAGE_URL=redis://localhost:6379/1" >> .env
fi

# 4. Install/update dependencies
echo ""
echo "3. Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# 5. Create systemd service
echo ""
echo "4. Creating systemd service..."
sudo tee /etc/systemd/system/kuwait-social-backend.service > /dev/null <<EOF
[Unit]
Description=Kuwait Social AI Backend
After=network.target postgresql.service redis.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/kuwait-social-ai/backend
Environment="PATH=/var/www/kuwait-social-ai/backend/venv/bin"
ExecStart=/var/www/kuwait-social-ai/backend/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 --timeout 120 wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 6. Start the service
echo ""
echo "5. Starting backend service..."
sudo systemctl daemon-reload
sudo systemctl enable kuwait-social-backend
sudo systemctl restart kuwait-social-backend

# 7. Check status
sleep 3
echo ""
echo "6. Checking service status..."
sudo systemctl status kuwait-social-backend --no-pager

# 8. Test the API
echo ""
echo "7. Testing API..."
curl -s http://localhost:5000/api/auth/login -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"test"}' | python3 -m json.tool

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Check the website: https://kwtsocial.com/login"