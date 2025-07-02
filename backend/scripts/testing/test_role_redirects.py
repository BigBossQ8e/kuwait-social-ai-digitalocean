#!/usr/bin/env python3
"""Test role-based redirects"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# Test users
test_users = [
    {"email": "admin@kwtsocial.com", "password": "admin123", "expected_role": "admin", "expected_redirect": "/admin"},
    {"email": "owner@kwtsocial.com", "password": "owner123", "expected_role": "owner", "expected_redirect": "/owner"},
    {"email": "client@example.com", "password": "client123", "expected_role": "client", "expected_redirect": "/dashboard"}
]

print("Testing role-based authentication and redirects...")
print("=" * 60)

for user in test_users:
    print(f"\nTesting {user['expected_role'].upper()} user:")
    print(f"Email: {user['email']}")
    
    # Make login request
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": user["email"], "password": user["password"]},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        user_info = data.get("user", {})
        
        print(f"✓ Login successful")
        print(f"  Role: {user_info.get('role')}")
        print(f"  Expected redirect: {user['expected_redirect']}")
        
        # Check if role matches
        if user_info.get("role") == user["expected_role"]:
            print(f"  ✓ Role matches expected: {user['expected_role']}")
        else:
            print(f"  ✗ Role mismatch! Expected: {user['expected_role']}, Got: {user_info.get('role')}")
        
        # Test access to role-specific endpoint
        access_token = data.get("access_token")
        if access_token:
            # Test /api/auth/me endpoint
            me_response = requests.get(
                f"{BASE_URL}/api/auth/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if me_response.status_code == 200:
                print(f"  ✓ Can access /api/auth/me endpoint")
            else:
                print(f"  ✗ Cannot access /api/auth/me endpoint")
                
    else:
        print(f"✗ Login failed with status: {response.status_code}")
        print(f"  Error: {response.text}")

print("\n" + "=" * 60)
print("Summary:")
print("- Admin users should redirect to: /admin")
print("- Owner users should redirect to: /owner")  
print("- Client users should redirect to: /dashboard")
print("\nThe React frontend handles the actual redirection based on the user role.")