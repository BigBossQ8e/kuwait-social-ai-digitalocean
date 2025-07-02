#!/usr/bin/env python3
"""Create test users for each role"""

from app_factory import create_app
from extensions import db
from models.core import User, Admin, Owner, Client

app = create_app('development')

with app.app_context():
    # Create owner if doesn't exist
    owner_user = User.query.filter_by(email='owner@kwtsocial.com').first()
    if not owner_user:
        owner_user = User(email='owner@kwtsocial.com', role='owner')
        owner_user.set_password('owner123')
        db.session.add(owner_user)
        db.session.flush()
        
        owner_profile = Owner(
            user_id=owner_user.id,
            company_name='Kuwait Social AI',
            phone='+965-1234567'
        )
        db.session.add(owner_profile)
        print("Created owner user: owner@kwtsocial.com / owner123")
    else:
        print("Owner already exists: owner@kwtsocial.com")
    
    # Create client if doesn't exist
    client_user = User.query.filter_by(email='client@example.com').first()
    if not client_user:
        client_user = User(email='client@example.com', role='client')
        client_user.set_password('client123')
        db.session.add(client_user)
        db.session.flush()
        
        client_profile = Client(
            user_id=client_user.id,
            company_name='Test Restaurant',
            contact_name='Test Client',
            phone='+965-9876543'
        )
        db.session.add(client_profile)
        print("Created client user: client@example.com / client123")
    else:
        print("Client already exists: client@example.com")
    
    # Commit all changes
    db.session.commit()
    
    # List all users
    print("\nAll users in database:")
    print("-" * 50)
    users = User.query.all()
    for user in users:
        print(f"Email: {user.email}, Role: {user.role}")