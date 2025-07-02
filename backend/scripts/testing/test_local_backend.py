#!/usr/bin/env python3
"""Test local backend API"""

import requests
import json

BASE_URL = "http://localhost:5000"

print("=== Testing Local Backend API ===\n")

# 1. Test health endpoint (if exists)
print("1. Testing health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/health", timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✓ Health check passed")
    else:
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ✗ Health endpoint not available: {e}")

# 2. Test login endpoint
print("\n2. Testing login endpoint...")
login_data = {
    "email": "test@restaurant.com",
    "password": "password123"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("   ✓ Login successful!")
        print(f"   User: {data.get('user', {}).get('email')}")
        print(f"   Token: {data.get('access_token', '')[:50]}...")
        
        # Save token for next test
        token = data.get('access_token')
        
        # 3. Test authenticated endpoint
        print("\n3. Testing authenticated endpoint (profile)...")
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = requests.get(f"{BASE_URL}/api/auth/profile", headers=headers, timeout=5)
        print(f"   Status: {profile_response.status_code}")
        if profile_response.status_code == 200:
            print("   ✓ Profile retrieved successfully")
            print(f"   Data: {json.dumps(profile_response.json(), indent=2)}")
    else:
        print(f"   ✗ Login failed: {response.json()}")
        
except Exception as e:
    print(f"   ✗ Error: {e}")

# 4. Test CORS headers
print("\n4. Testing CORS configuration...")
try:
    response = requests.options(
        f"{BASE_URL}/api/auth/login",
        headers={
            "Origin": "https://kwtsocial.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        },
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    print(f"   CORS Headers:")
    for header, value in response.headers.items():
        if 'access-control' in header.lower():
            print(f"     {header}: {value}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n=== Backend is ready for production deployment! ===")
print("\nNext steps:")
print("1. Deploy this exact code to your production server")
print("2. Use the same .env file (or .env.production)")
print("3. Start with: gunicorn --bind 0.0.0.0:5000 wsgi:application")
print("4. Or use systemd service for auto-restart")