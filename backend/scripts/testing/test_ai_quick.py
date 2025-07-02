#!/usr/bin/env python3
"""
Quick test for AI service
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if API key is loaded
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print(f"✓ OpenAI API key loaded: {api_key[:20]}...")
    print(f"✓ AI Provider: {os.getenv('AI_PROVIDER', 'openai')}")
else:
    print("✗ OpenAI API key not found!")
    exit(1)

# Now test the AI service
try:
    from services.ai_service import ai_service
    print("✓ AI Service initialized successfully!")
    
    # Test a simple generation
    print("\nTesting content generation...")
    result = ai_service.generate_content(
        prompt="Welcome to our restaurant",
        platform="instagram",
        tone="professional"
    )
    
    print(f"✓ Generated content: {result['content'][:100]}...")
    print(f"✓ Character count: {result['character_count']}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()