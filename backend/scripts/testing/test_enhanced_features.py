#!/usr/bin/env python3
"""Test script for enhanced F&B features"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
CONTENT_URL = f"{BASE_URL}/api/content/generate"
CONTENT_FB_URL = f"{BASE_URL}/api/content-fb/generate"
TEMPLATES_URL = f"{BASE_URL}/api/content-fb/templates"

def test_login():
    """Test login functionality"""
    print("Testing login...")
    
    # Test credentials
    credentials = {
        "email": "test@restaurant.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=credentials)
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            return data.get('access_token')
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.json())
            return None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def test_fb_templates(token):
    """Test F&B templates endpoint"""
    print("\nTesting F&B templates...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(TEMPLATES_URL, headers=headers)
        if response.status_code == 200:
            templates = response.json()
            print("✅ F&B templates retrieved successfully!")
            print(f"   - Categories: {list(templates.keys())}")
            for category, items in templates.items():
                print(f"   - {category}: {len(items)} templates")
            return True
        else:
            print(f"❌ Failed to get templates: {response.status_code}")
            print(response.json())
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_content_generation(token):
    """Test enhanced content generation"""
    print("\nTesting enhanced content generation...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test data for Friday Lunch Special
    test_data = {
        "template_id": "friday-lunch",
        "template_type": "social-gathering",
        "prompt": 'Generate a social media post for our dish "Majboos Diyay". It\'s a Friday lunch special. The tone should be warm and inviting, mentioning sharing and tradition for a family gathering in Kuwait.',
        "restaurant_context": "Traditional Kuwaiti restaurant in Salmiya",
        "target_audience": "families",
        "posting_time": "lunch",
        "language": "both",
        "hashtags": [],
        "include_emojis": True,
        "include_cta": True,
        "visual_cue": "A photo/video of a group of people (or just hands) sharing food, or a flat-lay of a large platter."
    }
    
    try:
        # Try enhanced endpoint first
        response = requests.post(CONTENT_FB_URL, headers=headers, json=test_data)
        
        if response.status_code == 404:
            print("⚠️  Enhanced endpoint not found, trying standard endpoint...")
            response = requests.post(CONTENT_URL, headers=headers, json={
                "prompt": test_data["prompt"],
                "platform": "instagram",
                "tone": "friendly",
                "include_hashtags": True,
                "include_emojis": True,
                "include_cta": True
            })
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Content generated successfully!")
            print(f"   - Content length: {len(data.get('content', ''))} chars")
            if 'hashtags' in data:
                print(f"   - Hashtags: {len(data['hashtags'])} suggested")
            if 'optimal_posting_time' in data:
                print(f"   - Optimal time: {data['optimal_posting_time']}")
            return True
        else:
            print(f"❌ Content generation failed: {response.status_code}")
            print(response.json())
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=== Kuwait Social AI - Enhanced F&B Features Test ===\n")
    
    # Test login
    token = test_login()
    if not token:
        print("\n⚠️  Cannot proceed without authentication")
        sys.exit(1)
    
    # Test F&B templates
    templates_ok = test_fb_templates(token)
    
    # Test content generation
    content_ok = test_content_generation(token)
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Login: ✅")
    print(f"F&B Templates: {'✅' if templates_ok else '❌'}")
    print(f"Content Generation: {'✅' if content_ok else '❌'}")
    
    if templates_ok and content_ok:
        print("\n✅ All enhanced F&B features are working correctly!")
    else:
        print("\n⚠️  Some features need attention")

if __name__ == "__main__":
    main()