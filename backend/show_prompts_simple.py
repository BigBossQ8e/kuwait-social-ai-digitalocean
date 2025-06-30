#!/usr/bin/env python3
"""
Display F&B prompts used by the AI service
"""

print("Kuwait Social AI - F&B Prompts for OpenAI")
print("=" * 50)

# System Prompt for F&B
system_prompt_template = """
You are a social media content expert specializing in the Kuwait market.
You create engaging {platform} posts for {business_type} in Kuwait.

Context about Kuwait:
- Bilingual market (Arabic and English)
- Islamic culture, conservative values
- High social media engagement rates
- Active shopping culture
- Strong family and community values
- Prayer times are respected
- Friday is the holy day, weekend is Friday-Saturday

Food & Beverage specific guidelines for Kuwait:
- Always mention if food is HALAL (this is crucial)
- Emphasize family-friendly atmosphere
- Highlight delivery options (very popular in Kuwait)
- Mention special dietary options (vegan, gluten-free, etc.)
- Reference popular meal times: Lunch (12-3 PM), Dinner (7-11 PM)
- During Ramadan: Focus on Iftar and Suhoor offerings
- Popular cuisines in Kuwait: Kuwaiti, Lebanese, Indian, Italian, Japanese
- Use food emojis appropriately 🍽️ 🥘 ☕ 🍰
- Mention air conditioning and indoor seating (important due to heat)
- Family sections and private dining areas are valued
- Include price ranges in KWD when appropriate

Platform specifications for {platform}:
- Maximum length: {max_length} characters
- Hashtag limit: {hashtag_limit}
- Best practices: {best_practices}

Write in a {tone} tone.
"""

# Example filled prompt
print("\n1. EXAMPLE SYSTEM PROMPT FOR INSTAGRAM RESTAURANT:")
print("-" * 50)
filled_prompt = system_prompt_template.format(
    platform="Instagram",
    business_type="restaurant",
    max_length="2200",
    hashtag_limit="30",
    best_practices="Use high-quality visuals, stories, and reels",
    tone="enthusiastic"
)
print(filled_prompt)

# User Prompt Template
print("\n\n2. USER PROMPT TEMPLATE:")
print("-" * 50)
user_prompt = """
Create a Instagram post about: Special weekend brunch buffet with live cooking stations

Target audience: Families and food lovers
Campaign goal: Increase weekend traffic
Key message: All-you-can-eat, halal, family-friendly, great value
"""
print(user_prompt)

# Hashtag Prompt
print("\n\n3. HASHTAG GENERATION PROMPT:")
print("-" * 50)
hashtag_prompt = """
Generate 30 hashtags for this Instagram post for a restaurant in Kuwait.
Mix popular Kuwait hashtags with niche ones.
Include both English and Arabic hashtags.

Content: Experience our special weekend brunch buffet!

Return only the hashtags, one per line, starting with #.
"""
print(hashtag_prompt)

# Expected Output Format
print("\n\n4. EXPECTED AI OUTPUT:")
print("-" * 50)
print("""
🌟 Weekend Brunch Paradise! 🌟

Join us this Friday & Saturday for our ALL-YOU-CAN-EAT brunch buffet! 🥞🍳

✅ 100% HALAL certified
👨‍👩‍👧‍👦 Family-friendly with kids play area
🍽️ Live cooking stations
❄️ Fully air-conditioned comfort
📍 Private family sections available

Only 12 KWD per adult, kids under 10 eat for half price!

⏰ Friday & Saturday: 10 AM - 3 PM
📱 Reserve now: [phone number]
🚗 Free delivery on orders above 5 KWD

#KuwaitFood #Q8Food #KuwaitRestaurants #WeekendBrunch #مطاعم_الكويت
""")

print("\n\n5. KEY F&B ELEMENTS THE AI INCLUDES:")
print("-" * 50)
print("✓ HALAL certification (always mentioned)")
print("✓ Family-friendly features")
print("✓ Air conditioning (crucial in Kuwait)")
print("✓ Delivery options")
print("✓ Price in KWD")
print("✓ Appropriate emojis")
print("✓ Mixed English/Arabic hashtags")
print("✓ Local area hashtags")
print("✓ Meal timing")
print("✓ Contact information")

print("\n✅ This is how the AI generates F&B content for Kuwait!")