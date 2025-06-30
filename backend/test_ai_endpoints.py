#!/usr/bin/env python3
"""
Test script for AI content generation endpoints
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "admin@kwtsocial.com"
TEST_PASSWORD = "admin123"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{BLUE}ℹ {message}{RESET}")

def print_warning(message):
    print(f"{YELLOW}⚠ {message}{RESET}")

def login():
    """Login and get JWT token"""
    print_info("Logging in...")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data['access_token']
        print_success(f"Logged in as {data['user']['email']} ({data['user']['role']})")
        return token
    else:
        print_error(f"Login failed: {response.text}")
        sys.exit(1)

def test_content_generation(token):
    """Test content generation endpoint"""
    print_info("\nTesting content generation...")
    
    test_cases = [
        {
            "name": "Instagram Restaurant Post",
            "payload": {
                "prompt": "Special Ramadan iftar buffet at our restaurant with traditional Kuwaiti dishes",
                "platform": "instagram",
                "tone": "enthusiastic",
                "include_arabic": True,
                "include_hashtags": True,
                "business_type": "restaurant"
            }
        },
        {
            "name": "Twitter Retail Sale",
            "payload": {
                "prompt": "Announce 50% off sale on all summer collection this weekend only",
                "platform": "twitter",
                "tone": "casual",
                "include_arabic": True,
                "include_hashtags": True,
                "business_type": "retail"
            }
        }
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for test in test_cases:
        print(f"\n  Testing: {test['name']}")
        
        response = requests.post(
            f"{BASE_URL}/api/ai/generate",
            json=test['payload'],
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()['data']
            print_success("Content generated successfully")
            print(f"    Platform: {data['platform']}")
            print(f"    Character count: {data['character_count']}")
            print(f"    Content: {data['content'][:100]}...")
            if data.get('arabic_content'):
                print(f"    Arabic: {data['arabic_content'][:100]}...")
            if data.get('hashtags'):
                print(f"    Hashtags: {', '.join(data['hashtags'][:5])}...")
        else:
            print_error(f"Failed: {response.text}")

def test_translation(token):
    """Test translation endpoint"""
    print_info("\nTesting translation...")
    
    test_cases = [
        {
            "text": "Welcome to our grand opening! Special offers all week.",
            "source_lang": "en",
            "target_lang": "ar"
        },
        {
            "text": "مرحباً بكم في مطعمنا الجديد",
            "source_lang": "ar", 
            "target_lang": "en"
        }
    ]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for test in test_cases:
        print(f"\n  Translating {test['source_lang']} → {test['target_lang']}")
        
        response = requests.post(
            f"{BASE_URL}/api/ai/translate",
            json=test,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()['data']
            print_success("Translation successful")
            print(f"    Original: {data['original_text']}")
            print(f"    Translated: {data['translated_text']}")
        else:
            print_error(f"Failed: {response.text}")

def test_hashtag_generation(token):
    """Test hashtag generation endpoint"""
    print_info("\nTesting hashtag generation...")
    
    test_content = "Join us for an exclusive dining experience featuring authentic Kuwaiti cuisine and live traditional music every Thursday evening."
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/api/ai/hashtags",
        json={
            "content": test_content,
            "platform": "instagram",
            "business_type": "restaurant"
        },
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()['data']
        print_success("Hashtags generated successfully")
        print(f"    Total count: {data['total_count']}")
        print(f"    High volume: {', '.join(data['hashtags']['high_volume'])}")
        print(f"    Medium volume: {', '.join(data['hashtags']['medium_volume'][:3])}...")
        print(f"    Niche: {', '.join(data['hashtags']['niche'][:3])}...")
    else:
        print_error(f"Failed: {response.text}")

def test_content_enhancement(token):
    """Test content enhancement endpoint"""
    print_info("\nTesting content enhancement...")
    
    original_content = "come to our store for big sale"
    
    headers = {"Authorization": f"Bearer {token}"}
    
    enhancement_types = ["grammar", "engagement", "localization"]
    
    for enhancement_type in enhancement_types:
        print(f"\n  Testing {enhancement_type} enhancement")
        
        response = requests.post(
            f"{BASE_URL}/api/ai/enhance",
            json={
                "content": original_content,
                "enhancement_type": enhancement_type
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()['data']
            print_success(f"{enhancement_type.capitalize()} enhancement successful")
            print(f"    Original: {data['original_content']}")
            print(f"    Enhanced: {data['enhanced_content']}")
            if data.get('changes'):
                print(f"    Changes: {'; '.join(data['changes'][:2])}...")
        else:
            print_error(f"Failed: {response.text}")

def test_templates(token):
    """Test template fetching"""
    print_info("\nTesting template fetching...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/ai/templates?platform=instagram&business_type=restaurant",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()['data']
        print_success(f"Fetched {len(data['templates'])} templates")
        for template in data['templates'][:2]:
            print(f"    - {template['name']}: {template['prompt'][:50]}...")
    else:
        print_error(f"Failed: {response.text}")

def test_trending(token):
    """Test trending topics"""
    print_info("\nTesting trending topics...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/ai/trending",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()['data']
        print_success("Fetched trending data")
        print(f"    Topics: {len(data['topics'])}")
        for topic in data['topics'][:2]:
            print(f"      - {topic['topic']}: {topic['description']}")
        print(f"    Trending hashtags: {', '.join(data['hashtags']['trending_now'][:5])}")
    else:
        print_error(f"Failed: {response.text}")

def main():
    """Run all tests"""
    print(f"\n{BLUE}Kuwait Social AI - AI Endpoints Test Suite{RESET}")
    print("=" * 50)
    
    # Check if API keys are configured
    print_warning("\nNOTE: Make sure you have configured the following in your .env file:")
    print("  - OPENAI_API_KEY or ANTHROPIC_API_KEY")
    print("  - AI_PROVIDER (set to 'openai' or 'anthropic')")
    
    input("\nPress Enter to continue with tests...")
    
    # Login
    token = login()
    
    # Run tests
    try:
        test_content_generation(token)
        test_translation(token)
        test_hashtag_generation(token)
        test_content_enhancement(token)
        test_templates(token)
        test_trending(token)
        
        print(f"\n{GREEN}All tests completed!{RESET}")
        
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
    except Exception as e:
        print_error(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    main()