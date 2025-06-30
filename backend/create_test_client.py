#!/usr/bin/env python3
"""Create a test client user for Kuwait Social AI"""

from app_factory import create_app
from extensions import db
from models import User, Client
from werkzeug.security import generate_password_hash
from datetime import datetime

app = create_app()

with app.app_context():
    # Check if test user already exists
    existing_user = User.query.filter_by(email='test@client.com').first()
    if existing_user:
        print("Test user already exists!")
        print("Email: test@client.com")
        print("Password: password123")
    else:
        # Create test user
        test_user = User(
            email='test@client.com',
            password_hash=generate_password_hash('password123'),
            role='client',
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(test_user)
        db.session.commit()
        
        # Create associated client profile
        test_client = Client(
            user_id=test_user.id,
            business_name='Test Restaurant',
            business_name_ar='مطعم تجريبي',
            contact_number='+965 1234 5678',
            address='Kuwait City',
            subscription_status='trial',
            subscription_plan='basic',
            ai_credits_remaining=100,
            created_at=datetime.utcnow()
        )
        db.session.add(test_client)
        db.session.commit()
        
        print("✅ Test client user created successfully!")
        print("\nLogin credentials:")
        print("Email: test@client.com")
        print("Password: password123")
        print("\nBusiness: Test Restaurant")
        print("Role: client")
        print("AI Credits: 100")
        
    # Also create an admin user
    admin_user = User.query.filter_by(email='admin@kwtsocial.com').first()
    if not admin_user:
        admin_user = User(
            email='admin@kwtsocial.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(admin_user)
        db.session.commit()
        
        print("\n✅ Admin user created!")
        print("Email: admin@kwtsocial.com")
        print("Password: admin123")