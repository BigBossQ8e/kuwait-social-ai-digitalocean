#!/usr/bin/env python3
"""
Test admin login functionality
"""

import requests
import json

# API base URL
BASE_URL = "https://kwtsocial.com"
# BASE_URL = "http://localhost:5000"  # For local testing

def test_login():
    """Test admin login"""
    
    print("🔐 Testing Admin Login")
    print("=" * 50)
    
    # Login credentials
    credentials = {
        "email": "admin@kwtsocial.com",
        "password": "Kuwait2024Admin!"
    }
    
    # Login endpoint
    login_url = f"{BASE_URL}/api/auth/login"
    
    print(f"URL: {login_url}")
    print(f"Credentials: {credentials['email']}")
    
    try:
        # Make login request
        response = requests.post(
            login_url,
            json=credentials,
            headers={"Content-Type": "application/json"},
            verify=True  # Verify SSL certificate
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Login Successful!")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check for tokens
            if 'access_token' in data:
                print(f"\nAccess Token: {data['access_token'][:50]}...")
            if 'user' in data:
                print(f"User Role: {data['user'].get('role')}")
                
        else:
            print("\n❌ Login Failed!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.SSLError as e:
        print(f"\n❌ SSL Error: {e}")
        print("Trying without SSL verification...")
        
        # Retry without SSL verification
        response = requests.post(
            login_url,
            json=credentials,
            headers={"Content-Type": "application/json"},
            verify=False
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
def test_admin_endpoints():
    """Test accessing admin endpoints after login"""
    
    print("\n\n📊 Testing Admin Endpoints")
    print("=" * 50)
    
    # First login to get token
    credentials = {
        "email": "admin@kwtsocial.com",
        "password": "Kuwait2024Admin!"
    }
    
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=credentials,
        verify=False  # For testing
    )
    
    if login_response.status_code == 200:
        data = login_response.json()
        token = data.get('access_token')
        
        if token:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Test admin endpoints
            endpoints = [
                "/api/admin/dashboard",
                "/api/admin/users",
                "/api/admin/stats"
            ]
            
            for endpoint in endpoints:
                url = f"{BASE_URL}{endpoint}"
                print(f"\nTesting: {url}")
                
                try:
                    response = requests.get(url, headers=headers, verify=False)
                    print(f"Status: {response.status_code}")
                    if response.status_code == 200:
                        print("✅ Accessible")
                    else:
                        print(f"Response: {response.text[:200]}...")
                except Exception as e:
                    print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
    test_admin_endpoints()