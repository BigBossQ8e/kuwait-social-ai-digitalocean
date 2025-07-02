#!/usr/bin/env python3
"""Simple API test for Kuwait Social AI"""

import requests
import json

BASE_URL = "http://localhost:5001"

print("🧪 Testing Kuwait Social AI API")
print("=" * 50)

# Test 1: Health Check
print("\n1️⃣ Testing Health Check...")
try:
    response = requests.get(f"{BASE_URL}/api/health")
    if response.status_code == 200:
        print("✅ API is running!")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
except Exception as e:
    print(f"❌ Cannot connect to server: {e}")
    print("\n⚠️  Make sure the server is running on port 5001")
    exit(1)

# Test 2: Test AI without auth (should fail)
print("\n2️⃣ Testing AI Generation (without login)...")
try:
    response = requests.post(
        f"{BASE_URL}/api/ai/generate",
        json={
            "prompt": "Create a post about burgers",
            "platform": "instagram"
        }
    )
    if response.status_code == 401:
        print("✅ Authentication required (as expected)")
    else:
        print(f"Response: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("\n📝 What to do next:")
print("1. Keep this server running")
print("2. In another terminal, run your frontend application")
print("3. OR use Postman/Insomnia to test the API")
print("4. OR create a test user and login to get auth token")

print("\n🎯 Your API endpoints are:")
print("- POST /api/auth/login - Login")
print("- POST /api/auth/register - Create account")
print("- POST /api/ai/generate - Generate content (needs auth)")
print("- POST /api/ai/translate - Translate content (needs auth)")
print("- GET /api/ai/trending - Get trending topics (needs auth)")