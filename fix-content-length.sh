#!/bin/bash

echo "🔧 Fixing MAX_CONTENT_LENGTH type issue..."

ssh root@209.38.176.129 << 'ENDSSH'
cd /opt/kuwait-social-ai/backend

echo "1. Checking current configuration..."
grep -n "MAX_CONTENT_LENGTH" config/config.py

echo ""
echo "2. Fixing the type conversion issue..."
# Backup the config file
cp config/config.py config/config.py.backup-$(date +%Y%m%d-%H%M%S)

# Fix MAX_CONTENT_LENGTH to be an integer
sed -i 's/MAX_CONTENT_LENGTH = os.getenv("MAX_CONTENT_LENGTH", .*/MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "16777216"))/' config/config.py

echo "Fixed line:"
grep "MAX_CONTENT_LENGTH" config/config.py

echo ""
echo "3. Restarting backend..."
pkill -f gunicorn
sleep 2

export $(grep -v '^#' .env | xargs)
/usr/local/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --daemon --pid /tmp/gunicorn.pid wsgi:app

sleep 5

echo ""
echo "4. Testing login endpoint..."
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@kwtsocial.com","password":"Kuwait2025@AI!"}' \
  -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "✅ Fix applied!"

ENDSSH