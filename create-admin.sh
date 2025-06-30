#!/bin/bash

echo "=== Creating Admin Account for Kuwait Social AI ==="
echo ""

# SSH into the server and create admin account
ssh root@209.38.176.129 << 'EOF'
cd /root/kuwait-social-ai

echo "Creating admin account via Flask shell..."

# Create a Python script to add admin user
cat > create_admin.py << 'SCRIPT'
from backend.app_factory import create_app
from backend.models import db, User
from werkzeug.security import generate_password_hash
import sys

# Create app context
app = create_app('production')

with app.app_context():
    try:
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@kwtsocial.com').first()
        
        if admin:
            print("Admin account already exists!")
            print(f"Email: {admin.email}")
            print(f"Role: {admin.role}")
        else:
            # Create new admin user
            admin = User(
                email='admin@kwtsocial.com',
                username='admin',
                password_hash=generate_password_hash('KuwaitSocial2024!'),
                role='owner',
                is_active=True,
                full_name='System Administrator'
            )
            
            db.session.add(admin)
            db.session.commit()
            
            print("Admin account created successfully!")
            print("")
            print("Login credentials:")
            print("Email: admin@kwtsocial.com")
            print("Password: KuwaitSocial2024!")
            print("")
            print("IMPORTANT: Change this password after first login!")
            
    except Exception as e:
        print(f"Error creating admin account: {e}")
        sys.exit(1)
SCRIPT

# Run the script in the backend container
docker exec kuwait-social-backend python create_admin.py

# Clean up
rm create_admin.py

echo ""
echo "=== Admin account setup complete! ==="
echo ""
echo "You can now login at: http://209.38.176.129/login"
echo "Email: admin@kwtsocial.com"
echo "Initial Password: KuwaitSocial2024!"
echo ""
echo "⚠️  SECURITY REMINDER: Change the password immediately after first login!"
EOF