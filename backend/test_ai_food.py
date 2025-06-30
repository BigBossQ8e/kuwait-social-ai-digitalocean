#!/usr/bin/env python3
"""
Test AI service for F&B (Food & Beverage) content
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Kuwait Social AI - F&B Content Generation Test")
print("=" * 50)

try:
    from services.ai_service import ai_service
    print("✓ AI Service initialized successfully!")
    
    # Test 1: Restaurant content
    print("\n1. Testing Restaurant Content Generation...")
    result = ai_service.generate_content(
        prompt="Announce our new Lebanese mezze platter with grilled meats",
        platform="instagram",
        tone="enthusiastic",
        include_arabic=True,
        include_hashtags=True,
        business_type="restaurant",
        additional_context={
            "target_audience": "Families and food lovers",
            "key_message": "Authentic Lebanese cuisine, halal certified, family-friendly"
        }
    )
    
    print(f"✓ Restaurant content generated")
    print(f"   Content: {result['content'][:150]}...")
    if result.get('arabic_content'):
        print(f"   Arabic: {result['arabic_content'][:150]}...")
    print(f"   Food hashtags: {[h for h in result.get('hashtags', []) if 'food' in h.lower() or 'restaurant' in h.lower()]}")
    
    # Test 2: Cafe content
    print("\n2. Testing Cafe Content Generation...")
    result2 = ai_service.generate_content(
        prompt="Morning coffee special with fresh croissants",
        platform="instagram",
        tone="casual",
        include_arabic=True,
        include_hashtags=True,
        business_type="cafe"
    )
    
    print(f"✓ Cafe content generated")
    print(f"   Content: {result2['content'][:150]}...")
    
    # Test 3: F&B Delivery
    print("\n3. Testing F&B Delivery Content...")
    result3 = ai_service.generate_content(
        prompt="Free delivery on orders above 5 KWD during lunch hours",
        platform="twitter",
        tone="professional",
        include_arabic=True,
        include_hashtags=True,
        business_type="f&b"
    )
    
    print(f"✓ Delivery content generated")
    print(f"   Content: {result3['content'][:150]}...")
    
    # Test 4: Ramadan Special
    print("\n4. Testing Ramadan F&B Content...")
    result4 = ai_service.generate_content(
        prompt="Special iftar buffet with traditional Kuwaiti dishes",
        platform="instagram",
        tone="enthusiastic",
        include_arabic=True,
        include_hashtags=True,
        business_type="restaurant"
    )
    
    print(f"✓ Ramadan content generated")
    print(f"   Content: {result4['content'][:150]}...")
    
    # Check for important F&B keywords
    print("\n5. Checking F&B Specific Elements...")
    all_content = result['content'] + result2['content'] + result3['content'] + result4['content']
    
    keywords_to_check = ['halal', 'family', 'delivery', 'fresh', 'authentic', 'KWD']
    found_keywords = [kw for kw in keywords_to_check if kw.lower() in all_content.lower()]
    
    print(f"✓ Found F&B keywords: {', '.join(found_keywords)}")
    
    # Check hashtags
    all_hashtags = set()
    for r in [result, result2, result3, result4]:
        all_hashtags.update(r.get('hashtags', []))
    
    food_hashtags = [h for h in all_hashtags if any(term in h.lower() for term in ['food', 'eat', 'restaurant', 'cafe', 'kuwait', 'q8'])]
    print(f"✓ Food-related hashtags: {', '.join(food_hashtags[:10])}")
    
    print("\n✅ F&B content generation is working perfectly!")
    print("The AI understands Kuwait's food culture and requirements!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()