#!/usr/bin/env python3
"""Initialize database with tables and test user"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app_factory import create_app
from extensions import db
from models import User, Client

app = create_app()

with app.app_context():
    print("=== Initializing Database ===")
    
    # Create all tables
    print("Creating database tables...")
    db.create_all()
    print("✓ Tables created successfully")
    
    # Check tables
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\nTables created: {tables}")
    
    # Create test user
    print("\n=== Creating Test User ===")
    
    test_email = "test@restaurant.com"
    test_password = "password123"
    
    # Check if user exists
    existing_user = User.query.filter_by(email=test_email).first()
    if existing_user:
        print(f"User {test_email} already exists")
    else:
        # Create user
        user = User(
            email=test_email,
            role='client',
            is_active=True
        )
        user.set_password(test_password)
        db.session.add(user)
        db.session.flush()
        
        # Create client profile
        client = Client(
            user_id=user.id,
            company_name="Test Restaurant",
            contact_name="Test User",
            phone="+96512345678",
            subscription_plan="trial"
        )
        db.session.add(client)
        db.session.commit()
        
        print(f"✓ Created test user:")
        print(f"  Email: {test_email}")
        print(f"  Password: {test_password}")
        print(f"  Role: client")
        print(f"  Company: Test Restaurant")
    
    # List all users
    print("\n=== All Users ===")
    users = User.query.all()
    for user in users:
        print(f"- {user.email} ({user.role}) - Active: {user.is_active}")
    
    print("\n✓ Database initialization complete!")