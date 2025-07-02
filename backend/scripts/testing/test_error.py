#!/usr/bin/env python3
"""Test login to see actual error"""

import requests
import json

# Test login endpoint
url = "http://localhost:5000/api/auth/login"
data = {
    "email": "test@restaurant.com",
    "password": "password123"
}

print("Testing login endpoint...")
print(f"URL: {url}")
print(f"Data: {data}")

try:
    response = requests.post(url, json=data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Also test a simple GET endpoint
print("\n\nTesting auth profile endpoint (should require auth)...")
profile_url = "http://localhost:5000/api/auth/profile"
response = requests.get(profile_url)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")