#!/usr/bin/env python
"""
Create a test admin user for testing the admin panel
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_factory import create_app
from models import db, User, Admin
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_test_admin():
    """Create a test admin user"""
    app = create_app('development')
    
    with app.app_context():
        # Check if admin already exists
        existing_user = User.query.filter_by(email='admin@example.com').first()
        if existing_user:
            print("Admin user already exists")
            
            # Check if admin profile exists
            if not existing_user.admin_profile:
                admin = Admin(
                    user_id=existing_user.id,
                    full_name='Test Admin',
                    permissions={'all': True, 'role': 'owner'}
                )
                db.session.add(admin)
                db.session.commit()
                print("Added admin profile to existing user")
            else:
                print(f"Admin profile exists with permissions: {existing_user.admin_profile.permissions}")
            return
        
        # Create new admin user
        user = User(
            email='admin@example.com',
            password_hash=generate_password_hash('password'),
            is_active=True,
            role='admin',
            created_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        
        # Create admin profile
        admin = Admin(
            user_id=user.id,
            full_name='Test Admin',
            permissions={'all': True, 'role': 'owner'}  # Store role in permissions
        )
        db.session.add(admin)
        db.session.commit()
        
        print(f"Created test admin user:")
        print(f"Email: admin@example.com")
        print(f"Password: password")
        print(f"Role: owner")
        print(f"User ID: {user.id}")

if __name__ == '__main__':
    create_test_admin()