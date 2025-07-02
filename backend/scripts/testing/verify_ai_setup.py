#!/usr/bin/env python3
"""
Verify AI Setup - Quick Check
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Kuwait Social AI - Configuration Check")
print("=" * 50)

# Check API Keys
openai_key = os.getenv('OPENAI_API_KEY', '')
anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
ai_provider = os.getenv('AI_PROVIDER', 'openai')

print("✓ OpenAI API Key:", "Found" if openai_key and openai_key != 'YOUR_OPENAI_API_KEY_HERE' else "Missing")
print("✓ Anthropic API Key:", "Found" if anthropic_key and anthropic_key != 'YOUR_ANTHROPIC_API_KEY_HERE' else "Missing")
print("✓ AI Provider:", ai_provider)

print("\n📊 Quick Test Results:")
print("-" * 50)

# Test AI Service
try:
    from services.container import get_ai_service
    ai_service = get_ai_service()
    
    # Quick content generation
    result = ai_service.generate_content(
        prompt="Create a 2-line announcement for lunch special",
        platform="instagram",
        tone="enthusiastic",
        business_type="restaurant"
    )
    
    print(f"✅ AI Service: Working with {ai_provider.upper()}")
    print(f"✅ Generated {result['character_count']} characters")
    print(f"✅ Content preview: {result['content'][:100]}...")
    
except Exception as e:
    print(f"❌ AI Service Error: {str(e)[:100]}")

print("\n🎯 Configuration Summary:")
print("-" * 50)
print("1. Claude 3.5 Sonnet:", "Ready ✅" if anthropic_key and 'sk-ant' in anthropic_key else "Needs API key ❌")
print("2. GPT-4 Turbo:", "Ready ✅" if openai_key and 'sk-' in openai_key else "Needs API key ❌")
print("3. Current Provider:", f"{ai_provider.upper()} {'✅' if ai_provider == 'anthropic' and anthropic_key or ai_provider == 'openai' and openai_key else '❌'}")

print("\n💡 Recommendations:")
if ai_provider == 'openai' and anthropic_key and 'sk-ant' in anthropic_key:
    print("• You have Claude API key but using OpenAI. Consider switching:")
    print("  Edit .env and set: AI_PROVIDER=anthropic")
elif not anthropic_key or 'YOUR_' in anthropic_key:
    print("• Add Anthropic API key for Claude 3.5 Sonnet access")
    
print("\n✅ Setup verification complete!")