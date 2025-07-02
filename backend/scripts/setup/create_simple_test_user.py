#!/usr/bin/env python3
"""Create a test user - simple version"""

from app_factory import create_app
from extensions import db
from models import User, Client
from datetime import datetime
import hashlib

app = create_app()

def simple_hash_password(password):
    """Simple password hashing for test purposes"""
    # For development only - uses simple SHA256
    return hashlib.sha256(password.encode()).hexdigest()

with app.app_context():
    # Check if test user already exists
    existing_user = User.query.filter_by(email='test@client.com').first()
    if existing_user:
        print("Test user already exists!")
        print("Email: test@client.com")
        print("Deleting and recreating...")
        
        # Delete existing user and client
        if existing_user.client:
            db.session.delete(existing_user.client)
        db.session.delete(existing_user)
        db.session.commit()
    
    # Create test user with simple password hash
    test_user = User(
        email='test@client.com',
        password_hash=simple_hash_password('password123'),
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
    print("\nNote: Using simple password hashing for development")
    
    # List all users
    print("\n📋 All users in database:")
    all_users = User.query.all()
    for user in all_users:
        print(f"  - {user.email} ({user.role})")