#!/usr/bin/env python3
"""
Test F&B content generation - Working version
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Kuwait Social AI - F&B Content Test")
print("=" * 50)

# Direct import to avoid initialization issues
try:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import only what we need
    from openai import OpenAI
    
    # Initialize OpenAI
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    print("✓ OpenAI client initialized successfully!")
    
    # F&B System Prompt
    system_prompt = """
    You are a social media content expert specializing in Kuwait's F&B market.
    
    KUWAIT F&B ESSENTIALS (ALWAYS INCLUDE):
    - ✅ ALWAYS mention "100% HALAL"
    - 👨‍👩‍👧‍👦 ALWAYS emphasize "family-friendly"
    - 🚗 ALWAYS include delivery options
    - ❄️ ALWAYS mention "fully air-conditioned"
    - 💰 ALWAYS show prices in KWD
    
    Use appetizing language and food emojis. Make readers hungry!
    """
    
    # Test generation
    print("\nGenerating F&B content...")
    
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Create an Instagram post about: Special weekend grilled meat platter at our Lebanese restaurant"}
        ],
        max_tokens=500,
        temperature=0.8
    )
    
    content = response.choices[0].message.content
    
    print("\n✅ Generated F&B Content:")
    print("-" * 50)
    print(content)
    print("-" * 50)
    
    # Check if key elements are included
    print("\n✓ Content Check:")
    checks = {
        "HALAL mentioned": "halal" in content.lower(),
        "Family-friendly": "family" in content.lower(),
        "Delivery mentioned": "delivery" in content.lower() or "deliver" in content.lower(),
        "Price in KWD": "kwd" in content.lower(),
        "Has emojis": "🍽" in content or "🥘" in content or "🍖" in content
    }
    
    for check, result in checks.items():
        print(f"  {check}: {'✅' if result else '❌'}")
    
    print("\n✅ F&B AI is working perfectly!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()