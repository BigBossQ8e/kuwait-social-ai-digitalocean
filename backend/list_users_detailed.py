#!/usr/bin/env python3
"""List all users with detailed information"""

from dotenv import load_dotenv
load_dotenv()

from app_factory import create_app
from extensions import db
from models import User, Client, Admin, Owner

app = create_app()

with app.app_context():
    users = User.query.all()
    print(f"Found {len(users)} users:\n")
    
    for user in users:
        print(f"{'='*50}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Active: {user.is_active}")
        print(f"Created: {user.created_at}")
        print(f"Last Login: {user.last_login}")
        
        # Get profile details based on role
        if user.role == 'client' and user.client_profile:
            client = user.client_profile
            print(f"\nClient Details:")
            print(f"  Company: {client.company_name}")
            print(f"  Contact: {client.contact_name}")
            print(f"  Plan: {client.subscription_plan}")
            print(f"  Status: {client.subscription_status}")
            print(f"  Posts Used: {client.monthly_posts_used}/{client.monthly_posts_limit}")
            
        elif user.role == 'admin' and user.admin_profile:
            admin = user.admin_profile
            print(f"\nAdmin Details:")
            print(f"  Full Name: {admin.full_name}")
            print(f"  Phone: {admin.phone}")
            print(f"  Permissions: {admin.permissions}")
            
        elif user.role == 'owner' and user.owner_profile:
            owner = user.owner_profile
            print(f"\nOwner Details:")
            print(f"  Company: {owner.company_name}")
            print(f"  Phone: {owner.phone}")
    
    print(f"{'='*50}")
    
    # Also check for any users without profiles
    print("\nChecking for users without profiles...")
    
    users_without_profiles = []
    for user in users:
        if user.role == 'client' and not user.client_profile:
            users_without_profiles.append(f"Client: {user.email}")
        elif user.role == 'admin' and not user.admin_profile:
            users_without_profiles.append(f"Admin: {user.email}")
        elif user.role == 'owner' and not user.owner_profile:
            users_without_profiles.append(f"Owner: {user.email}")
    
    if users_without_profiles:
        print("Users without profiles:")
        for u in users_without_profiles:
            print(f"  - {u}")
    else:
        print("All users have proper profiles ✓")