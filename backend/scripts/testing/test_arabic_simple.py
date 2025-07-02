#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple test for Arabic content generation"""

import os
import json
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Set encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_arabic_content():
    """Test Arabic content generation locally"""
    
    print("🔍 Testing Arabic Content Generation")
    print("=" * 40)
    
    # Test content
    test_content = {
        "english": "Welcome to Beit Beirut Restaurant in Salmiya!",
        "arabic": "مرحباً بكم في مطعم بيت بيروت في السالمية!",
        "mixed": "Special Friday offer - عرض الجمعة الخاص",
        "hashtags": ["#الكويت", "#مطاعم_الكويت", "#السالمية", "#عرض_خاص"]
    }
    
    print("\n1. Direct output:")
    print(f"   English: {test_content['english']}")
    print(f"   Arabic: {test_content['arabic']}")
    print(f"   Mixed: {test_content['mixed']}")
    
    print("\n2. JSON output (ensure_ascii=False):")
    print(json.dumps(test_content, ensure_ascii=False, indent=2))
    
    print("\n3. Simulated API response:")
    api_response = {
        "status": "success",
        "data": {
            "content": test_content,
            "metadata": {
                "language": "ar-KW",
                "encoding": "UTF-8"
            }
        }
    }
    
    print(json.dumps(api_response, ensure_ascii=False, indent=2))
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    test_arabic_content()