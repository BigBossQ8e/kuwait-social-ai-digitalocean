#!/usr/bin/env python3
"""Check for all users mentioned in WORKING-CREDENTIALS.md"""

from dotenv import load_dotenv
load_dotenv()

from app_factory import create_app
from extensions import db
from models import User

app = create_app()

# List of users from WORKING-CREDENTIALS.md
expected_users = {
    'client': [
        'test@test.com',
        'test@restaurant.com',
        'test@fbrestaurant.com',
        'client1@test.com',
        'client2@test.com',
        'client3@test.com'
    ],
    'admin': [
        'admin@kwtsocial.com',
        'admin@kuwaitsocial.ai'
    ]
}

with app.app_context():
    print("=== Checking for All Known Users ===\n")
    
    # Check existing users
    existing_users = User.query.all()
    existing_emails = [u.email for u in existing_users]
    
    print(f"Currently in database: {len(existing_users)} users")
    for user in existing_users:
        print(f"  ✓ {user.email} ({user.role})")
    
    print("\n--- Checking Expected Users ---")
    
    missing_users = []
    for role, emails in expected_users.items():
        print(f"\n{role.upper()} users:")
        for email in emails:
            if email in existing_emails:
                user = User.query.filter_by(email=email).first()
                print(f"  ✓ {email} - EXISTS (active: {user.is_active})")
            else:
                print(f"  ✗ {email} - MISSING")
                missing_users.append((email, role))
    
    if missing_users:
        print(f"\n\n{len(missing_users)} users are missing from the database:")
        for email, role in missing_users:
            print(f"  - {email} ({role})")
        
        print("\nWould you like to create these missing users? (y/n)")
        # For now, just report - don't create automatically
    else:
        print("\n\nAll expected users exist in the database! ✓")