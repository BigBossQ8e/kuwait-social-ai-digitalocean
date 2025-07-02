#!/usr/bin/env python3
"""Simple login test"""

import requests
import json

# Test with local server
BASE_URL = "http://localhost:5000"

print("Testing login to Kuwait Social AI...\n")

# Test credentials
test_users = [
    {"email": "test@restaurant.com", "password": "test123"},
    {"email": "admin@kuwaitsocial.ai", "password": "admin123"},
    {"email": "owner@kuwaitsocial.ai", "password": "owner123"}
]

for user in test_users:
    print(f"Trying {user['email']}...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=user)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(f"   Token: {data.get('access_token', '')[:20]}...")
            print(f"   User: {data.get('user', {})}")
        else:
            print(f"❌ Login failed")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        print("   Make sure the server is running on port 5000")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("-" * 50)

print("\nTesting server health...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"Server response: {response.status_code}")
except:
    print("❌ Server not responding")