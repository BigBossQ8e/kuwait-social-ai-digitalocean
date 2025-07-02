"""
Content Creation Tools for Kuwait F&B Social Media
"""

from crewai.tools import tool
from typing import Dict, List, Any, Optional
import json
import random
from datetime import datetime

@tool("Template Generator")
def template_generator_tool(content_type: str, dish_name: str, restaurant_name: str, special_features: Optional[List[str]] = None) -> str:
    """Generate engaging content templates for Kuwait F&B social media posts"""
    special_features = special_features or []
    
    templates = {
        "post": _generate_post_templates(),
        "story": _generate_story_templates(),
        "reel": _generate_reel_templates()
    }
    
    template_list = templates.get(content_type.lower(), templates["post"])
    
    # Select appropriate template based on features
    if "new" in str(special_features).lower():
        template = random.choice([t for t in template_list if "NEW" in t or "introducing" in t.lower()])
    elif "offer" in str(special_features).lower() or "discount" in str(special_features).lower():
        template = random.choice([t for t in template_list if "offer" in t.lower() or "special" in t.lower()])
    else:
        template = random.choice(template_list)
    
    # Replace placeholders
    result = template.replace("{dish_name}", dish_name)
    result = result.replace("{restaurant_name}", restaurant_name)
    
    # Add special features
    if special_features:
        features_text = " | ".join(special_features)
        result += f"\n\n✨ {features_text}"
    
    # Add call to action
    cta_options = [
        "📱 Order now on Talabat/Deliveroo",
        "🚗 Drive-thru available",
        "📍 Visit us today!",
        "💚 WhatsApp us for orders",
        "🏃 Fast delivery to your door"
    ]
    result += f"\n\n{random.choice(cta_options)}"
    
    # Add Arabic version suggestion
    arabic_suggestion = _suggest_arabic_version(dish_name, restaurant_name)
    
    return json.dumps({
        "english_template": result,
        "arabic_suggestion": arabic_suggestion,
        "content_type": content_type,
        "character_count": len(result),
        "includes_emoji": True,
        "platform_optimized": True
    }, indent=2)

def _generate_post_templates() -> List[str]:
    """Generate Instagram/Facebook post templates"""
    return [
        "🔥 NEW ARRIVAL 🔥\n{dish_name} has landed at {restaurant_name}!\n\nGet ready for a flavor explosion that will blow your mind 🤯",
        "Craving something delicious? 😋\n\nOur {dish_name} is calling your name! Made fresh daily at {restaurant_name} with love ❤️",
        "Weekend vibes = {dish_name} vibes 🍴\n\nTreat yourself this weekend at {restaurant_name}!",
        "⏰ LIMITED TIME OFFER ⏰\n\nTry our special {dish_name} before it's gone! Only at {restaurant_name}",
        "Hungry? We've got you covered! 🍽️\n\n{dish_name} delivered hot and fresh from {restaurant_name} to your door",
        "✨ CUSTOMER FAVORITE ✨\n\nFind out why everyone's talking about our {dish_name} at {restaurant_name}!",
        "Perfect for sharing... or not! 😉\n\nOur {dish_name} at {restaurant_name} is too good to share",
        "Lunch sorted! ✅\n\nMake your day better with {dish_name} from {restaurant_name}"
    ]

def _generate_story_templates() -> List[str]:
    """Generate Instagram/Snapchat story templates"""
    return [
        "SWIPE UP FOR {dish_name} 👆\n\n@ {restaurant_name}",
        "Who's hungry? 🙋‍♂️🙋‍♀️\n\n{dish_name} fresh out the kitchen!",
        "POLL: {dish_name} for lunch? \nYES 😍 / DEFINITELY YES 🤤",
        "Behind the scenes 👨‍🍳\nMaking your favorite {dish_name}",
        "Last chance today! ⏰\n{dish_name} @ {restaurant_name}",
        "Rate our {dish_name} 1-10! 🌟\nDrop your rating below 👇"
    ]

