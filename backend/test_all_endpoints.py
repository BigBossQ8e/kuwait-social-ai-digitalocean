#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all major endpoints in the Kuwait Social AI application
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:5000/api"
PROD_URL = "https://kwtsocial.com/api"

# Test credentials
ADMIN_EMAIL = "admin@kwtsocial.com"
ADMIN_PASS = "admin123"
CLIENT_EMAIL = "test@restaurant.com"
CLIENT_PASS = "password123"

# Use production if specified
if len(sys.argv) > 1 and sys.argv[1] == "--prod":
    BASE_URL = PROD_URL
    print(f"Testing production API at {PROD_URL}")
else:
    print(f"Testing local API at {BASE_URL}")

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_result(endpoint, method, status_code, success):
    """Print test result with color coding"""
    color = GREEN if success else RED
    status = "✓ PASS" if success else "✗ FAIL"
    print(f"{color}{status}{RESET} {method:6} {endpoint:40} [{status_code}]")

def test_endpoint(method, endpoint, headers=None, data=None, expected_status=200):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return None, f"Unknown method: {method}"
        
        success = response.status_code == expected_status
        print_result(endpoint, method, response.status_code, success)
        
        if not success:
            print(f"  Expected: {expected_status}, Got: {response.status_code}")
            if response.text:
                try:
                    error_data = response.json()
                    print(f"  Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"  Response: {response.text[:200]}")
        
        return response, None
    except Exception as e:
        print_result(endpoint, method, "ERR", False)
        print(f"  Error: {str(e)}")
        return None, str(e)

def login(email, password):
    """Login and get access token"""
    response, error = test_endpoint("POST", "/auth/login", data={
        "email": email,
        "password": password
    })
    
    if response and response.status_code == 200:
        data = response.json()
        return data.get("access_token"), data.get("user")
    return None, None

print("\n" + "="*70)
print("KUWAIT SOCIAL AI - API ENDPOINT TEST SUITE")
print("="*70 + "\n")

# Test 1: Health Check
print("1. HEALTH CHECK")
print("-" * 30)
test_endpoint("GET", "/health")

# Test 2: Authentication
print("\n2. AUTHENTICATION")
print("-" * 30)

# Login as client
client_token, client_user = login(CLIENT_EMAIL, CLIENT_PASS)
if client_token:
    print(f"  Client login successful: {client_user.get('email')}")
    client_headers = {"Authorization": f"Bearer {client_token}"}
else:
    print(f"  {RED}Client login failed!{RESET}")
    client_headers = {}

# Login as admin
admin_token, admin_user = login(ADMIN_EMAIL, ADMIN_PASS)
if admin_token:
    print(f"  Admin login successful: {admin_user.get('email')}")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
else:
    print(f"  {RED}Admin login failed!{RESET}")
    admin_headers = {}

# Test auth endpoints
test_endpoint("GET", "/auth/me", headers=client_headers)
test_endpoint("POST", "/auth/refresh", headers=client_headers)
test_endpoint("POST", "/auth/logout", headers=client_headers)

# Test 3: Client Endpoints
print("\n3. CLIENT ENDPOINTS")
print("-" * 30)
test_endpoint("GET", "/clients/profile", headers=client_headers)
test_endpoint("GET", "/clients/dashboard", headers=client_headers)
test_endpoint("GET", "/clients/posts", headers=client_headers)
test_endpoint("GET", "/clients/analytics", headers=client_headers)
test_endpoint("GET", "/clients/social-accounts", headers=client_headers)
test_endpoint("GET", "/clients/competitors", headers=client_headers)
test_endpoint("GET", "/clients/features", headers=client_headers)
test_endpoint("GET", "/clients/subscription", headers=client_headers)

# Test 4: Post Management
print("\n4. POST MANAGEMENT")
print("-" * 30)
test_endpoint("GET", "/posts", headers=client_headers)
test_endpoint("GET", "/posts/drafts", headers=client_headers)
test_endpoint("GET", "/posts/scheduled", headers=client_headers)
test_endpoint("GET", "/posts/published", headers=client_headers)

# Create a test post
post_data = {
    "content_type": "text",
    "caption_en": "Test post from API test suite",
    "caption_ar": "اختبار منشور من مجموعة اختبار API",
    "hashtags": ["#test", "#api", "#kuwait"],
    "status": "draft"
}
response, _ = test_endpoint("POST", "/posts", headers=client_headers, data=post_data, expected_status=201)
if response and response.status_code == 201:
    post_id = response.json().get("id")
    print(f"  Created test post with ID: {post_id}")
    
    # Test post operations
    test_endpoint("GET", f"/posts/{post_id}", headers=client_headers)
    test_endpoint("PUT", f"/posts/{post_id}", headers=client_headers, data={
        "caption_en": "Updated test post"
    })
    test_endpoint("POST", f"/posts/{post_id}/schedule", headers=client_headers, data={
        "scheduled_time": (datetime.utcnow() + timedelta(hours=1)).isoformat()
    })
    test_endpoint("DELETE", f"/posts/{post_id}", headers=client_headers)

# Test 5: Content Features
print("\n5. CONTENT FEATURES")
print("-" * 30)
test_endpoint("POST", "/content/generate", headers=client_headers, data={
    "prompt": "Create a social media post about Kuwaiti cuisine",
    "include_arabic": True
})
test_endpoint("GET", "/content/templates", headers=client_headers)
test_endpoint("POST", "/content/hashtags/suggest", headers=client_headers, data={
    "content": "Beautiful sunset at Kuwait Towers",
    "platform": "instagram"
})
test_endpoint("GET", "/content/trending-hashtags", headers=client_headers)
test_endpoint("POST", "/content/validate", headers=client_headers, data={
    "content": "Test content for validation",
    "platform": "instagram"
})

# Test 6: Analytics
print("\n6. ANALYTICS")
print("-" * 30)
test_endpoint("GET", "/analytics/overview", headers=client_headers)
test_endpoint("GET", "/analytics/posts", headers=client_headers)
test_endpoint("GET", "/analytics/engagement", headers=client_headers)
test_endpoint("GET", "/analytics/growth", headers=client_headers)
test_endpoint("GET", "/analytics/export?format=csv", headers=client_headers)

# Test 7: Admin Endpoints (if logged in as admin)
if admin_token:
    print("\n7. ADMIN ENDPOINTS")
    print("-" * 30)
    test_endpoint("GET", "/admin/dashboard", headers=admin_headers)
    test_endpoint("GET", "/admin/users", headers=admin_headers)
    test_endpoint("GET", "/admin/clients", headers=admin_headers)
    test_endpoint("GET", "/admin/analytics", headers=admin_headers)
    test_endpoint("GET", "/admin/platform-settings", headers=admin_headers)
    test_endpoint("GET", "/admin/support-tickets", headers=admin_headers)

# Test 8: Social Media Integration
print("\n8. SOCIAL MEDIA INTEGRATION")
print("-" * 30)
test_endpoint("GET", "/social/instagram/auth-url", headers=client_headers)
test_endpoint("GET", "/social/snapchat/auth-url", headers=client_headers)
test_endpoint("GET", "/social/accounts", headers=client_headers)

# Test 9: Kuwait-Specific Features
print("\n9. KUWAIT-SPECIFIC FEATURES")
print("-" * 30)
test_endpoint("GET", "/prayer-times", headers=client_headers)
test_endpoint("GET", "/kuwait/events", headers=client_headers)
test_endpoint("GET", "/kuwait/trending", headers=client_headers)
test_endpoint("GET", "/kuwait/cultural-guidelines", headers=client_headers)

# Test 10: Competitor Analysis
print("\n10. COMPETITOR ANALYSIS")
print("-" * 30)
test_endpoint("GET", "/competitors", headers=client_headers)
test_endpoint("POST", "/competitors", headers=client_headers, data={
    "name": "Test Competitor",
    "instagram_handle": "@testcompetitor",
    "industry": "restaurant"
})
test_endpoint("GET", "/competitors/analysis", headers=client_headers)
test_endpoint("GET", "/competitors/comparison", headers=client_headers)

# Test 11: Error Handling
print("\n11. ERROR HANDLING")
print("-" * 30)
test_endpoint("GET", "/nonexistent", expected_status=404)
test_endpoint("GET", "/clients/profile", expected_status=401)  # No auth
test_endpoint("POST", "/auth/login", data={"email": "wrong@email.com", "password": "wrong"}, expected_status=401)
test_endpoint("GET", "/posts/999999", headers=client_headers, expected_status=404)

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print(f"\nTesting completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"API Base URL: {BASE_URL}")
print("\nNote: Some endpoints may fail if:")
print("- Features are not implemented yet")
print("- Required data doesn't exist")
print("- External services are not configured")
print("\nCheck the application logs for detailed error information.")