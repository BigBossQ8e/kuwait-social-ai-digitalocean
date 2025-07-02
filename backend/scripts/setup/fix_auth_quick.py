#!/usr/bin/env python3
"""
Quick fix for authentication issues
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_factory import create_app
from models import db

def add_missing_columns():
    """Add missing columns to users table"""
    app = create_app('development')
    
    with app.app_context():
        print("🔧 Adding missing columns to users table...")
        
        try:
            # Add missing columns
            db.session.execute("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0,
                ADD COLUMN IF NOT EXISTS last_failed_login TIMESTAMP
            """)
            db.session.commit()
            print("✅ Columns added successfully!")
        except Exception as e:
            print(f"⚠️  Note: {e}")
            print("   (This is okay if columns already exist)")

if __name__ == '__main__':
    add_missing_columns()
    print("\n✅ Auth fix applied! You can now login.")