def _generate_reel_templates() -> List[str]:
    """Generate Instagram Reel/TikTok templates"""
    return [
        "POV: You just discovered the best {dish_name} in Kuwait 🤤\n\n📍 {restaurant_name}",
        "Wait for it... 👀\n\nThe perfect {dish_name} does exist at {restaurant_name}!",
        "{dish_name} appreciation post 🙌\n\nTag someone who needs this in their life!",
        "How we make the famous {dish_name} 👨‍🍳\n\nOnly at {restaurant_name} ✨",
        "Rating {dish_name} from different restaurants...\n\n{restaurant_name} = 10/10 🏆"
    ]

def _suggest_arabic_version(dish_name: str, restaurant_name: str) -> str:
    """Suggest Arabic version of the content"""
    arabic_templates = [
        f"جديد لدينا! 🔥 {dish_name} في {restaurant_name}",
        f"جرب {dish_name} اللذيذ من {restaurant_name} 😋",
        f"عرض خاص على {dish_name} - {restaurant_name} 🎉",
        f"أفضل {dish_name} في الكويت! فقط في {restaurant_name} ⭐"
    ]
    return random.choice(arabic_templates)


@tool("Hashtag Optimizer")
def hashtag_optimizer_tool(content: str, platform: str, cuisine_type: Optional[str] = None) -> str:
    """Generate optimized hashtags for Kuwait F&B social media content"""
    
    # Base Kuwait hashtags
    base_tags = {
        "english": ["#Kuwait", "#Q8", "#KuwaitFood", "#KuwaitFoodie", "#Q8Food"],
        "arabic": ["#الكويت", "#كويت_فود", "#مطاعم_الكويت", "#فوديز_الكويت", "#اكل_كويتي"]
    }
    
    # Platform-specific limits
    platform_limits = {
        "instagram": 30,
        "twitter": 5,
        "facebook": 10,
        "tiktok": 10
    }
    
    limit = platform_limits.get(platform.lower(), 30)
    
    # Analyze content for relevant tags
    hashtags = []
    
    # Add base tags
    hashtags.extend(base_tags["english"][:2])
    hashtags.extend(base_tags["arabic"][:2])
    
    # Add cuisine-specific tags
    if cuisine_type:
        cuisine_tags = _get_cuisine_tags(cuisine_type)
        hashtags.extend(cuisine_tags[:3])
    
    # Add content-specific tags
    if "breakfast" in content.lower() or "morning" in content.lower():
        hashtags.extend(["#KuwaitBreakfast", "#فطور_الكويت", "#MorningVibes"])
    elif "lunch" in content.lower():
        hashtags.extend(["#KuwaitLunch", "#غداء_الكويت", "#LunchTime"])
    elif "dinner" in content.lower():
        hashtags.extend(["#KuwaitDinner", "#عشاء_الكويت", "#DinnerTime"])
    
    # Add trending tags
    trending = _get_trending_tags()
    hashtags.extend(trending[:3])
    
    # Add delivery tags if mentioned
    if any(word in content.lower() for word in ["delivery", "talabat", "deliveroo"]):
        hashtags.extend(["#KuwaitDelivery", "#توصيل_الكويت"])
    
    # Ensure uniqueness and limit
    unique_hashtags = list(dict.fromkeys(hashtags))[:limit]
    
    return json.dumps({
        "hashtags": unique_hashtags,
        "count": len(unique_hashtags),
        "platform": platform,
        "mix": {
            "english": len([h for h in unique_hashtags if not any(ord(c) > 127 for c in h)]),
            "arabic": len([h for h in unique_hashtags if any(ord(c) > 127 for c in h)])
        },
        "recommendations": [
            "Use 20-25 hashtags for Instagram posts",
            "Mix Arabic and English for wider reach",
            "Include location-specific tags",
            "Update trending tags weekly"
        ]
    }, indent=2)

