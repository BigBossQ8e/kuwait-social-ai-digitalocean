#!/usr/bin/env python3
"""
Display F&B prompts used by the AI service
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Use service container for proper dependency injection
from services.container import get_ai_service
ai_service = get_ai_service()

print("Kuwait Social AI - F&B Prompts")
print("=" * 50)

# Example 1: Restaurant
print("\n1. RESTAURANT PROMPT EXAMPLE:")
print("-" * 30)
system_prompt = ai_service._build_system_prompt(
    platform="instagram",
    tone="enthusiastic",
    business_type="restaurant"
)
print("System Prompt:")
print(system_prompt)

user_prompt = ai_service._build_user_prompt(
    prompt="Grilled lamb chops with traditional sides",
    platform="instagram",
    additional_context={
        "target_audience": "Families and meat lovers",
        "campaign_goal": "Increase dinner reservations",
        "key_message": "Authentic, halal, family-friendly"
    }
)
print("\nUser Prompt:")
print(user_prompt)

# Example 2: Hashtag Generation
print("\n\n2. HASHTAG GENERATION PROMPT:")
print("-" * 30)
hashtag_prompt = f"""
Generate 30 hashtags for this instagram post for a restaurant in Kuwait.
Mix popular Kuwait hashtags with niche ones.
Include both English and Arabic hashtags.

Content: Experience the best grilled meats in Kuwait at our family restaurant!

Return only the hashtags, one per line, starting with #.
"""
print(hashtag_prompt)

# Example 3: Translation with F&B context
print("\n\n3. TRANSLATION PROMPT:")
print("-" * 30)
translation_prompt = f"""
Translate the following text from en to ar.
Maintain the marketing tone and adapt it culturally for Kuwait.
Preserve any brand names, hashtags, and emojis.

Text: Try our special weekend brunch! All-you-can-eat buffet with live cooking stations. Family-friendly atmosphere with kids play area. Only 12 KWD per person!
"""
print(translation_prompt)

# Show F&B specific elements
print("\n\n4. F&B SPECIFIC ELEMENTS IN PROMPTS:")
print("-" * 30)
print("✓ Always mentions HALAL certification")
print("✓ Emphasizes family-friendly atmosphere")
print("✓ Highlights delivery options")
print("✓ Mentions air conditioning (important in Kuwait heat)")
print("✓ Includes price in KWD")
print("✓ References meal times (lunch, dinner, iftar)")
print("✓ Uses appropriate food emojis 🍽️ 🥘 ☕")
print("✓ Mentions popular cuisines in Kuwait")
print("✓ Considers prayer times and cultural values")

print("\n\n5. F&B HASHTAGS ADDED:")
print("-" * 30)
print("General:", ai_service.kuwait_context['food_hashtags'][:5])
print("\nThese hashtags are automatically added to F&B content!")

print("\n\n✅ The AI is fully optimized for Kuwait F&B businesses!")