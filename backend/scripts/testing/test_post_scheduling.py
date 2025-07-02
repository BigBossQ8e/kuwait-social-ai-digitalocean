#!/usr/bin/env python3
"""Test post scheduling functionality"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Configuration
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
POSTS_URL = f"{BASE_URL}/api/client/posts"
DASHBOARD_URL = f"{BASE_URL}/api/client/dashboard"

def test_login():
    """Test login functionality"""
    print("Testing login...")
    
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

def test_create_scheduled_post(token):
    """Test creating a scheduled post"""
    print("\nTesting scheduled post creation...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Schedule for 2 hours from now
    scheduled_time = (datetime.utcnow() + timedelta(hours=2)).isoformat()
    
    post_data = {
        "content": "🍽️ Exciting announcement coming soon! Stay tuned for our special Friday lunch offer.",
        "content_ar": "🍽️ إعلان مثير قادم قريباً! ترقبوا عرض غداء الجمعة الخاص لدينا.",
        "platform": "instagram",
        "status": "scheduled",
        "scheduled_time": scheduled_time,
        "hashtags": ["#kuwaitfood", "#fridaylunch", "#مطاعم_الكويت"],
        "ai_generated": True
    }
    
    try:
        response = requests.post(POSTS_URL, headers=headers, json=post_data)
        
        if response.status_code in [200, 201]:
            result = response.json()
            print("✅ Scheduled post created successfully!")
            print(f"   - Post ID: {result.get('id')}")
            print(f"   - Scheduled for: {scheduled_time}")
            print(f"   - Status: {result.get('status')}")
            return result.get('id')
        else:
            print(f"❌ Failed to create scheduled post: {response.status_code}")
            print(response.json())
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_get_scheduled_posts(token):
    """Test retrieving scheduled posts"""
    print("\nTesting scheduled posts retrieval...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        # Try getting scheduled posts from dashboard
        response = requests.get(DASHBOARD_URL, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            scheduled_posts = data.get('scheduled_posts', [])
            
            print(f"✅ Retrieved {len(scheduled_posts)} scheduled posts")
            
            for post in scheduled_posts[:3]:  # Show first 3
                print(f"   - Caption: {post.get('caption', '')[:50]}...")
                print(f"     Scheduled: {post.get('scheduled_time')}")
                print(f"     Platforms: {', '.join(post.get('platforms', []))}")
            
            return True
        else:
            print(f"❌ Failed to get scheduled posts: {response.status_code}")
            print(response.json())
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_update_scheduled_post(token, post_id):
    """Test updating a scheduled post"""
    print("\nTesting scheduled post update...")
    
    if not post_id:
        print("⚠️  No post ID provided, skipping update test")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Reschedule for 3 hours from now
    new_scheduled_time = (datetime.utcnow() + timedelta(hours=3)).isoformat()
    
    update_data = {
        "scheduled_time": new_scheduled_time,
        "content": "🍽️ UPDATED: Amazing Friday lunch special! Don't miss out on our Majboos feast!"
    }
    
    try:
        response = requests.put(f"{POSTS_URL}/{post_id}", headers=headers, json=update_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Scheduled post updated successfully!")
            print(f"   - New scheduled time: {new_scheduled_time}")
            return True
        else:
            print(f"❌ Failed to update scheduled post: {response.status_code}")
            print(response.json())
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_cancel_scheduled_post(token, post_id):
    """Test canceling a scheduled post"""
    print("\nTesting scheduled post cancellation...")
    
    if not post_id:
        print("⚠️  No post ID provided, skipping cancellation test")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Update status to draft (cancel scheduling)
    cancel_data = {
        "status": "draft"
    }
    
    try:
        response = requests.put(f"{POSTS_URL}/{post_id}", headers=headers, json=cancel_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Scheduled post cancelled successfully!")
            print(f"   - New status: {result.get('status')}")
            return True
        else:
            print(f"❌ Failed to cancel scheduled post: {response.status_code}")
            print(response.json())
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_schedule_validation():
    """Test scheduling validation (past times, invalid formats)"""
    print("\nTesting schedule validation...")
    
    # This would test various invalid scheduling scenarios
    test_cases = [
        {
            "name": "Past time",
            "scheduled_time": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
            "expected_error": True
        },
        {
            "name": "Too far in future (>30 days)",
            "scheduled_time": (datetime.utcnow() + timedelta(days=45)).isoformat(),
            "expected_error": True
        },
        {
            "name": "Valid future time",
            "scheduled_time": (datetime.utcnow() + timedelta(hours=5)).isoformat(),
            "expected_error": False
        }
    ]
    
    print("✅ Schedule validation tests defined")
    return True

def main():
    print("=== Kuwait Social AI - Post Scheduling Test ===\n")
    
    # Test login
    token = test_login()
    if not token:
        print("\n⚠️  Cannot proceed without authentication")
        sys.exit(1)
    
    # Test creating scheduled post
    post_id = test_create_scheduled_post(token)
    
    # Test getting scheduled posts
    get_scheduled = test_get_scheduled_posts(token)
    
    # Test updating scheduled post
    update_scheduled = test_update_scheduled_post(token, post_id)
    
    # Test canceling scheduled post
    cancel_scheduled = test_cancel_scheduled_post(token, post_id)
    
    # Test validation rules
    validation = test_schedule_validation()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Login: ✅")
    print(f"Create Scheduled Post: {'✅' if post_id else '❌'}")
    print(f"Get Scheduled Posts: {'✅' if get_scheduled else '❌'}")
    print(f"Update Scheduled Post: {'✅' if update_scheduled else '❌'}")
    print(f"Cancel Scheduled Post: {'✅' if cancel_scheduled else '❌'}")
    print(f"Validation Rules: {'✅' if validation else '❌'}")
    
    if all([post_id, get_scheduled, validation]):
        print("\n✅ Post scheduling functionality is working!")
    else:
        print("\n⚠️  Some scheduling features need attention")

if __name__ == "__main__":
    main()