def _get_cuisine_tags(cuisine_type: str) -> List[str]:
    """Get cuisine-specific hashtags"""
    cuisine_tags = {
        "burger": ["#BurgerKuwait", "#برجر_الكويت", "#Q8Burger"],
        "pizza": ["#PizzaKuwait", "#بيتزا_الكويت", "#Q8Pizza"],
        "arabic": ["#ArabicFood", "#اكل_عربي", "#MiddleEasternFood"],
        "indian": ["#IndianFoodKuwait", "#اكل_هندي", "#Q8Indian"],
        "italian": ["#ItalianKuwait", "#ايطالي_الكويت", "#Q8Italian"],
        "japanese": ["#JapaneseFoodKuwait", "#ياباني_الكويت", "#SushiKuwait"],
        "coffee": ["#CoffeeKuwait", "#قهوة_الكويت", "#Q8Coffee", "#KuwaitCafe"]
    }
    
    return cuisine_tags.get(cuisine_type.lower(), ["#InternationalCuisine", "#عالمي"])

def _get_trending_tags() -> List[str]:
    """Get currently trending tags in Kuwait"""
    # In production, this would fetch real trending data
    trending_pools = [
        ["#Kuwait2024", "#Q8Life", "#KuwaitVibes"],
        ["#كويت_انستغرام", "#الكويت_اليوم", "#كويتيات"],
        ["#FoodieKuwait", "#KuwaitEats", "#Q8Foodie"]
    ]
    
    return random.choice(trending_pools)


@tool("Emoji Food Expert")
def emoji_food_expert_tool(dish_type: str, mood: str = "exciting") -> str:
    """Suggest perfect emojis for Kuwait F&B content"""
    
    # Food type emoji mapping
    food_emojis = {
        "burger": ["🍔", "🍟", "🥤"],
        "pizza": ["🍕", "🧀", "🍅"],
        "pasta": ["🍝", "🍜", "🥄"],
        "salad": ["🥗", "🥬", "🥒"],
        "dessert": ["🍰", "🍨", "🍪"],
        "coffee": ["☕", "🥐", "🌅"],
        "juice": ["🥤", "🍊", "🍓"],
        "chicken": ["🍗", "🔥", "😋"],
        "seafood": ["🦐", "🐟", "🦀"],
        "breakfast": ["🍳", "🥞", "🥓"],
        "arabic": ["🥙", "🍖", "🫓"]
    }
    
    # Mood emoji mapping
    mood_emojis = {
        "exciting": ["🔥", "💥", "🎉", "✨", "⚡"],
        "delicious": ["😋", "🤤", "😍", "👌", "💯"],
        "fresh": ["🌿", "🌱", "💚", "🥬", "🌟"],
        "hot": ["🔥", "🌶️", "♨️", "🥵", "💨"],
        "cool": ["❄️", "🧊", "💙", "🏖️", "🌊"],
        "premium": ["👑", "💎", "⭐", "🏆", "✨"],
        "healthy": ["💪", "🥗", "💚", "🌱", "✅"],
        "family": ["👨‍👩‍👧‍👦", "❤️", "🏠", "🤗", "👏"]
    }
    
    # Get relevant emojis
    dish_emojis = food_emojis.get(dish_type.lower(), ["🍽️", "🍴", "👨‍🍳"])
    mood_emoji_list = mood_emojis.get(mood.lower(), mood_emojis["exciting"])
    
    # Create combinations
    suggestions = {
        "primary_emojis": dish_emojis,
        "mood_emojis": mood_emoji_list[:3],
        "recommended_combinations": [
            f"{dish_emojis[0]} {mood_emoji_list[0]} {dish_emojis[0]}",
            f"{mood_emoji_list[0]} {dish_emojis[0]} {mood_emoji_list[1]}",
            f"{dish_emojis[0]} + {dish_emojis[1]} = {mood_emoji_list[2]}"
        ],
        "usage_tips": [
            "Use 2-5 emojis per post for optimal engagement",
            "Place emojis at beginning or end of sentences",
            "Avoid overusing the same emoji",
            "Match emoji tone with content mood",
            "Use flag emoji 🇰🇼 sparingly (once per post max)"
        ],
        "platform_specific": {
            "instagram": "Use more emojis (5-8) for visual appeal",
            "twitter": "Keep it minimal (2-3) due to character limit",
            "facebook": "Moderate use (3-5) for professionalism"
        }
    }
    
    return json.dumps(suggestions, indent=2)


# Create tool instances for backward compatibility
TemplateGeneratorTool = template_generator_tool
HashtagOptimizerTool = hashtag_optimizer_tool
EmojiFoodExpertTool = emoji_food_expert_tool