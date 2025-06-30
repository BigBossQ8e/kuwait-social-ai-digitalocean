#!/bin/bash

# Deploy Bilingual System for Kuwait Social AI
# This script deploys the translation system and updated frontend

set -e  # Exit on error

echo "🚀 Starting Kuwait Social AI Bilingual Deployment..."

# Configuration
SERVER_IP="209.38.176.129"
SERVER_USER="root"
REMOTE_PATH="/var/www/kwtsocial"
BACKUP_DIR="/var/backups/kwtsocial"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Step 1: Build React Frontend
echo ""
echo "📦 Building React Frontend..."
cd frontend-react

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    print_warning "Installing frontend dependencies..."
    npm install
fi

# Build for production
print_status "Building production bundle..."
npm run build

# Check if build was successful
if [ ! -d "dist" ]; then
    print_error "Build failed! No dist directory found."
    exit 1
fi

print_status "Frontend build completed!"

# Step 2: Prepare deployment package
echo ""
echo "📋 Preparing deployment package..."
cd ..

# Create deployment directory
DEPLOY_DIR="deploy-$(date +%Y%m%d-%H%M%S)"
mkdir -p $DEPLOY_DIR

# Copy backend files
print_status "Copying backend files..."
cp -r backend/* $DEPLOY_DIR/
rm -rf $DEPLOY_DIR/__pycache__ $DEPLOY_DIR/venv $DEPLOY_DIR/logs

# Copy frontend build
print_status "Copying frontend build..."
cp -r frontend-react/dist $DEPLOY_DIR/frontend

# Copy deployment scripts
cp deployment-scripts/update-backend.sh $DEPLOY_DIR/
cp deployment-scripts/nginx-config/kwtsocial.conf $DEPLOY_DIR/

# Create deployment info
cat > $DEPLOY_DIR/deployment-info.txt << EOF
Deployment Date: $(date)
Version: Bilingual System Update
Features:
- Database-backed translations
- Arabic/English support
- RTL layout
- Admin translation editor
EOF

# Step 3: Create remote backup
echo ""
echo "💾 Creating remote backup..."
ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
# Create backup directory
sudo mkdir -p /var/backups/kwtsocial
BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"

# Backup database
echo "Backing up database..."
cd /var/www/kwtsocial
docker-compose exec -T postgres pg_dump -U postgres kuwait_social_ai > /var/backups/kwtsocial/$BACKUP_NAME.sql

# Backup current files
echo "Backing up application files..."
sudo tar -czf /var/backups/kwtsocial/$BACKUP_NAME-files.tar.gz \
    --exclude='*.log' \
    --exclude='__pycache__' \
    --exclude='venv' \
    /var/www/kwtsocial

echo "Backup completed: $BACKUP_NAME"
ENDSSH

# Step 4: Upload new files
echo ""
echo "📤 Uploading files to server..."
tar -czf $DEPLOY_DIR.tar.gz $DEPLOY_DIR
scp $DEPLOY_DIR.tar.gz $SERVER_USER@$SERVER_IP:/tmp/

# Step 5: Deploy on server
echo ""
echo "🔧 Deploying on server..."
ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
set -e

# Extract files
cd /tmp
tar -xzf deploy-*.tar.gz
DEPLOY_DIR=$(ls -d deploy-* | grep -v tar.gz | head -1)

# Stop services
echo "Stopping services..."
cd /var/www/kwtsocial
docker-compose stop web celery

# Update backend
echo "Updating backend..."
cp -r /tmp/$DEPLOY_DIR/*.py /var/www/kwtsocial/
cp -r /tmp/$DEPLOY_DIR/models /var/www/kwtsocial/
cp -r /tmp/$DEPLOY_DIR/routes /var/www/kwtsocial/
cp -r /tmp/$DEPLOY_DIR/migrations /var/www/kwtsocial/
cp -r /tmp/$DEPLOY_DIR/scripts /var/www/kwtsocial/

# Update frontend
echo "Updating frontend..."
rm -rf /var/www/kwtsocial/static/*
cp -r /tmp/$DEPLOY_DIR/frontend/* /var/www/kwtsocial/static/

# Set permissions
chown -R www-data:www-data /var/www/kwtsocial/static

# Run database migrations
echo "Running database migrations..."
docker-compose exec -T postgres psql -U postgres -d kuwait_social_ai < /var/www/kwtsocial/migrations/add_translations_tables.sql

# Restart services
echo "Restarting services..."
docker-compose up -d web celery

# Wait for services to be ready
sleep 10

# Run translation population script
echo "Populating translations..."
docker-compose exec -T web python scripts/populate_translations.py

# Reload nginx
echo "Reloading nginx..."
docker exec kwtsocial-nginx nginx -s reload

# Clean up
rm -rf /tmp/$DEPLOY_DIR*

echo "Deployment completed successfully!"
ENDSSH

# Step 6: Verify deployment
echo ""
echo "🔍 Verifying deployment..."

# Check health endpoint
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://kwtsocial.com/api/health)
if [ "$HEALTH_CHECK" = "200" ]; then
    print_status "Backend API is healthy"
else
    print_error "Backend API health check failed (HTTP $HEALTH_CHECK)"
fi

# Check translations endpoint
TRANS_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://kwtsocial.com/api/translations?locale=en)
if [ "$TRANS_CHECK" = "200" ]; then
    print_status "Translation API is working"
else
    print_warning "Translation API returned HTTP $TRANS_CHECK"
fi

# Check frontend
FRONTEND_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://kwtsocial.com)
if [ "$FRONTEND_CHECK" = "200" ]; then
    print_status "Frontend is accessible"
else
    print_error "Frontend check failed (HTTP $FRONTEND_CHECK)"
fi

# Clean up local files
rm -rf $DEPLOY_DIR $DEPLOY_DIR.tar.gz

echo ""
echo "✅ Deployment completed!"
echo ""
echo "📝 Post-deployment checklist:"
echo "1. Test language switching on https://kwtsocial.com"
echo "2. Verify Arabic RTL layout"
echo "3. Login as admin and check translation editor"
echo "4. Test signup/login in both languages"
echo "5. Monitor error logs: docker logs kwtsocial-web"
echo ""
echo "🔄 To rollback if needed:"
echo "ssh $SERVER_USER@$SERVER_IP"
echo "cd /var/www/kwtsocial"
echo "# Restore from backup in /var/backups/kwtsocial"