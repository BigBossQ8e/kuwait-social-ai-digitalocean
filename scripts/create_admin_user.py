#!/usr/bin/env python3
"""
Create initial admin user for Kuwait Social AI platform
Run this on the server after deployment
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.models import db, User
from werkzeug.security import generate_password_hash
import getpass

def create_admin_user():
    app = create_app()
    
    with app.app_context():
        print("Creating admin user for Kuwait Social AI...")
        
        # Get user details
        email = input("Enter admin email: ")
        username = input("Enter admin username: ")
        company = input("Enter company name: ")
        password = getpass.getpass("Enter password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        
        if password != confirm_password:
            print("Passwords don't match!")
            return
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"User with email {email} already exists!")
            return
        
        # Create admin user
        admin_user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password),
            role='admin',
            company_name=company,
            is_active=True,
            is_verified=True
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"✅ Admin user created successfully!")
        print(f"Email: {email}")
        print(f"Role: admin")
        print(f"You can now login at https://kwtsocial.com")

if __name__ == "__main__":
    create_admin_user()