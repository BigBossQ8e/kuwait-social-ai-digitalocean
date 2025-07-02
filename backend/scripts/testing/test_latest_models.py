#!/usr/bin/env python3
"""
Test Latest AI Models - Claude 3.5 Sonnet & GPT-4 Turbo
"""

import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing Latest AI Models for Kuwait Social AI")
print("=" * 50)

# Check API keys
anthropic_key = os.getenv('ANTHROPIC_API_KEY')
openai_key = os.getenv('OPENAI_API_KEY')

print(f"✓ Anthropic API Key: {'Found' if anthropic_key else 'Missing'}")
print(f"✓ OpenAI API Key: {'Found' if openai_key else 'Missing'}")

# Test with direct import
try:
    from services.container import get_ai_service
    ai_service = get_ai_service()
    print("✓ AI Service initialized successfully!")
except Exception as e:
    print(f"✗ Error initializing AI Service: {e}")
    exit(1)

# Test prompt for F&B
test_prompt = """
Create an Instagram post for a Kuwait restaurant's weekend special:
- Grilled seafood platter
- Family size (4-6 people)
- Special price this Thursday-Friday only
"""

print("\n" + "=" * 50)
print("TESTING CLAUDE 3.5 SONNET")
print("=" * 50)

if anthropic_key:
    try:
        # Set to use Claude
        ai_service.default_provider = 'anthropic'
        
        start_time = time.time()
        result = ai_service.generate_content(
            prompt=test_prompt,
            platform="instagram",
            tone="enthusiastic",
            business_type="restaurant",
            include_arabic=True,
            include_hashtags=True,
            additional_context={
                "target_audience": "Families",
                "key_message": "Fresh, HALAL, great value"
            }
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"\n✓ Generated in {elapsed_time:.2f} seconds")
        print(f"\nContent ({result['character_count']} chars):")
        print("-" * 40)
        print(result['content'])
        print("-" * 40)
        
        if result.get('arabic_content'):
            print(f"\nArabic Translation:")
            print(result['arabic_content'])
        
        if result.get('hashtags'):
            print(f"\nHashtags ({len(result['hashtags'])}):")
            print(", ".join(result['hashtags']))
            
        print(f"\nOptimal Posting Times:")
        for posting_time in result.get('optimal_posting_times', []):
            print(f"  - {posting_time}")
            
    except Exception as e:
        print(f"\n✗ Claude Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n⚠ Skipping Claude test - No API key found")

print("\n" + "=" * 50)
print("TESTING GPT-4 TURBO")
print("=" * 50)

if openai_key:
    try:
        # Set to use OpenAI
        ai_service.default_provider = 'openai'
        
        start_time = time.time()
        result = ai_service.generate_content(
            prompt=test_prompt,
            platform="instagram",
            tone="enthusiastic",
            business_type="restaurant",
            include_arabic=False,  # Faster without translation
            include_hashtags=True
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"\n✓ Generated in {elapsed_time:.2f} seconds")
        print(f"\nContent ({result['character_count']} chars):")
        print("-" * 40)
        print(result['content'])
        print("-" * 40)
        
        if result.get('hashtags'):
            print(f"\nHashtags ({len(result['hashtags'])}):")
            print(", ".join(result['hashtags']))
            
    except Exception as e:
        print(f"\n✗ OpenAI Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n⚠ Skipping GPT-4 test - No API key found")

print("\n" + "=" * 50)
print("PERFORMANCE COMPARISON")
print("=" * 50)

# Quick performance test
if anthropic_key and openai_key:
    simple_prompt = "Create a short lunch special announcement"
    
    # Test Claude
    ai_service.default_provider = 'anthropic'
    start = time.time()
    claude_result = ai_service.generate_content(simple_prompt, platform="instagram")
    claude_time = time.time() - start
    
    # Test OpenAI
    ai_service.default_provider = 'openai'
    start = time.time()
    openai_result = ai_service.generate_content(simple_prompt, platform="instagram")
    openai_time = time.time() - start
    
    print(f"Claude 3.5 Sonnet: {claude_time:.2f}s")
    print(f"GPT-4 Turbo: {openai_time:.2f}s")
    print(f"Winner: {'Claude' if claude_time < openai_time else 'OpenAI'} (by {abs(claude_time - openai_time):.2f}s)")

print("\n✅ Model testing complete!")
print("\nRecommendations:")
print("1. Use Claude 3.5 Sonnet for complex, creative content")
print("2. Use GPT-4 Turbo for structured, analytical tasks")
print("3. Consider Claude 3.5 Haiku for simple, fast generation")
print("4. Set AI_PROVIDER=anthropic in .env to prefer Claude")