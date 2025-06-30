#!/bin/bash

echo "🚀 Starting Kuwait Social AI Backend..."

ssh root@209.38.176.129 'bash -l' << 'ENDSSH'
cd /opt/kuwait-social-ai/backend

echo "1. Stopping existing processes..."
pkill -f gunicorn
sleep 2

echo "2. Loading environment..."
set -a
source .env
set +a

echo "3. Starting gunicorn..."
/usr/local/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 3 \
    --daemon \
    --pid /tmp/gunicorn.pid \
    --error-logfile logs/error.log \
    --access-logfile logs/access.log \
    wsgi:app

echo "4. Waiting for startup..."
sleep 5

echo "5. Checking status..."
if [ -f /tmp/gunicorn.pid ] && ps -p $(cat /tmp/gunicorn.pid) > /dev/null; then
    echo "✅ Gunicorn is running (PID: $(cat /tmp/gunicorn.pid))"
    echo "Workers: $(ps aux | grep -c "[g]unicorn.*worker")"
else
    echo "❌ Gunicorn failed to start"
    echo "Last 10 lines of error log:"
    tail -10 logs/error.log
fi

echo ""
echo "6. Testing API..."
echo -n "Local test: "
curl -s http://localhost:5000/api/health -w " (HTTP %{http_code})\n" || echo "Failed"

ENDSSH

echo ""
echo "7. External test..."
echo -n "Public API: "
curl -s https://kwtsocial.com/api/health -w " (HTTP %{http_code})\n"