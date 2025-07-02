#!/usr/bin/env python3
"""Create test user with simpler approach"""

import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

# Create/connect to database
conn = sqlite3.connect('kuwait_social_test.db')
cursor = conn.cursor()

# Create users table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    role TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
)
''')

# Create clients table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    company_name TEXT NOT NULL,
    contact_name TEXT,
    phone TEXT,
    address TEXT,
    subscription_plan TEXT DEFAULT 'trial',
    subscription_status TEXT DEFAULT 'active',
    subscription_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subscription_end TIMESTAMP,
    monthly_posts_limit INTEGER DEFAULT 100,
    monthly_posts_used INTEGER DEFAULT 0,
    ai_credits_limit INTEGER DEFAULT 1000,
    ai_credits_used INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Check if user exists
email = 'test@restaurant.com'
cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
existing_user = cursor.fetchone()

if existing_user:
    print(f"User {email} already exists with ID: {existing_user[0]}")
    user_id = existing_user[0]
else:
    # Create test user
    password_hash = generate_password_hash('test123')
    cursor.execute('''
        INSERT INTO users (email, password_hash, role, created_at)
        VALUES (?, ?, ?, ?)
    ''', (email, password_hash, 'client', datetime.utcnow()))
    user_id = cursor.lastrowid
    print(f"Created user {email} with ID: {user_id}")

# Check if client profile exists
cursor.execute('SELECT id FROM clients WHERE user_id = ?', (user_id,))
existing_client = cursor.fetchone()

if not existing_client:
    # Create client profile
    cursor.execute('''
        INSERT INTO clients (user_id, company_name, contact_name, phone)
        VALUES (?, ?, ?, ?)
    ''', (user_id, 'Test Restaurant', 'Test User', '+965 12345678'))
    client_id = cursor.lastrowid
    print(f"Created client profile with ID: {client_id}")
else:
    print(f"Client profile already exists with ID: {existing_client[0]}")

# Commit changes
conn.commit()
conn.close()

print("\n✅ Test user ready!")
print("Email: test@restaurant.com")
print("Password: test123")