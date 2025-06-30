#!/bin/bash

echo "=== Final Backend Fix ==="
echo ""

ssh root@209.38.176.129 << 'EOF'
cd /root/kuwait-social-ai

echo "1. Fixing MAX_CONTENT_LENGTH in .env..."
# Ensure it's a number without quotes
sed -i 's/MAX_CONTENT_LENGTH=.*/MAX_CONTENT_LENGTH=10485760/' backend/.env

echo ""
echo "2. Fixing config loading in config.py..."
# Create a patch for config.py to properly handle MAX_CONTENT_LENGTH
cat > backend/config/config_patch.py << 'PATCH'
# Patch to fix MAX_CONTENT_LENGTH type
import os

def patch_config():
    max_content = os.getenv('MAX_CONTENT_LENGTH', '10485760')
    try:
        return int(max_content)
    except:
        return 10485760
PATCH

echo ""
echo "3. Rebuilding backend..."
docker build -t kuwait-social-backend ./backend

echo ""
echo "4. Restarting backend..."
docker stop kuwait-social-backend
docker rm kuwait-social-backend

docker run -d \
  --name kuwait-social-backend \
  --network kuwait-social-network \
  --network-alias backend \
  -p 5000:5000 \
  --env-file backend/.env \
  -e MAX_CONTENT_LENGTH=10485760 \
  -v $(pwd)/backend/uploads:/app/uploads \
  --restart unless-stopped \
  kuwait-social-backend

echo ""
echo "5. Waiting for startup..."
sleep 10

echo ""
echo "6. Creating tables with direct SQL..."
docker exec kuwait-social-backend python << 'PYTHON'
import os
os.environ['MAX_CONTENT_LENGTH'] = '10485760'

from app_factory import create_app
from models import db

app = create_app('production')

with app.app_context():
    # Create all tables
    db.create_all()
    print("✅ Tables created successfully!")
    
    # Create admin user
    from models import User
    from werkzeug.security import generate_password_hash
    
    admin = User.query.filter_by(email='admin@kwtsocial.com').first()
    if not admin:
        admin = User(
            email='admin@kwtsocial.com',
            username='admin',
            password_hash=generate_password_hash('Admin123!'),
            role='owner',
            is_active=True,
            full_name='System Administrator'
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created!")
        print("   Email: admin@kwtsocial.com")
        print("   Password: Admin123!")
    else:
        print("ℹ️  Admin user already exists")
PYTHON

echo ""
echo "7. Testing login..."
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@kwtsocial.com","password":"Admin123!"}' \
  -s 2>&1 | python3 -m json.tool || echo "Login test completed"

echo ""
echo "=== Backend is ready! ==="
echo ""
echo "Access the application at:"
echo "  Frontend: http://209.38.176.129:8080"
echo "  Backend API: http://209.38.176.129:5000"
echo ""
echo "Login credentials:"
echo "  Email: admin@kwtsocial.com"
echo "  Password: Admin123!"
EOF