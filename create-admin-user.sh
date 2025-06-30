#!/bin/bash

echo "👤 Creating Admin User for Kuwait Social AI"
echo "=========================================="

ssh root@209.38.176.129 << 'ENDSSH'
cd /opt/kuwait-social-ai/backend

echo "Creating Python script to add admin user..."
cat > create_admin.py << 'EOF'
import sys
sys.path.append('.')

from app_factory import create_app
from models import db, User
from werkzeug.security import generate_password_hash
import datetime

app = create_app()

with app.app_context():
    # Check if admin already exists
    existing_admin = User.query.filter_by(email='admin@kwtsocial.com').first()
    
    if existing_admin:
        print(f"Admin user already exists: {existing_admin.email}")
        print(f"Is admin: {existing_admin.is_admin}")
        print(f"Created: {existing_admin.created_at}")
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
        
        # Also create with alternative email if needed
        alt_admin = User.query.filter_by(email='almasaied@gmail.com').first()
        if not alt_admin:
            alt_admin = User(
                email='almasaied@gmail.com',
                password=generate_password_hash('Kuwait2025@AI!'),
                name='Al Masaied',
                is_admin=True,
                is_active=True,
                created_at=datetime.datetime.utcnow()
            )
            db.session.add(alt_admin)
            print("Created alternative admin: almasaied@gmail.com")
        
        db.session.commit()
        print("✅ Admin user created successfully!")
        print(f"Email: admin@kwtsocial.com")
        print(f"Password: Kuwait2025@AI!")
        
    # List all admin users
    print("\nAll admin users:")
    admins = User.query.filter_by(is_admin=True).all()
    for admin in admins:
        print(f"- {admin.email} (ID: {admin.id})")
EOF

echo ""
echo "Running admin creation script..."
python3 create_admin.py

# Clean up
rm create_admin.py

echo ""
echo "✅ Admin user setup complete!"
echo ""
echo "You can now login at:"
echo "- https://kwtsocial.com/admin"
echo "- Email: admin@kwtsocial.com"
echo "- Password: Kuwait2025@AI!"
echo ""
echo "Alternative admin:"
echo "- Email: almasaied@gmail.com"
echo "- Password: Kuwait2025@AI!"

ENDSSH