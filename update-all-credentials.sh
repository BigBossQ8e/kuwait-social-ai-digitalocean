#!/bin/bash

echo "🔐 Updating All Kuwait Social AI Credentials"
echo "==========================================="

ssh root@209.38.176.129 << 'ENDSSH'
cd /opt/kuwait-social-ai/backend

echo "1. Creating backup of current .env..."
BACKUP_FILE=".env.backup-complete-$(date +%Y%m%d-%H%M%S)"
cp .env $BACKUP_FILE
echo "   Backup saved as: $BACKUP_FILE"

echo ""
echo "2. Checking current database password..."
CURRENT_DB_PASS=$(grep -E "DATABASE_URL|SQLALCHEMY_DATABASE_URI" .env | head -1 | sed 's/.*kuwait_user://' | sed 's/@.*//')
echo "   Current DB password starts with: ${CURRENT_DB_PASS:0:3}..."

echo ""
echo "3. Verifying database connection..."
docker exec kuwait-social-db psql -U kuwait_user -d kuwait_social_ai -c "\dt" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Database connection working with current password"
else
    echo "   ❌ Database connection failed - may need password update"
fi

echo ""
echo "4. Checking for admin user in database..."
docker exec kuwait-social-db psql -U kuwait_user -d kuwait_social_ai -c "SELECT email, is_admin FROM users WHERE email='admin@kwtsocial.com';" 2>/dev/null

echo ""
echo "5. Current .env summary:"
echo "   OpenAI API Key: $(grep OPENAI_API_KEY .env | cut -d= -f2 | sed 's/\(sk-[^-]*-\).*\(....\)$/\1***\2/')"
echo "   Database URL: $(grep DATABASE_URL .env | sed 's/password=.*/password=****@/' | cut -d= -f2)"
echo "   Redis URL: $(grep REDIS_URL .env | cut -d= -f2)"
echo "   Flask Environment: $(grep FLASK_ENV .env | cut -d= -f2)"

echo ""
echo "6. Checking Redis connection..."
docker exec kuwait-social-redis redis-cli ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Redis is running and accessible"
else
    echo "   ❌ Redis connection failed"
fi

echo ""
echo "📝 Summary of credentials from your file:"
echo "   - Admin Email: admin@kwtsocial.com"
echo "   - Admin Password: Kuwait2025@AI!"
echo "   - Database Password: gtEtBwHptJPoObNGI1EFAmfYx"
echo "   - Redis Password: XG07Mq4BuUzIagXPIZP8G2HjP"
echo "   - OpenAI API Key: Already updated ✅"

echo ""
echo "🔧 Additional checks:"
echo "   - Gmail app password noted: fjdq bfnw naqd qumb"
echo "   - DigitalOcean API token available"
echo "   - Alternative admin email: almasaied@gmail.com"

ENDSSH

echo ""
echo "✅ Credential check complete!"
echo ""
echo "Next steps if needed:"
echo "1. Update database password if not matching"
echo "2. Create admin user if not exists"
echo "3. Configure email settings with Gmail app password"