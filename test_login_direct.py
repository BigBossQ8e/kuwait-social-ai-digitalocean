#!/usr/bin/env python3
"""Direct database test for login validation"""

import psycopg2
import hashlib
from werkzeug.security import check_password_hash

# Database connection
DB_HOST = "209.38.176.129"
DB_PORT = 5432
DB_NAME = "kuwait_social_ai"
DB_USER = "kuwait_user"
DB_PASS = "secure_password"

def test_admin_login():
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        
        cursor = conn.cursor()
        
        # Check if admin user exists
        cursor.execute(
            "SELECT id, email, password_hash, role, is_active FROM users WHERE email = %s",
            ("admin@kwtsocial.com",)
        )
        
        result = cursor.fetchone()
        
        if result:
            user_id, email, password_hash, role, is_active = result
            print(f"Admin user found:")
            print(f"  ID: {user_id}")
            print(f"  Email: {email}")
            print(f"  Role: {role}")
            print(f"  Active: {is_active}")
            print(f"  Password hash exists: {bool(password_hash)}")
            
            # Test password
            test_password = "AdminPass123!"
            if password_hash and check_password_hash(password_hash, test_password):
                print(f"  Password verification: SUCCESS")
            else:
                print(f"  Password verification: FAILED")
                
        else:
            print("Admin user not found in database")
            
            # List all users
            cursor.execute("SELECT email, role FROM users")
            users = cursor.fetchall()
            if users:
                print("\nExisting users:")
                for email, role in users:
                    print(f"  - {email} ({role})")
            else:
                print("\nNo users found in database")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    test_admin_login()