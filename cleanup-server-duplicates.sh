#!/bin/bash

echo "🧹 Kuwait Social AI Server Cleanup - Duplicate Removal"
echo "===================================================="
echo ""
echo "This script will clean up duplicate files and unused Docker resources"
echo ""

SERVER_IP="209.38.176.129"
SERVER_USER="root"

read -p "Continue with cleanup? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled"
    exit 1
fi

ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'

echo "📋 Current Status Check..."
echo "========================"

echo "1. Active processes:"
ps aux | grep -E "gunicorn|python.*kuwait" | grep -v grep

echo ""
echo "2. Docker containers:"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"

echo ""
echo "3. Disk usage before cleanup:"
df -h /

echo ""
echo "🗑️  Starting Cleanup..."
echo "====================="

# 1. Remove old Docker images
echo ""
echo "1. Removing old Docker images..."
docker rmi kuwait-social-ai-backend:fixed 2>/dev/null || true
docker rmi kuwait-social-ai-backend:fixed2 2>/dev/null || true
docker rmi kuwait-social-ai-backend:fixed3 2>/dev/null || true
docker rmi kuwait-social-ai-backend:fixed4 2>/dev/null || true
docker image prune -f

# 2. Remove stopped containers (keep running ones)
echo ""
echo "2. Removing stopped containers..."
docker container prune -f

# 3. Clean up duplicate directories
echo ""
echo "3. Checking duplicate directories..."
if [ -d "/opt/kuwait-social-ai/backend-minimal" ]; then
    echo "  Moving backend-minimal to backup..."
    mv /opt/kuwait-social-ai/backend-minimal /root/backup-minimal-$(date +%Y%m%d)
fi

# 4. Clean up old backup files in the main directory
echo ""
echo "4. Cleaning old backup files..."
cd /opt/kuwait-social-ai
find . -name "*.backup*" -mtime +7 -type f -delete 2>/dev/null
find . -name "*.old" -mtime +7 -type f -delete 2>/dev/null
find . -name "*~" -type f -delete 2>/dev/null

# 5. Clean Python cache
echo ""
echo "5. Cleaning Python cache..."
find /opt/kuwait-social-ai -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find /opt/kuwait-social-ai -name "*.pyc" -delete 2>/dev/null

# 6. Clean npm cache if exists
echo ""
echo "6. Cleaning npm cache..."
cd /opt/kuwait-social-ai/frontend 2>/dev/null && npm cache clean --force 2>/dev/null || true

# 7. Organize log files
echo ""
echo "7. Organizing log files..."
cd /opt/kuwait-social-ai/backend
mkdir -p logs/archive
find logs -name "*.log" -size +100M -exec gzip {} \; 2>/dev/null
find logs -name "*.gz" -mtime +30 -delete 2>/dev/null

# 8. Create systemd service for backend
echo ""
echo "8. Creating systemd service for backend..."
cat > /etc/systemd/system/kuwait-social-backend.service << 'EOF'
[Unit]
Description=Kuwait Social AI Backend
After=network.target

[Service]
Type=forking
User=root
WorkingDirectory=/opt/kuwait-social-ai/backend
Environment="PATH=/usr/local/bin:/usr/bin"
EnvironmentFile=/opt/kuwait-social-ai/backend/.env
ExecStart=/usr/local/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --daemon --pid /tmp/gunicorn.pid --error-logfile /opt/kuwait-social-ai/backend/logs/error.log --access-logfile /opt/kuwait-social-ai/backend/logs/access.log wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PIDFile=/tmp/gunicorn.pid
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
echo "✅ Systemd service created (not started yet)"

# 9. Summary
echo ""
echo "📊 Cleanup Summary"
echo "=================="
echo "Disk usage after cleanup:"
df -h /

echo ""
echo "Docker images remaining:"
docker images | grep kuwait

echo ""
echo "Active services:"
systemctl list-units | grep -i kuwait || echo "No systemd services active yet"

echo ""
echo "✅ Cleanup Complete!"
echo ""
echo "📝 Next Steps:"
echo "1. To manage backend with systemd:"
echo "   systemctl start kuwait-social-backend"
echo "   systemctl enable kuwait-social-backend"
echo "   systemctl status kuwait-social-backend"
echo ""
echo "2. Current backend is still running as daemon"
echo "   To switch to systemd:"
echo "   pkill -f gunicorn"
echo "   systemctl start kuwait-social-backend"

ENDSSH

echo ""
echo "🎯 Cleanup completed on server $SERVER_IP"