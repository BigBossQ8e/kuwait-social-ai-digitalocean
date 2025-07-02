#!/usr/bin/env python3
"""
Comprehensive API Testing Script
Tests all endpoints and functionality
"""

import os
import sys
import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5001')
ADMIN_EMAIL = 'admin@example.com'
ADMIN_PASSWORD = 'password'

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")
        self.test_results.append({
            'timestamp': timestamp,
            'status': status,
            'message': message
        })
    
    def test_endpoint(self, method, endpoint, data=None, headers=None, expected_status=200):
        """Test a single endpoint"""
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers)
            
            if response.status_code == expected_status:
                self.log(f"✅ {method} {endpoint} - Status: {response.status_code}", "PASS")
                return True, response
            else:
                self.log(f"❌ {method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}", "FAIL")
                self.log(f"   Response: {response.text[:200]}", "ERROR")
                return False, response
                
        except Exception as e:
            self.log(f"❌ {method} {endpoint} - Error: {str(e)}", "ERROR")
            return False, None
    
    def test_auth(self):
        """Test authentication endpoints"""
        self.log("\n=== Testing Authentication ===")
        
        # Test login
        success, response = self.test_endpoint(
            'POST', '/api/auth/login',
            data={'email': ADMIN_EMAIL, 'password': ADMIN_PASSWORD}
        )
        
        if success and response.json().get('access_token'):
            self.token = response.json()['access_token']
            self.session.headers.update({'Authorization': f'Bearer {self.token}'})
            self.log("✅ Authentication successful", "PASS")
        else:
            self.log("❌ Authentication failed", "FAIL")
    
    def test_admin_endpoints(self):
        """Test admin endpoints"""
        self.log("\n=== Testing Admin Endpoints ===")
        
        if not self.token:
            self.log("⚠️  Skipping admin tests - no auth token", "WARN")
            return
        
        endpoints = [
            ('GET', '/api/admin/dashboard/overview'),
            ('GET', '/api/admin/platforms'),
            ('GET', '/api/admin/features'),
            ('GET', '/api/admin/packages'),
            ('GET', '/api/admin/dashboard/activity-feed'),
        ]
        
        for method, endpoint in endpoints:
            self.test_endpoint(method, endpoint, expected_status=200)
    
    def test_client_endpoints(self):
        """Test client endpoints"""
        self.log("\n=== Testing Client Endpoints ===")
        
        endpoints = [
            ('GET', '/api/client/profile'),
            ('GET', '/api/client/posts'),
            ('GET', '/api/client/analytics/overview'),
        ]
        
        for method, endpoint in endpoints:
            self.test_endpoint(method, endpoint, expected_status=[200, 401])
    
    def test_public_endpoints(self):
        """Test public endpoints"""
        self.log("\n=== Testing Public Endpoints ===")
        
        endpoints = [
            ('GET', '/api/prayer-times/today'),
            ('GET', '/admin-preview'),
            ('GET', '/admin-ai'),
        ]
        
        # Remove auth for public endpoints
        self.session.headers.pop('Authorization', None)
        
        for method, endpoint in endpoints:
            self.test_endpoint(method, endpoint, expected_status=200)
    
    def run_all_tests(self):
        """Run all tests"""
        self.log("Starting Comprehensive API Tests", "INFO")
        self.log(f"Base URL: {BASE_URL}", "INFO")
        
        self.test_auth()
        self.test_admin_endpoints()
        self.test_client_endpoints()
        self.test_public_endpoints()
        
        # Summary
        self.log("\n=== Test Summary ===")
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        self.log(f"Total: {len(self.test_results)}, Passed: {passed}, Failed: {failed}")
        
        # Save results
        with open(f'test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        return failed == 0

if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
