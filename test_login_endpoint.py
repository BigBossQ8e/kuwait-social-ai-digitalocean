#!/usr/bin/env python3
"""Test login endpoint to debug 400 error"""

import requests
import json

# Test different variations
base_url = "https://kwtsocial.com"
tests = [
    {
        "name": "Standard JSON",
        "headers": {"Content-Type": "application/json"},
        "data": json.dumps({"email": "admin@kwtsocial.com", "password": "AdminPass123!"})
    },
    {
        "name": "With charset",
        "headers": {"Content-Type": "application/json; charset=utf-8"},
        "data": json.dumps({"email": "admin@kwtsocial.com", "password": "AdminPass123!"})
    },
    {
        "name": "With Accept header",
        "headers": {"Content-Type": "application/json", "Accept": "application/json"},
        "data": json.dumps({"email": "admin@kwtsocial.com", "password": "AdminPass123!"})
    },
    {
        "name": "Using json parameter",
        "headers": {},
        "json": {"email": "admin@kwtsocial.com", "password": "AdminPass123!"}
    }
]

for test in tests:
    print(f"\n=== {test['name']} ===")
    
    if 'json' in test:
        response = requests.post(f"{base_url}/api/auth/login", 
                               headers=test.get('headers', {}),
                               json=test['json'])
    else:
        response = requests.post(f"{base_url}/api/auth/login", 
                               headers=test['headers'],
                               data=test['data'])
    
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    if response.status_code != 200:
        print(f"Response: {response.text[:200]}")
    else:
        print(f"Success: {response.json()}")