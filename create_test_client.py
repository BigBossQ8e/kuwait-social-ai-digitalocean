#!/usr/bin/env python3
"""
Create a test client for Kuwait Social AI
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_factory import create_app
from models import db, Client
from extensions import bcrypt
from datetime import datetime, timedelta

def create_test_client():
    app = create_app()
    
    with app.app_context():
        # Check if client already exists
        existing = Client.query.filter_by(email='test@kuwaitcoffee.com').first()
        if existing:
            print(f"Client already exists: {existing.email}")
            return
        
        # Create new client
        client = Client(
            company_name='Kuwait Coffee House',
            contact_name='Ahmed Al-Sabah',
            email='test@kuwaitcoffee.com',
            phone='+965 9999 8888',
            password_hash=bcrypt.generate_password_hash('Test123!').decode('utf-8'),
            subscription_plan='professional',
            subscription_status='active',
            monthly_posts_limit=100,
            monthly_posts_used=0,
            trial_ends_at=datetime.utcnow() + timedelta(days=7),
            is_active=True,
            email_verified=True,
            commercial_license='12345/2024',
            civil_id='123456789012'
        )
        
        db.session.add(client)
        db.session.commit()
        
        print(f"✅ Test client created successfully!")
        print(f"Email: {client.email}")
        print(f"Password: Test123!")
        print(f"Company: {client.company_name}")
        print(f"Plan: {client.subscription_plan}")
        print(f"Posts limit: {client.monthly_posts_limit}")

if __name__ == '__main__':
    create_test_client()