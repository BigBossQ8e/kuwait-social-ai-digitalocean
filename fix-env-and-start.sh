#!/bin/bash

echo "🔧 Fixing Environment and Starting Backend..."

ssh root@209.38.176.129 << 'ENDSSH'
cd /opt/kuwait-social-ai/backend

echo "Step 1: Backing up current .env..."
cp .env .env.backup.$(date +%Y%m%d-%H%M%S)

echo ""
echo "Step 2: Checking database credentials..."
# Get database password from docker
DB_PASS=$(docker exec kuwait-social-db env | grep POSTGRES_PASSWORD | cut -d'=' -f2)
echo "Found database password: ${DB_PASS:0:3}..."

echo ""
echo "Step 3: Creating proper .env file..."
cat > .env << ENVFILE
# Flask Configuration
SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production
FLASK_DEBUG=False

# Database Configuration  
DATABASE_URL=postgresql://kuwait_user:${DB_PASS}@localhost:5432/kuwait_social_ai
SQLALCHEMY_DATABASE_URI=postgresql://kuwait_user:${DB_PASS}@localhost:5432/kuwait_social_ai

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# JWT Configuration
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ACCESS_TOKEN_EXPIRES=86400

# OpenAI Configuration (update with real key)
OPENAI_API_KEY=sk-your-openai-key-here

# Upload Configuration
UPLOAD_FOLDER=/tmp/uploads
MAX_CONTENT_LENGTH=16777216

# CORS Configuration
CORS_ORIGINS=https://kwtsocial.com,http://localhost:3000
ENVFILE

echo "✅ Created proper .env file with secure keys"

echo ""
echo "Step 4: Setting up environment and starting service..."
# Export environment variables
set -a
source .env
set +a

# Kill any existing processes
pkill -f gunicorn 2>/dev/null || true
sleep 2

# Start gunicorn
echo "Starting gunicorn..."
/usr/local/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 3 \
    --daemon \
    --log-level info \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --pid /tmp/gunicorn.pid \
    wsgi:app

echo ""
echo "Step 5: Waiting for startup..."
sleep 5

echo ""
echo "Step 6: Testing service..."
echo -n "Process check: "
if [ -f /tmp/gunicorn.pid ]; then
    if ps -p $(cat /tmp/gunicorn.pid) > /dev/null; then
        echo "✅ Gunicorn running (PID: $(cat /tmp/gunicorn.pid))"
    else
        echo "❌ Gunicorn not running"
    fi
else
    echo "❌ No PID file"
fi

echo -n "Port check: "
if netstat -tlnp 2>/dev/null | grep -q ":5000"; then
    echo "✅ Listening on port 5000"
else
    echo "❌ Not listening on port 5000"
fi

echo -n "API test: "
RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:5000/api/health)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ API responding (HTTP $HTTP_CODE)"
    echo "Response: $(echo "$RESPONSE" | head -1)"
else
    echo "❌ API not working (HTTP $HTTP_CODE)"
fi

echo ""
echo "Step 7: Checking logs for errors..."
tail -10 logs/error.log 2>/dev/null | grep -i error || echo "No recent errors in log"

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "⚠️  Important: Update OPENAI_API_KEY in .env with your real key"
ENDSSH

echo ""
echo "🌐 Testing from outside..."
sleep 2
echo -n "Website: "
curl -s https://kwtsocial.com -o /dev/null -w "%{http_code}\n"
echo -n "API Health: "
curl -s https://kwtsocial.com/api/health -w "\nHTTP: %{http_code}\n"