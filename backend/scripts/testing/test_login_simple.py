#!/usr/bin/env python3
"""Simple login test with correct test client usage"""

from dotenv import load_dotenv
load_dotenv()

from app_factory import create_app

app = create_app()

# Test credentials
email = "test@restaurant.com"
password = "password123"

print("=== Simple Login Test ===")
print(f"Email: {email}")
print(f"Password: {password}")

# Start Flask app
with app.test_client() as client:
    # Make login request using json parameter
    response = client.post('/api/auth/login', json={
        'email': email,
        'password': password
    })
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.get_json()
        print("✓ Login successful!")
        print(f"User: {data.get('user', {}).get('email')}")
        print(f"Role: {data.get('user', {}).get('role')}")
        print(f"Company: {data.get('user', {}).get('company_name')}")
        print(f"Access Token: {data.get('access_token', '')[:50]}...")
    else:
        print("✗ Login failed!")
        print(f"Response: {response.get_json()}")