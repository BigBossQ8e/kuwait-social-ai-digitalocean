#!/usr/bin/env python3
"""Create admin user for Kuwait Social AI"""

from dotenv import load_dotenv
load_dotenv()

from app_factory import create_app
from extensions import db
from models import User, Admin
import getpass

app = create_app()

with app.app_context():
    print("=== Create Admin User ===")
    
    # Get admin details
    email = input("Admin email: ") or "admin@kwtsocial.com"
    full_name = input("Full name: ") or "System Administrator"
    password = getpass.getpass("Password: ") or "Admin123!"
    
    # Check if user exists
    existing = User.query.filter_by(email=email).first()
    if existing:
        print(f"❌ User {email} already exists!")
        exit(1)
    
    # Create admin user
    user = User(
        email=email,
        role='admin',
        is_active=True
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    
    # Create admin profile
    admin = Admin(
        user_id=user.id,
        full_name=full_name,
        permissions=['all']
    )
    db.session.add(admin)
    db.session.commit()
    
    print(f"\n✅ Admin user created successfully!")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"\nLogin at: https://kwtsocial.com/admin-panel")