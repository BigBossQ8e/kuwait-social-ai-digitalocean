#!/bin/bash

echo "=== Installing Redis on Production Server ==="
echo "Run this script on your production server (kwtsocial.com)"
echo ""

# Update package list
echo "1. Updating package list..."
sudo apt update

# Install Redis
echo ""
echo "2. Installing Redis server..."
sudo apt install -y redis-server

# Configure Redis for production
echo ""
echo "3. Configuring Redis for production..."
sudo tee -a /etc/redis/redis.conf > /dev/null <<EOF

# Additional production settings
maxmemory 256mb
maxmemory-policy allkeys-lru
tcp-backlog 511
timeout 300
tcp-keepalive 60
EOF

# Enable and start Redis
echo ""
echo "4. Starting Redis service..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Test Redis
echo ""
echo "5. Testing Redis connection..."
if redis-cli ping | grep -q PONG; then
    echo "✓ Redis is working!"
else
    echo "✗ Redis test failed!"
    exit 1
fi

# Check Redis status
echo ""
echo "6. Redis service status:"
sudo systemctl status redis-server --no-pager

# Update backend .env file
echo ""
echo "7. Updating backend configuration..."
cd /var/www/kuwait-social-ai/backend || cd /home/kuwait-social-ai/backend || {
    echo "Backend directory not found. Trying alternative locations..."
    find / -name "kuwait-social-ai" -type d 2>/dev/null | head -5
}

# Ensure Redis URL is set correctly in .env
if [ -f ".env" ]; then
    # Update RATELIMIT_STORAGE_URL to use Redis
    sed -i 's|RATELIMIT_STORAGE_URL=memory://|RATELIMIT_STORAGE_URL=redis://localhost:6379/1|g' .env
    echo "✓ Updated .env file to use Redis"
else
    echo "⚠️  No .env file found. Make sure to set:"
    echo "   RATELIMIT_STORAGE_URL=redis://localhost:6379/1"
fi

# Restart backend service
echo ""
echo "8. Restarting backend service..."
if systemctl is-active --quiet kuwait-social-backend; then
    sudo systemctl restart kuwait-social-backend
    echo "✓ Restarted kuwait-social-backend service"
else
    echo "⚠️  No systemd service found. Restarting Gunicorn manually..."
    pkill -f gunicorn
    sleep 2
    cd /var/www/kuwait-social-ai/backend
    source venv/bin/activate
    nohup gunicorn --bind 0.0.0.0:5000 --workers 3 wsgi:application > gunicorn.log 2>&1 &
    echo "✓ Started Gunicorn in background"
fi

# Test the API
echo ""
echo "9. Testing API endpoint..."
sleep 3
if curl -s http://localhost:5000/api/auth/login -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"test"}' | grep -q "error"; then
    echo "✓ API is responding (got expected error for invalid credentials)"
else
    echo "⚠️  API test inconclusive. Check manually."
fi

echo ""
echo "=== Redis Installation Complete ==="
echo ""
echo "Redis is now running on your production server!"
echo "Your backend should now work without Redis connection errors."
echo ""
echo "Test your website: https://kwtsocial.com/login"
echo ""
echo "Useful commands:"
echo "  - Check Redis: redis-cli ping"
echo "  - Monitor Redis: redis-cli monitor"
echo "  - Redis status: sudo systemctl status redis-server"
echo "  - Backend logs: sudo journalctl -u kuwait-social-backend -f"