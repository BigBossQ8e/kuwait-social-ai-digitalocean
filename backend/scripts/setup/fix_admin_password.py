#!/usr/bin/env python3
"""
Fix admin password in production database
"""

import psycopg2
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'host': 'localhost',
    'port': 5432,
    'database': 'kuwait_social_ai',
    'user': 'kuwait_user',
    'password': 'secure_password'
}

def update_admin_password(email, new_password):
    """Update admin password directly in database"""
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        
        # Generate password hash
        password_hash = generate_password_hash(new_password)
        
        # Update password
        cur.execute("""
            UPDATE users 
            SET password_hash = %s, updated_at = NOW()
            WHERE email = %s
            RETURNING id, email, role
        """, (password_hash, email))
        
        result = cur.fetchone()
        
        if result:
            user_id, email, role = result
            print(f"✅ Password updated for {email} (ID: {user_id}, Role: {role})")
            conn.commit()
        else:
            print(f"❌ User {email} not found")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=== Fixing Admin Password ===\n")
    
    # Update admin password
    update_admin_password('admin@kwtsocial.com', 'admin123')
    
    # Also update the other admin if needed
    update_admin_password('admin@kuwaitsocial.ai', 'admin123')
    update_admin_password('test@kwtsocial.com', 'admin123')
    
    print("\nDone!")