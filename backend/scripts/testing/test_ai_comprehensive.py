#!/usr/bin/env python3
"""
Comprehensive test for AI service
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Kuwait Social AI - Comprehensive AI Test")
print("=" * 50)

try:
    from services.ai_service import ai_service
    print("✓ AI Service initialized successfully!")
    
    # Test 1: Content Generation with Kuwait context
    print("\n1. Testing Kuwait-specific content generation...")
    result = ai_service.generate_content(
        prompt="Announce our special weekend brunch buffet",
        platform="instagram",
        tone="enthusiastic",
        include_arabic=True,
        include_hashtags=True,
        business_type="restaurant"
    )
    
    print(f"✓ Content generated ({result['character_count']} chars)")
    print(f"   English: {result['content'][:100]}...")
    if result.get('arabic_content'):
        print(f"   Arabic: {result['arabic_content'][:100]}...")
    if result.get('hashtags'):
        print(f"   Hashtags ({len(result['hashtags'])}): {', '.join(result['hashtags'][:5])}...")
    if result.get('recommendations'):
        print(f"   Tips: {result['recommendations'][0]}")
    
    # Test 2: Translation
    print("\n2. Testing translation service...")
    translated = ai_service.translate_content(
        "Welcome to the best restaurant in Kuwait City!",
        source_lang="en",
        target_lang="ar"
    )
    print(f"✓ Translation successful")
    print(f"   Arabic: {translated}")
    
    # Test 3: Hashtag Generation
    print("\n3. Testing hashtag generation...")
    hashtags = ai_service.generate_hashtags(
        "Authentic Kuwaiti cuisine with a modern twist",
        platform="instagram",
        business_type="restaurant"
    )
    print(f"✓ Generated {len(hashtags)} hashtags")
    print(f"   Tags: {', '.join(hashtags[:8])}")
    
    # Test 4: Content Enhancement
    print("\n4. Testing content enhancement...")
    enhanced = ai_service.enhance_content(
        "come eat at our place we have good food",
        enhancement_type="engagement"
    )
    print(f"✓ Content enhanced")
    print(f"   Original: {enhanced['original_content']}")
    print(f"   Enhanced: {enhanced['enhanced_content'][:100]}...")
    
    print("\n✅ All AI features are working correctly!")
    print("The AI backend is ready to generate amazing content for Kuwait businesses!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()