#!/bin/bash

echo "=== Debugging Login Error ==="
echo ""

ssh root@209.38.176.129 << 'EOF'
echo "1. Check if database tables exist:"
docker exec kuwait-social-backend python << 'PYTHON'
from app_factory import create_app
from models import db

app = create_app('production')
with app.app_context():
    try:
        # Test database connection
        result = db.session.execute(db.text("SELECT 1"))
        print("✅ Database connection OK")
        
        # Check if users table exists
        result = db.session.execute(db.text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'users'"))
        count = result.scalar()
        if count > 0:
            print("✅ Users table exists")
            # Count users
            result = db.session.execute(db.text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()
            print(f"   Total users: {user_count}")
        else:
            print("❌ Users table does NOT exist - Creating tables...")
            db.create_all()
            print("✅ Tables created")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("   Attempting to create all tables...")
        try:
            db.create_all()
            print("✅ Tables created successfully")
        except Exception as e2:
            print(f"❌ Failed to create tables: {e2}")
PYTHON

echo ""
echo "2. Create a test user if needed:"
docker exec kuwait-social-backend python << 'PYTHON'
from app_factory import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app('production')
with app.app_context():
    try:
        # Check if any user exists
        user = User.query.first()
        if not user:
            print("No users found. Creating admin user...")
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
        else:
            print(f"✅ Users exist. First user: {user.email}")
            
        # List all users
        users = User.query.all()
        print(f"\nAll users ({len(users)}):")
        for u in users:
            print(f"  - {u.email} (role: {u.role}, active: {u.is_active})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
PYTHON

echo ""
echo "3. Test login with a simple Python script:"
docker exec kuwait-social-backend python << 'PYTHON'
import requests
import json

# Test login endpoint
url = "http://localhost:5000/api/auth/login"
data = {"email": "admin@kwtsocial.com", "password": "Admin123!"}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ Login successful!")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Login failed")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Request error: {e}")
PYTHON

echo ""
echo "4. Check the actual login route code:"
echo "Looking for login route in auth.py..."
docker exec kuwait-social-backend cat routes/auth/auth.py | grep -A 20 "@auth_bp.route('/login" || echo "Login route not found in auth.py"

echo ""
echo "=== End of debugging ==="
EOF