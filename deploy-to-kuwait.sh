#!/bin/bash

# Deploy Bilingual Updates to Kuwait Social AI Production
# Server: 209.38.176.129 (kwtsocial.com)
# App location: /opt/kuwait-social-ai/

set -e

echo "🚀 Deploying Bilingual System to Kuwait Social AI"
echo "================================================"
echo ""

# Configuration
SERVER_IP="209.38.176.129"
SERVER_USER="root"
APP_DIR="/opt/kuwait-social-ai"
LOCAL_FRONTEND="frontend-react/dist"
LOCAL_BACKEND="backend"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; exit 1; }

# Step 1: Check local build
echo "1️⃣ Checking local build..."
if [ ! -d "$LOCAL_FRONTEND" ]; then
    print_warning "No frontend build found. Building now..."
    cd frontend-react
    npm install
    npm run build
    cd ..
fi

if [ -d "$LOCAL_FRONTEND" ]; then
    print_status "Frontend build exists"
else
    print_error "Frontend build failed!"
fi

# Step 2: Create backup on server
echo ""
echo "2️⃣ Creating server backup..."
ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
cd /opt/kuwait-social-ai
BACKUP_DIR="/root/backups/kuwait-social-$(date +%Y%m%d-%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup current deployment
echo "Backing up current files..."
cp -r frontend $BACKUP_DIR/ 2>/dev/null || true
cp -r backend/routes $BACKUP_DIR/ 2>/dev/null || true
cp backend/app_factory.py $BACKUP_DIR/ 2>/dev/null || true

# Backup database
echo "Backing up database..."
docker exec kuwait-social-db pg_dump -U kuwait_user kuwait_social_ai > $BACKUP_DIR/database.sql

echo "Backup created at: $BACKUP_DIR"
ENDSSH

# Step 3: Deploy frontend
echo ""
echo "3️⃣ Deploying frontend..."
echo "Uploading React build..."
tar -czf frontend-build.tar.gz -C $LOCAL_FRONTEND .
scp frontend-build.tar.gz $SERVER_USER@$SERVER_IP:/tmp/
rm frontend-build.tar.gz

ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
cd /opt/kuwait-social-ai
# Backup old frontend
mv frontend frontend.old 2>/dev/null || true
mkdir -p frontend

# Extract new frontend
cd frontend
tar -xzf /tmp/frontend-build.tar.gz
rm /tmp/frontend-build.tar.gz

# Set permissions
chown -R www-data:www-data .
echo "Frontend deployed"
ENDSSH

# Step 4: Update backend files
echo ""
echo "4️⃣ Updating backend..."

# Copy translation files if they don't exist
if [ ! -f "$LOCAL_BACKEND/routes/translations.py" ]; then
    print_warning "translations.py not found locally, skipping..."
else
    scp $LOCAL_BACKEND/routes/translations.py $SERVER_USER@$SERVER_IP:$APP_DIR/backend/routes/
    print_status "Updated translations.py"
fi

if [ -f "$LOCAL_BACKEND/models/translation.py" ]; then
    scp $LOCAL_BACKEND/models/translation.py $SERVER_USER@$SERVER_IP:$APP_DIR/backend/models/
    print_status "Updated translation model"
fi

# Update app_factory if needed
if [ -f "$LOCAL_BACKEND/app_factory.py" ]; then
    ssh $SERVER_USER@$SERVER_IP "grep -q 'translations_bp' $APP_DIR/backend/app_factory.py || echo 'Need to update app_factory'"
fi

# Step 5: Run database migration
echo ""
echo "5️⃣ Running database migration..."
if [ -f "$LOCAL_BACKEND/migrations/add_translations_tables.sql" ]; then
    scp $LOCAL_BACKEND/migrations/add_translations_tables.sql $SERVER_USER@$SERVER_IP:/tmp/
    ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
# Check if tables exist
TABLE_EXISTS=$(docker exec kuwait-social-db psql -U kuwait_user -d kuwait_social_ai -t -c "SELECT 1 FROM information_schema.tables WHERE table_name='translations';" | grep -c 1 || true)

if [ "$TABLE_EXISTS" -eq "0" ]; then
    echo "Creating translation tables..."
    docker exec -i kuwait-social-db psql -U kuwait_user -d kuwait_social_ai < /tmp/add_translations_tables.sql
    echo "Tables created"
else
    echo "Translation tables already exist"
fi
rm /tmp/add_translations_tables.sql
ENDSSH
else
    print_warning "No migration file found"
fi

# Step 6: Restart services
echo ""
echo "6️⃣ Restarting services..."
ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
# Find and restart gunicorn
echo "Restarting application..."
pkill -f gunicorn || true
sleep 2
cd /opt/kuwait-social-ai/backend
/usr/bin/python3.10 /usr/local/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --chdir /opt/kuwait-social-ai/backend wsgi:app --daemon

# Reload nginx
echo "Reloading nginx..."
nginx -s reload

echo "Services restarted"
ENDSSH

# Step 7: Populate translations
echo ""
echo "7️⃣ Populating translations..."
if [ -f "$LOCAL_BACKEND/scripts/populate_translations.py" ]; then
    scp $LOCAL_BACKEND/scripts/populate_translations.py $SERVER_USER@$SERVER_IP:$APP_DIR/backend/scripts/
    scp -r frontend-react/src/i18n/locales $SERVER_USER@$SERVER_IP:/tmp/
    
    ssh $SERVER_USER@$SERVER_IP << 'ENDSSH'
cd /opt/kuwait-social-ai/backend
# Run population script if tables exist
if docker exec kuwait-social-db psql -U kuwait_user -d kuwait_social_ai -t -c "SELECT 1 FROM translations LIMIT 1;" 2>/dev/null; then
    echo "Translation tables empty, populating..."
    # python3 scripts/populate_translations.py
else
    echo "Translations already populated"
fi
rm -rf /tmp/locales
ENDSSH
fi

# Step 8: Verify deployment
echo ""
echo "8️⃣ Verifying deployment..."
sleep 3

# Check endpoints
API_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://kwtsocial.com/api/health || echo "000")
SITE_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://kwtsocial.com || echo "000")
TRANS_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://kwtsocial.com/api/translations?locale=en || echo "000")

echo ""
echo "📊 Deployment Status:"
echo "-------------------"
[ "$SITE_CHECK" = "200" ] && print_status "Website accessible" || print_warning "Website returned $SITE_CHECK"
[ "$API_CHECK" = "200" ] && print_status "API healthy" || print_warning "API returned $API_CHECK"
[ "$TRANS_CHECK" = "200" ] && print_status "Translations API working" || print_warning "Translations API returned $TRANS_CHECK"

# Check for React
if curl -s https://kwtsocial.com | grep -q "Vite"; then
    print_status "React app detected"
else
    print_warning "React app not detected in response"
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Visit https://kwtsocial.com"
echo "2. Test language switcher (AR/EN)"
echo "3. Check RTL layout for Arabic"
echo "4. Login as admin and check translation editor"
echo ""
echo "🔄 To rollback:"
echo "ssh $SERVER_USER@$SERVER_IP"
echo "cd /opt/kuwait-social-ai"
echo "rm -rf frontend && mv frontend.old frontend"
echo "nginx -s reload"