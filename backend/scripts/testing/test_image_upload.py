#!/usr/bin/env python3
"""Test image upload and enhancement functionality"""

import requests
import os
import sys
from PIL import Image
import io

# Configuration
BASE_URL = "http://localhost:5000"
LOGIN_URL = f"{BASE_URL}/api/auth/login"
UPLOAD_URL = f"{BASE_URL}/api/content/upload-image"

def create_test_image():
    """Create a test image for upload"""
    print("Creating test image...")
    
    # Create a simple test image
    img = Image.new('RGB', (800, 800), color='red')
    
    # Add some pattern to make it more interesting
    for x in range(0, 800, 100):
        for y in range(0, 800, 100):
            if (x + y) % 200 == 0:
                # Draw yellow squares
                for i in range(100):
                    for j in range(100):
                        img.putpixel((x + i, y + j), (255, 255, 0))
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

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

def test_image_upload(token, enhance=True, platform='instagram', generate_caption=False):
    """Test image upload with various options"""
    print(f"\nTesting image upload (enhance={enhance}, platform={platform}, caption={generate_caption})...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Create test image
    img_bytes = create_test_image()
    
    files = {
        'image': ('test_food.jpg', img_bytes, 'image/jpeg')
    }
    
    data = {
        'enhance': 'true' if enhance else 'false',
        'platform': platform,
        'generate_caption': 'true' if generate_caption else 'false'
    }
    
    try:
        response = requests.post(UPLOAD_URL, headers=headers, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Image uploaded successfully!")
            print(f"   - Image URL: {result.get('image_url')}")
            print(f"   - Thumbnail URL: {result.get('thumbnail_url')}")
            print(f"   - Dimensions: {result.get('dimensions')}")
            print(f"   - File size: {result.get('file_size_mb')} MB")
            
            if result.get('generated_caption'):
                print(f"   - Generated caption: {result['generated_caption'].get('caption_en', '')[:100]}...")
            
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.json())
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_large_image(token):
    """Test uploading a large image"""
    print("\nTesting large image upload...")
    
    # Create a large image (4K resolution)
    img = Image.new('RGB', (3840, 2160), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', quality=95)
    img_bytes.seek(0)
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    files = {
        'image': ('large_test.jpg', img_bytes, 'image/jpeg')
    }
    
    data = {
        'enhance': 'true',
        'platform': 'instagram'
    }
    
    try:
        response = requests.post(UPLOAD_URL, headers=headers, files=files, data=data)
        
        if response.status_code == 200:
            print("✅ Large image processed successfully!")
            result = response.json()
            print(f"   - Original size: ~{img_bytes.tell() / 1024 / 1024:.2f} MB")
            print(f"   - Processed dimensions: {result.get('dimensions')}")
            return True
        else:
            print(f"❌ Large image failed: {response.status_code}")
            print(response.json())
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_invalid_file(token):
    """Test uploading an invalid file type"""
    print("\nTesting invalid file upload...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Create a text file
    files = {
        'image': ('test.txt', b'This is not an image', 'text/plain')
    }
    
    data = {
        'enhance': 'true',
        'platform': 'instagram'
    }
    
    try:
        response = requests.post(UPLOAD_URL, headers=headers, files=files, data=data)
        
        if response.status_code == 400:
            print("✅ Invalid file correctly rejected")
            print(f"   - Error: {response.json().get('error')}")
            return True
        else:
            print(f"❌ Invalid file not properly handled: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=== Kuwait Social AI - Image Upload Test ===\n")
    
    # Test login
    token = test_login()
    if not token:
        print("\n⚠️  Cannot proceed without authentication")
        sys.exit(1)
    
    # Test basic upload
    basic_upload = test_image_upload(token)
    
    # Test with caption generation
    caption_upload = test_image_upload(token, generate_caption=True)
    
    # Test different platforms
    tiktok_upload = test_image_upload(token, platform='tiktok')
    
    # Test large image
    large_upload = test_large_image(token)
    
    # Test invalid file
    invalid_upload = test_invalid_file(token)
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Login: ✅")
    print(f"Basic Upload: {'✅' if basic_upload else '❌'}")
    print(f"Caption Generation: {'✅' if caption_upload else '❌'}")
    print(f"Platform Resize: {'✅' if tiktok_upload else '❌'}")
    print(f"Large Image: {'✅' if large_upload else '❌'}")
    print(f"Invalid File Handling: {'✅' if invalid_upload else '❌'}")
    
    if all([basic_upload, caption_upload, tiktok_upload, large_upload, invalid_upload]):
        print("\n✅ All image upload tests passed!")
    else:
        print("\n⚠️  Some tests failed")

if __name__ == "__main__":
    main()