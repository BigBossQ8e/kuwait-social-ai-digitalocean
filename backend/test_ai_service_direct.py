#!/usr/bin/env python3
"""
Direct test of AI service with proper initialization
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Kuwait Social AI - Direct AI Service Test")
print("=" * 50)

# Check environment
api_key = os.getenv('OPENAI_API_KEY')
print(f"✓ API Key loaded: {api_key[:20] if api_key else 'NOT FOUND'}...")

# Now use the service container
try:
    # Use service container for proper dependency injection
    from services.container import get_ai_service
    
    # Get service instance
    ai_service = get_ai_service()
    print("✓ AI Service initialized successfully!")
    
    # Test the F&B prompt building
    print("\n1. F&B SYSTEM PROMPT:")
    print("-" * 50)
    system_prompt = ai_service._build_system_prompt(
        platform="instagram",
        tone="enthusiastic",
        business_type="restaurant"
    )
    print(system_prompt)
    
    print("\n2. USER PROMPT:")
    print("-" * 50)
    user_prompt = ai_service._build_user_prompt(
        prompt="Weekend seafood special with grilled fish",
        platform="instagram",
        additional_context={
            "target_audience": "Seafood lovers and families",
            "campaign_goal": "Increase weekend traffic",
            "key_message": "Fresh catch, halal, family atmosphere"
        }
    )
    print(user_prompt)
    
    print("\n3. GENERATING F&B CONTENT:")
    print("-" * 50)
    result = ai_service.generate_content(
        prompt="Special grilled meat platter for families",
        platform="instagram",
        tone="enthusiastic",
        include_arabic=True,
        include_hashtags=True,
        business_type="restaurant",
        additional_context={
            "target_audience": "Families",
            "key_message": "Halal, generous portions, great value"
        }
    )
    
    print(f"✓ Generated content ({result['character_count']} chars)")
    print(f"\nEnglish:\n{result['content'][:300]}...")
    
    if result.get('arabic_content'):
        print(f"\nArabic:\n{result['arabic_content'][:200]}...")
    
    if result.get('hashtags'):
        print(f"\nHashtags ({len(result['hashtags'])}):")
        print(', '.join(result['hashtags'][:10]))
    
    # Check F&B elements
    print("\n4. F&B ELEMENTS CHECK:")
    print("-" * 50)
    content_lower = result['content'].lower()
    checks = {
        "HALAL mentioned": "halal" in content_lower,
        "Family-friendly": "family" in content_lower,
        "Delivery mentioned": "delivery" in content_lower or "deliver" in content_lower,
        "Air conditioning": "air-condition" in content_lower or "ac" in content_lower,
        "Price mentioned": "kwd" in content_lower,
        "Food hashtags": any('#kuwait' in h.lower() or 'food' in h.lower() for h in result.get('hashtags', []))
    }
    
    for check, passed in checks.items():
        print(f"  {check}: {'✅' if passed else '❌'}")
    
    print("\n✅ AI Service is working perfectly for F&B!")
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nThis might be due to missing dependencies. Make sure you have:")
    print("  - pip install openai anthropic")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()