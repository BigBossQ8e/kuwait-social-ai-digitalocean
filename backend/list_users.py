#!/usr/bin/env python3
"""List all users in the database"""

from app_factory import create_app
from models import User

app = create_app()

with app.app_context():
    users = User.query.all()
    
    if not users:
        print("No users found in database!")
        print("\nTo create a test user, you can:")
        print("1. Use the registration endpoint via the frontend")
        print("2. Or create one manually")
    else:
        print(f"Found {len(users)} users:\n")
        for user in users:
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Active: {user.is_active}")
            print(f"Created: {user.created_at}")
            print("-" * 40)