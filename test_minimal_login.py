#!/usr/bin/env python3
import requests
import json

# Test the minimal login endpoint
url = "http://209.38.176.129:5000/api/auth/test-login"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
data = {
    "email": "admin@kwtsocial.com",
    "password": "AdminPass123!"
}

print("Testing minimal login endpoint...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"\nStatus Code: {response.status_code}")
    
    # Try to parse as JSON
    try:
        response_data = response.json()
        print(f"Response JSON: {json.dumps(response_data, indent=2)}")
    except:
        print(f"Response Text: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")