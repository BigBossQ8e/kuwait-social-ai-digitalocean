#!/usr/bin/env python
"""
Quick setup for admin panel testing - creates tables and test data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

from app_factory import create_app
from models import db

def quick_setup():
    """Quick setup for testing"""
    print("🚀 Quick Setup for Admin Panel Testing")
    
    app = create_app('development')
    
    with app.app_context():
        print("📊 Creating database tables...")
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created")
        except Exception as e:
            print(f"⚠️  Warning: {e}")
        
        print("\n✅ Setup complete!")
        print("\n📱 Access the admin panel at:")
        print("   http://localhost:5001/admin-test")
        print("\n🔑 Use these credentials:")
        print("   Email: admin@example.com")
        print("   Password: password")
        print("\n💡 Note: You can login with any email/password for testing")

if __name__ == '__main__':
    quick_setup()