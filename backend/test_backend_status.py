#!/usr/bin/env python3
"""Test backend API status"""

import requests
import json
import sys

# Test both local and production
ENDPOINTS = {
    "Local": "http://localhost:5000",
    "Production": "https://kwtsocial.com"
}

def test_endpoint(name, base_url):
    print(f"\n=== Testing {name} ({base_url}) ===")
    
    # 1. Test API login endpoint
    print("\n1. Testing /api/auth/login endpoint...")
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={"email": "test@restaurant.com", "password": "password123"},
            timeout=5,
            verify=True  # Verify SSL for production
        )
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Login successful!")
            print(f"   User: {data.get('user', {}).get('email')}")
            token = data.get('access_token', '')[:50] + '...' if data.get('access_token') else 'No token'
            print(f"   Token: {token}")
        elif response.status_code == 401:
            print(f"   ✓ API is working (invalid credentials)")
        elif response.status_code == 500:
            print(f"   ✗ Server Error: {response.json()}")
        else:
            print(f"   Response: {response.text[:200]}")
    except requests.exceptions.SSLError as e:
        print(f"   ✗ SSL Error: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"   ✗ Connection Error: Cannot reach {base_url}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 2. Test static pages (production only)
    if "kwtsocial.com" in base_url:
        print("\n2. Testing static pages...")
        static_pages = [
            "/login",
            "/admin-panel/index.html",
            "/dashboard"
        ]
        
        for page in static_pages:
            try:
                response = requests.get(f"{base_url}{page}", timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    print(f"   ✓ {page} - OK")
                else:
                    print(f"   ✗ {page} - Status {response.status_code}")
            except Exception as e:
                print(f"   ✗ {page} - Error: {e}")

# Test local first
test_endpoint("Local Backend", ENDPOINTS["Local"])

# Test production
test_endpoint("Production", ENDPOINTS["Production"])

print("\n=== Summary ===")
print("\nIf local is working but production is not:")
print("1. SSH into your server: ssh root@kuwait-social-ai-1750866347")
print("2. Install Redis: apt install redis-server")
print("3. Start Redis: systemctl start redis-server")
print("4. Restart backend service")
print("\nProduction URL: https://kwtsocial.com")