#!/bin/bash

echo "=== Fixing Backend 500 Error ==="
echo ""

ssh root@209.38.176.129 << 'EOF'
cd /root/kuwait-social-ai/backend

echo "1. First, let's see the exact error:"
docker logs kuwait-social-backend 2>&1 | grep -A 20 "TypeError:" | tail -30

echo ""
echo "2. The issue is MAX_CONTENT_LENGTH being compared as string vs int. Let's fix config.py:"
cat > config/fix_config.py << 'PYTHON'
import os

# Fix for config.py - ensuring MAX_CONTENT_LENGTH is an integer
original_file = 'config.py'
backup_file = 'config.py.backup'

# Read the original file
with open(original_file, 'r') as f:
    content = f.read()

# Backup the original
with open(backup_file, 'w') as f:
    f.write(content)

# Fix the MAX_CONTENT_LENGTH line
fixed_content = content.replace(
    "MAX_CONTENT_LENGTH = os.getenv('MAX_CONTENT_LENGTH', '10485760')",
    "MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '10485760'))"
)

# Write the fixed content
with open(original_file, 'w') as f:
    f.write(fixed_content)

print("✅ Fixed MAX_CONTENT_LENGTH in config.py")
PYTHON

cd config && python fix_config.py && cd ..

echo ""
echo "3. Rebuild the backend image:"
cd /root/kuwait-social-ai
docker build -t kuwait-social-backend ./backend

echo ""
echo "4. Stop and remove old container:"
docker stop kuwait-social-backend
docker rm kuwait-social-backend

echo ""
echo "5. Run new container with fixed config:"
docker run -d \
  --name kuwait-social-backend \
  --network kuwait-social-network \
  --network-alias backend \
  -p 5000:5000 \
  --env-file backend/.env \
  -v $(pwd)/backend/uploads:/app/uploads \
  --restart unless-stopped \
  kuwait-social-backend

echo ""
echo "6. Wait for startup:"
sleep 10

echo ""
echo "7. Create database tables:"
docker exec kuwait-social-backend python << 'CREATEDB'
from app_factory import create_app
from models import db

app = create_app('production')
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # List tables
        result = db.session.execute(db.text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
        tables = [row[0] for row in result]
        print(f"Tables in database: {', '.join(tables)}")
    except Exception as e:
        print(f"Error: {e}")
CREATEDB

echo ""
echo "8. Create admin user:"
docker exec kuwait-social-backend python << 'CREATEADMIN'
from app_factory import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app('production')
with app.app_context():
    try:
        # Check if admin exists
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
            print("✅ Admin user created successfully!")
        else:
            print("ℹ️  Admin user already exists")
    except Exception as e:
        print(f"Error creating admin: {e}")
CREATEADMIN

echo ""
echo "9. Test login endpoint:"
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@kwtsocial.com","password":"Admin123!"}' \
  -s | python3 -m json.tool

echo ""
echo "=== Backend Fixed! ==="
EOF