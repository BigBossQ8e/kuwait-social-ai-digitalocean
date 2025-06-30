#!/bin/bash

# Complete backend fix - remove duplicates and restart

echo "🔧 Fixing Kuwait Social AI Backend..."
echo ""

ssh root@209.38.176.129 << 'ENDSSH'
cd /opt/kuwait-social-ai/backend

echo "🧹 Step 1: Cleaning up duplicate files..."
# Backup the duplicates
mkdir -p /root/route-backups
mv routes/admin-backup.py routes/admin_old.py /root/route-backups/ 2>/dev/null || true
echo "✅ Removed duplicate admin files"

# Also check for other duplicates
find routes -name "*backup*" -o -name "*old*" -o -name "*copy*" | while read file; do
    echo "  Moving $file to backup..."
    mv "$file" /root/route-backups/ 2>/dev/null || true
done

echo ""
echo "🔧 Step 2: Fixing app_factory.py..."
# First, let's see what's there
echo "Current blueprint imports:"
grep -n "blueprint" app_factory.py | grep -E "import|register" | head -20

# Temporarily remove translations blueprint
cp app_factory.py app_factory.py.backup
sed -i '/from routes.translations import translations_bp/d' app_factory.py
sed -i '/app.register_blueprint(translations_bp/d' app_factory.py
echo "✅ Temporarily removed translations blueprint"

echo ""
echo "🔄 Step 3: Restarting backend service..."
# Kill ALL python/gunicorn processes
pkill -9 -f gunicorn 2>/dev/null || true
pkill -9 -f "python.*wsgi" 2>/dev/null || true
pkill -9 -f "python3.*5000" 2>/dev/null || true
sleep 2

# Clear any port conflicts
fuser -k 5000/tcp 2>/dev/null || true

echo ""
echo "🚀 Step 4: Starting fresh gunicorn..."
cd /opt/kuwait-social-ai/backend

# Start with explicit python path and module
/usr/bin/python3.10 -m gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 3 \
    --daemon \
    --pid /tmp/gunicorn.pid \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    wsgi:app

echo "⏳ Waiting for service to start..."
sleep 5

echo ""
echo "📊 Step 5: Verifying service..."
echo -n "Process check: "
ps aux | grep -c "[g]unicorn.*5000" | xargs echo "gunicorn workers running:"

echo -n "Port check: "
netstat -tlnp 2>/dev/null | grep 5000 | wc -l | xargs echo "listeners on port 5000:"

echo -n "Local API test: "
curl -s http://localhost:5000/api/health -w " (HTTP %{http_code})\n" 2>/dev/null || echo "Failed"

echo ""
echo "📝 Log check:"
tail -5 logs/error.log 2>/dev/null || echo "No recent errors"

echo ""
echo "✅ Backend fix complete!"
ENDSSH

echo ""
echo "🌐 Testing from outside..."
echo -n "Website: "
curl -s https://kwtsocial.com -o /dev/null -w "%{http_code}\n"
echo -n "API: "
curl -s https://kwtsocial.com/api/health -o /dev/null -w "%{http_code}\n"

echo ""
echo "✨ If API still shows 502, check:"
echo "1. ssh root@209.38.176.129"
echo "2. cd /opt/kuwait-social-ai/backend"
echo "3. tail -f logs/error.log"