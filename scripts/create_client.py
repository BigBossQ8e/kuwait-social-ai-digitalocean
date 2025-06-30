#!/usr/bin/env python3
"""
Create client users for Kuwait Social AI platform
Run this to onboard new clients
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app
from backend.models import db, User, Subscription
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import getpass

def create_client():
    app = create_app()
    
    with app.app_context():
        print("=== Kuwait Social AI - Client Onboarding ===\n")
        
        # Get client details
        company = input("Company name: ")
        email = input("Client email: ")
        username = input("Username: ")
        phone = input("Phone number (optional): ")
        
        # Package selection
        print("\nAvailable packages:")
        print("1. Starter (19 KWD/month) - Instagram only, 30 posts/month")
        print("2. Professional (29 KWD/month) - All platforms, unlimited posts, AI features")
        print("3. Enterprise (49 KWD/month) - Everything + team accounts, API access")
        
        package = input("\nSelect package (1-3): ")
        packages = {
            '1': {'name': 'Starter', 'price': 19, 'plan_type': 'starter'},
            '2': {'name': 'Professional', 'price': 29, 'plan_type': 'professional'},
            '3': {'name': 'Enterprise', 'price': 49, 'plan_type': 'enterprise'}
        }
        
        selected_package = packages.get(package, packages['2'])
        
        # Set password
        print("\nSet client password:")
        password = getpass.getpass("Password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        
        if password != confirm_password:
            print("❌ Passwords don't match!")
            return
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"❌ User with email {email} already exists!")
            return
        
        # Create client user
        client_user = User(
            email=email,
            username=username,
            password_hash=generate_password_hash(password),
            role='client',
            company_name=company,
            phone=phone if phone else None,
            is_active=True,
            is_verified=True,
            preferred_language='en',
            timezone='Asia/Kuwait'
        )
        
        db.session.add(client_user)
        db.session.flush()  # Get user ID
        
        # Create subscription
        subscription = Subscription(
            user_id=client_user.id,
            plan_type=selected_package['plan_type'],
            status='active',
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            price=selected_package['price'],
            currency='KWD',
            auto_renew=True
        )
        
        db.session.add(subscription)
        db.session.commit()
        
        print(f"\n✅ Client created successfully!")
        print(f"Company: {company}")
        print(f"Email: {email}")
        print(f"Package: {selected_package['name']} ({selected_package['price']} KWD/month)")
        print(f"\nClient can now login at https://kwtsocial.com")
        print(f"Login credentials sent to: {email}")

if __name__ == "__main__":
    create_client()