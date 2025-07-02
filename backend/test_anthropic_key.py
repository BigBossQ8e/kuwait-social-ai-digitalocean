#!/usr/bin/env python3
"""
Quick test for Anthropic API key
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

print("Testing Anthropic API Key...")
print("=" * 50)

api_key = os.getenv('ANTHROPIC_API_KEY')
print(f"API Key found: {api_key[:20]}...{api_key[-10:]}")

try:
    # Initialize client
    client = Anthropic(api_key=api_key)
    
    # Simple test message
    print("\nSending test message to Claude 3.5 Sonnet...")
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{
            "role": "user", 
            "content": "Say 'Hello Kuwait!' and tell me you're Claude 3.5 Sonnet in 1 sentence."
        }]
    )
    
    print("\n✅ SUCCESS! API Key is working!")
    print(f"\nClaude's response: {response.content[0].text}")
    
    # Test with Kuwait F&B content
    print("\n" + "=" * 50)
    print("Testing F&B Content Generation...")
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=200,
        system="You are a Kuwait F&B social media expert. Always mention HALAL.",
        messages=[{
            "role": "user",
            "content": "Create a short Instagram caption for a grilled chicken special at a Kuwait restaurant."
        }]
    )
    
    print(f"\nF&B Content: {response.content[0].text}")
    print("\n✅ Your Anthropic API key is working perfectly!")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("\nThe API key appears to be invalid or there's a connection issue.")
    if "authentication" in str(e).lower():
        print("This is an authentication error - the API key is not valid.")
    elif "rate" in str(e).lower():
        print("This might be a rate limit issue.")
    else:
        print(f"Full error: {e}")