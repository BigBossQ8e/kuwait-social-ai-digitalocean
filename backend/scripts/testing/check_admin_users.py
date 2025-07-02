#!/usr/bin/env python3
"""
Check for admin users or create a default admin
"""

import os
import sys
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_factory import create_app
from models import db, User
from werkzeug.security import generate_password_hash

def check_or_create_admin():
    """Check for admin users or create default admin"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check for existing admin users
            admins = User.query.filter_by(role='admin', is_active=True).all()
            
            if admins:
                print("✅ Found existing admin users:")
                print("-" * 60)
                for admin in admins:
                    print(f"Email: {admin.email}")
                    print(f"Username: {admin.username if hasattr(admin, 'username') else 'N/A'}")
                    print(f"Created: {admin.created_at}")
                    print(f"Last Login: {admin.last_login if hasattr(admin, 'last_login') else 'Never'}")
                    print("-" * 60)
            else:
                print("❌ No admin users found!")
                print("\nWould you like to create a default admin user?")
                print("Default credentials would be:")
                print("  Email: admin@kuwaitsocial.ai")
                print("  Password: KuwaitSocial2024!")
                
                response = input("\nCreate default admin? (yes/no): ").lower().strip()
                
                if response == 'yes':
                    # Create default admin
                    admin = User(
                        email='admin@kuwaitsocial.ai',
                        username='admin',
                        password_hash=generate_password_hash('KuwaitSocial2024!'),
                        role='admin',
                        is_active=True,
                        created_at=datetime.utcnow()
                    )
                    
                    db.session.add(admin)
                    db.session.commit()
                    
                    print("\n✅ Admin user created successfully!")
                    print("\n🔐 Login credentials:")
                    print("  Email: admin@kuwaitsocial.ai")
                    print("  Password: KuwaitSocial2024!")
                    print("\n⚠️  IMPORTANT: Change this password after first login!")
                else:
                    print("\nNo admin user created. You can create one manually later.")
                    
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("\nPossible issues:")
            print("1. Database connection failed")
            print("2. Database tables not created")
            print("3. Invalid configuration in .env file")
            
            # Try to show current database URL (without password)
            db_url = os.getenv('DATABASE_URL', 'Not configured')
            if 'postgresql' in db_url:
                # Hide password in URL
                import re
                safe_url = re.sub(r'://[^:]+:[^@]+@', '://***:***@', db_url)
                print(f"\nCurrent DATABASE_URL: {safe_url}")
            else:
                print(f"\nCurrent DATABASE_URL: {db_url}")

if __name__ == "__main__":
    check_or_create_admin()