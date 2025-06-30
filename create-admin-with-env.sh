#!/bin/bash

echo "👤 Creating Admin User with Environment Variables"
echo "=============================================="

ssh root@209.38.176.129 << 'ENDSSH'
cd /opt/kuwait-social-ai/backend

# Load environment variables
export $(grep -v '^#' .env | xargs)

echo "Creating admin user..."
python3 << 'EOF'
import os
import sys
sys.path.append('.')

# Ensure environment variables are loaded
from dotenv import load_dotenv
load_dotenv()

from app_factory import create_app
from models import db, User
from werkzeug.security import generate_password_hash
import datetime

app = create_app()

with app.app_context():
    try:
        # Check if admin already exists
        existing_admin = User.query.filter_by(email='admin@kwtsocial.com').first()
        
        if existing_admin:
            print(f"✅ Admin user already exists: {existing_admin.email}")
            print(f"   Is admin: {existing_admin.is_admin}")
            print(f"   Created: {existing_admin.created_at}")
            
            # Update password if needed
            existing_admin.password = generate_password_hash('Kuwait2025@AI!')
            db.session.commit()
            print("   Password updated to: Kuwait2025@AI!")
        else:
            # Create new admin user
            admin = User(
                email='admin@kwtsocial.com',
                password=generate_password_hash('Kuwait2025@AI!'),
                name='Admin',
                is_admin=True,
                is_active=True,
                created_at=datetime.datetime.utcnow()
            )
            
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created successfully!")
            print(f"   Email: admin@kwtsocial.com")
            print(f"   Password: Kuwait2025@AI!")
        
        # Also check/create alternative admin
        alt_admin = User.query.filter_by(email='almasaied@gmail.com').first()
        if alt_admin:
            print(f"\n✅ Alternative admin exists: {alt_admin.email}")
            alt_admin.password = generate_password_hash('Kuwait2025@AI!')
            db.session.commit()
            print("   Password updated")
        else:
            alt_admin = User(
                email='almasaied@gmail.com',
                password=generate_password_hash('Kuwait2025@AI!'),
                name='Al Masaied',
                is_admin=True,
                is_active=True,
                created_at=datetime.datetime.utcnow()
            )
            db.session.add(alt_admin)
            db.session.commit()
            print("\n✅ Alternative admin created: almasaied@gmail.com")
        
        # List all admin users
        print("\n📋 All admin users:")
        admins = User.query.filter_by(is_admin=True).all()
        for admin in admins:
            print(f"   - {admin.email} (ID: {admin.id}, Active: {admin.is_active})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
EOF

echo ""
echo "✅ Admin setup complete!"
echo ""
echo "🌐 Login URLs:"
echo "   Main site: https://kwtsocial.com"
echo "   Admin panel: https://kwtsocial.com/admin"
echo ""
echo "📧 Admin Credentials:"
echo "   Primary: admin@kwtsocial.com / Kuwait2025@AI!"
echo "   Alternative: almasaied@gmail.com / Kuwait2025@AI!"

ENDSSH