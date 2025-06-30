#!/bin/bash

echo "🧹 Kuwait Social AI - Complete Server Cleanup"
echo "==========================================="
echo ""
echo "⚠️  WARNING: This will remove all Kuwait Social AI data!"
echo "Starting in 5 seconds... Press Ctrl+C to cancel"
sleep 5

# 1. Create backup directory
echo ""
echo "📦 Step 1: Creating final backup..."
echo "-----------------------------------"
BACKUP_DIR="/root/kuwait-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup any database data if accessible
echo "Attempting to backup database..."
docker exec kuwait-social-db pg_dump -U kuwait_user kuwait_social > "$BACKUP_DIR/database.sql" 2>/dev/null || echo "Could not backup database"

# Backup environment files
cp /root/kuwait-social-ai/.env "$BACKUP_DIR/.env" 2>/dev/null || echo "No .env file found"

# Create info file
echo "Backup created on $(date)" > "$BACKUP_DIR/backup-info.txt"
echo "Server: $(hostname)" >> "$BACKUP_DIR/backup-info.txt"
echo "Backup saved to: $BACKUP_DIR"

# 2. Stop all containers
echo ""
echo "🛑 Step 2: Stopping all Docker containers..."
echo "-------------------------------------------"
docker stop $(docker ps -aq) 2>/dev/null || echo "No containers to stop"

# 3. Remove all containers
echo ""
echo "🗑️  Step 3: Removing all Docker containers..."
echo "--------------------------------------------"
docker rm $(docker ps -aq) 2>/dev/null || echo "No containers to remove"

# 4. Remove all Docker images
echo ""
echo "🗑️  Step 4: Removing all Docker images..."
echo "-----------------------------------------"
docker rmi $(docker images -q) -f 2>/dev/null || echo "No images to remove"

# 5. Clean Docker volumes and networks
echo ""
echo "🗑️  Step 5: Cleaning Docker volumes and networks..."
echo "--------------------------------------------------"
docker volume prune -f
docker network prune -f
docker system prune -af

# 6. Remove application directories
echo ""
echo "🗑️  Step 6: Removing application directories..."
echo "----------------------------------------------"
rm -rf /root/kuwait-social-ai
rm -rf /opt/kuwait-social-ai
rm -rf /opt/kuwait-social-ai-backup
rm -f /root/kuwait-social.tar.gz

# 7. Clean nginx configurations
echo ""
echo "🔧 Step 7: Resetting nginx configuration..."
echo "------------------------------------------"
rm -f /etc/nginx/sites-enabled/kuwait-social
rm -f /etc/nginx/sites-enabled/kwtsocial.com
rm -f /etc/nginx/sites-available/kuwait-social
rm -f /etc/nginx/sites-available/kuwait-social-ai
rm -f /etc/nginx/sites-available/kwtsocial.com

# Test nginx
nginx -t

# 8. Clear system caches
echo ""
echo "🗑️  Step 8: Clearing system caches..."
echo "------------------------------------"
apt-get clean
apt-get autoclean

# 9. Show disk usage
echo ""
echo "💾 Step 9: Current disk usage..."
echo "--------------------------------"
df -h /
docker system df

# Summary
echo ""
echo "✅ CLEANUP COMPLETE!"
echo "==================="
echo "- All Docker containers removed"
echo "- All Docker images removed" 
echo "- All application directories removed"
echo "- Nginx configurations reset"
echo "- Backup saved to: $BACKUP_DIR"
echo ""
echo "🔐 Preserved:"
echo "- SSL certificates (/etc/letsencrypt/)"
echo "- System configurations"
echo "- Backup data"
echo ""
echo "The server is now clean and ready for fresh deployment!"