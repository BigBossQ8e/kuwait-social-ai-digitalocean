#!/usr/bin/env python3
"""Test script for TelegramAccount model"""

from app_factory import create_app
from extensions import db
from models import User, TelegramAccount

app = create_app('development')

with app.app_context():
    # Test 1: Check if table exists
    try:
        count = TelegramAccount.query.count()
        print(f"✓ TelegramAccount table exists. Current records: {count}")
    except Exception as e:
        print(f"✗ Error accessing TelegramAccount table: {e}")
        exit(1)
    
    # Test 2: Create a test telegram account
    try:
        # Get or create a test user
        test_user = User.query.filter_by(email='test@example.com').first()
        if not test_user:
            test_user = User(email='test@example.com', role='client')
            test_user.set_password('testpass123')
            db.session.add(test_user)
            db.session.commit()
            print(f"✓ Created test user: {test_user.email}")
        else:
            print(f"✓ Found existing test user: {test_user.email}")
        
        # Create telegram account
        telegram_account = TelegramAccount(
            user_id=test_user.id,
            telegram_id='123456789',
            telegram_username='testuser',
            first_name='Test',
            last_name='User',
            is_verified=True
        )
        db.session.add(telegram_account)
        db.session.commit()
        print(f"✓ Created telegram account for user {test_user.email}")
        
        # Test 3: Access relationship
        user_telegrams = test_user.telegram_accounts.all()
        print(f"✓ User has {len(user_telegrams)} telegram account(s)")
        
        # Test 4: Access reverse relationship
        telegram_user = telegram_account.user
        print(f"✓ Telegram account belongs to user: {telegram_user.email}")
        
        # Clean up
        db.session.delete(telegram_account)
        db.session.commit()
        print("✓ Cleaned up test data")
        
    except Exception as e:
        print(f"✗ Error testing TelegramAccount model: {e}")
        db.session.rollback()
        exit(1)

print("\n✓ All tests passed! TelegramAccount model is working correctly.")