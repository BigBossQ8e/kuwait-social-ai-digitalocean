#!/usr/bin/env python3
"""Debug login functionality"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app_factory import create_app
from extensions import db
from models import User, Client

app = create_app()

with app.app_context():
    print("=== Testing Login Functionality ===\n")
    
    # Check database connection
    try:
        db.engine.execute('SELECT 1')
        print("✓ Database connected")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        exit(1)
    
    # Check if test user exists
    test_email = "test@restaurant.com"
    user = User.query.filter_by(email=test_email).first()
    
    if not user:
        print(f"✗ User {test_email} not found")
        print("\nCreating test user...")
        
        # Create test user
        user = User(
            email=test_email,
            role='client'
        )
        user.set_password('test123')
        db.session.add(user)
        db.session.flush()
        
        # Create client profile
        client = Client(
            user_id=user.id,
            company_name='Test Restaurant',
            contact_name='Test User',
            phone='+965 12345678',
            subscription_plan='trial'
        )
        db.session.add(client)
        
        try:
            db.session.commit()
            print("✓ Test user created successfully")
            print(f"  - User ID: {user.id}")
            print(f"  - Client ID: {client.id}")
        except Exception as e:
            db.session.rollback()
            print(f"✗ Failed to create user: {e}")
            exit(1)
    else:
        print(f"✓ User found: {user.email} (ID: {user.id})")
        
        # Check client profile
        client = Client.query.filter_by(user_id=user.id).first()
        if client:
            print(f"✓ Client profile found: {client.company_name} (ID: {client.id})")
        else:
            print("✗ No client profile found")
            print("Creating client profile...")
            
            client = Client(
                user_id=user.id,
                company_name='Test Restaurant',
                contact_name='Test User',
                phone='+965 12345678',
                subscription_plan='trial'
            )
            db.session.add(client)
            try:
                db.session.commit()
                print("✓ Client profile created")
            except Exception as e:
                db.session.rollback()
                print(f"✗ Failed to create client profile: {e}")
    
    # Test password
    if user.check_password('test123'):
        print("✓ Password check passed")
    else:
        print("✗ Password check failed")
        print("Resetting password...")
        user.set_password('test123')
        db.session.commit()
        print("✓ Password reset")
    
    # Test login route directly
    print("\n=== Testing Login Route ===")
    
    with app.test_client() as client:
        response = client.post('/api/auth/login', 
            json={'email': test_email, 'password': 'test123'},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.get_json()}")
        
        if response.status_code == 200:
            data = response.get_json()
            print("\n✓ Login successful!")
            print(f"Token: {data.get('access_token', '')[:50]}...")
        else:
            print("\n✗ Login failed")
            
            # Try to get more details about the error
            if app.debug:
                print("\nDebug mode is ON - check server logs for full traceback")
            else:
                print("\nTo see full error details, run server in debug mode")