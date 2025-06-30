#!/bin/bash

echo "🧹 Complete Kuwait Social AI Cleanup"
echo "===================================="
echo ""
echo "This will:"
echo "- Remove duplicate files and directories"
echo "- Consolidate log files"
echo "- Clean up old backups"
echo "- Organize the file structure"
echo ""

read -p "Proceed with complete cleanup? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled"
    exit 1
fi

ssh root@209.38.176.129 << 'ENDSSH'

echo "📁 Step 1: Creating organized backup structure..."
BACKUP_ROOT="/root/kuwait-backups"
BACKUP_DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/cleanup-$BACKUP_DATE"
mkdir -p $BACKUP_DIR

echo ""
echo "📦 Step 2: Moving old archives to backup..."
mkdir -p $BACKUP_DIR/old-archives
mv /opt/kuwait-social-ai/*.tar.gz $BACKUP_DIR/old-archives/ 2>/dev/null || true
mv /tmp/kuwait-updates.tar.gz $BACKUP_DIR/old-archives/ 2>/dev/null || true

echo ""
echo "📄 Step 3: Consolidating environment files..."
# Keep only the backend .env
if [ -f "/opt/kuwait-social-ai/.env" ]; then
    mv /opt/kuwait-social-ai/.env $BACKUP_DIR/root-env.backup
    echo "  Moved root .env to backup"
fi

echo ""
echo "📊 Step 4: Consolidating log files..."
mkdir -p /var/log/kuwait-social-ai
# Move all logs to central location
if [ -f "/root/logs/kuwait-social-ai.log" ]; then
    mv /root/logs/kuwait-social-ai.log /var/log/kuwait-social-ai/old-root.log
fi
# Link nginx logs
ln -sf /var/log/nginx/kuwait-social-ai-access.log /var/log/kuwait-social-ai/nginx-access.log 2>/dev/null || true
ln -sf /var/log/nginx/kuwait-social-ai-error.log /var/log/kuwait-social-ai/nginx-error.log 2>/dev/null || true
echo "  Logs consolidated in /var/log/kuwait-social-ai/"

echo ""
echo "🗑️ Step 5: Removing duplicate directories..."
if [ -d "/opt/kuwait-social-ai/backend-minimal" ]; then
    echo "  Moving backend-minimal to backup..."
    mv /opt/kuwait-social-ai/backend-minimal $BACKUP_DIR/
fi

echo ""
echo "🔧 Step 6: Cleaning nginx configs..."
mkdir -p $BACKUP_DIR/nginx-backups
mv /etc/nginx/sites-available/kwtsocial.com.backup* $BACKUP_DIR/nginx-backups/ 2>/dev/null || true
echo "  Old nginx configs moved to backup"

echo ""
echo "🐳 Step 7: Cleaning Docker resources..."
# Remove old images
docker images | grep "kuwait.*fixed" | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
# Remove stopped containers
docker container prune -f > /dev/null
# Clean unused volumes
docker volume prune -f > /dev/null
echo "  Docker cleaned"

echo ""
echo "🐍 Step 8: Cleaning Python artifacts..."
find /opt/kuwait-social-ai -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find /opt/kuwait-social-ai -name "*.pyc" -delete 2>/dev/null || true
find /opt/kuwait-social-ai -name "*.pyo" -delete 2>/dev/null || true
find /opt/kuwait-social-ai -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
echo "  Python artifacts cleaned"

echo ""
echo "📝 Step 9: Creating cleanup report..."
cat > $BACKUP_DIR/cleanup-report.txt << EOF
Kuwait Social AI Cleanup Report
Date: $(date)

Items moved to backup:
- Old archives: $(ls -la $BACKUP_DIR/old-archives 2>/dev/null | wc -l) files
- Duplicate .env from root
- backend-minimal directory
- Old nginx backup configs

Active configuration:
- Main app: /opt/kuwait-social-ai/
- Backend .env: /opt/kuwait-social-ai/backend/.env
- Logs: /var/log/kuwait-social-ai/
- Nginx: /etc/nginx/sites-enabled/kwtsocial.com

Services:
- Backend: Gunicorn on port 5000
- Database: Docker container (kuwait-social-db)
- Redis: Docker container (kuwait-social-redis)
EOF

echo ""
echo "🧪 Step 10: Verifying setup..."
echo "Checking services:"
echo -n "- Backend API: "
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/ || echo "Failed"
echo -n "- Website: "
curl -s -o /dev/null -w "%{http_code}" https://kwtsocial.com || echo "Failed"
echo -n "- Database: "
docker exec kuwait-social-db pg_isready > /dev/null && echo "Ready" || echo "Not ready"
echo -n "- Redis: "
docker exec kuwait-social-redis redis-cli ping > /dev/null && echo "Ready" || echo "Not ready"

echo ""
echo "📊 Final Statistics:"
echo "==================="
echo "Disk usage: $(df -h / | awk 'NR==2 {print $3 " used of " $2 " (" $5 ")"}')"
echo "Docker images: $(docker images | grep kuwait | wc -l)"
echo "Running processes: $(ps aux | grep -c "[g]unicorn")"
echo "Backup location: $BACKUP_DIR"

echo ""
echo "✅ Cleanup Complete!"
echo ""
echo "📌 Important Notes:"
echo "1. All backups saved in: $BACKUP_DIR"
echo "2. Main application in: /opt/kuwait-social-ai/"
echo "3. Logs centralized in: /var/log/kuwait-social-ai/"
echo "4. To restore any file: cp $BACKUP_DIR/<file> <original-location>"

# Create a reference file
cat > /opt/kuwait-social-ai/DEPLOYMENT-INFO.txt << EOF
Kuwait Social AI - Deployment Information
========================================
Last cleaned: $(date)

Directory Structure:
- Application: /opt/kuwait-social-ai/
- Backend: /opt/kuwait-social-ai/backend/
- Frontend: /opt/kuwait-social-ai/frontend/
- Admin Panel: /opt/kuwait-social-ai/admin-panel/

Services:
- Backend: Gunicorn on localhost:5000
- Database: PostgreSQL in Docker (kuwait-social-db)
- Redis: Redis in Docker (kuwait-social-redis)
- Web Server: Nginx (proxy to backend)

Logs:
- Application: /opt/kuwait-social-ai/backend/logs/
- Nginx: /var/log/nginx/kuwait-social-ai-*.log
- Centralized: /var/log/kuwait-social-ai/

Environment:
- Backend config: /opt/kuwait-social-ai/backend/.env

Management Commands:
- Restart backend: pkill -f gunicorn && cd /opt/kuwait-social-ai/backend && ./start.sh
- View logs: tail -f /opt/kuwait-social-ai/backend/logs/error.log
- Database shell: docker exec -it kuwait-social-db psql -U kuwait_user -d kuwait_social_ai
EOF

echo ""
echo "Created DEPLOYMENT-INFO.txt for reference"

ENDSSH

echo ""
echo "🎯 Server cleanup completed!"