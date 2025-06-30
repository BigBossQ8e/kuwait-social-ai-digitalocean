#!/usr/bin/env python3
"""Initialize local database with test data"""

from dotenv import load_dotenv
load_dotenv()

from app_factory import create_app
from extensions import db
from models import User, Client

app = create_app()

with app.app_context():
    print("Creating database tables...")
    db.create_all()
    
    # Create test user
    email = "test@restaurant.com"
    user = User.query.filter_by(email=email).first()
    
    if not user:
        print("Creating test user...")
        user = User(email=email, role='client')
        user.set_password('test123')
        db.session.add(user)
        db.session.flush()
        
        # Create client profile
        client = Client(
            user_id=user.id,
            company_name='Test Restaurant',
            contact_name='Test User',
            phone='+965 12345678',
            subscription_plan='trial',
            monthly_posts_limit=100,
            monthly_posts_used=0,
            ai_credits_limit=1000,
            ai_credits_used=0
        )
        db.session.add(client)
        db.session.commit()
        
        print(f"✓ Test user created: {email} / test123")
        print(f"✓ Client ID: {client.id}")
    else:
        print(f"User already exists: {email}")
    
    print("\n✓ Database initialized successfully!")
    print("\nYou can now login with:")
    print("Email: test@restaurant.com")
    print("Password: test123")