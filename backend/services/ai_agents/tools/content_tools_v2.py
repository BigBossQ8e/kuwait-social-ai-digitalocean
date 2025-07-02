"""
Content Creation Tools for Kuwait F&B - CrewAI v0.5.0 Compatible
"""

from crewai.tools import tool
import json
from datetime import datetime
import random
import logging

logger = logging.getLogger(__name__)

@tool("Template Generator Tool")
def generate_content_template(content_type: str, business_info: str) -> str:
    """
    Generates content templates optimized for Kuwait F&B businesses.
    Content types: weekend_special, new_dish, delivery_promo, ramadan_offer, family_meal
    Business info should include: name, cuisine type, and target audience
    """
    try:
        templates = {
            "weekend_special": {
                "structure": [
                    "🌟 {hook} 🌟",
                    "",
                    "{main_offer}",
                    "",
                    "✨ Special Features:",
                    "{features}",
                    "",
                    "📍 {location_details}",
                    "⏰ {timing}",
                    "💰 {price}",
                    "",
                    "📞 {contact}",
                    "",
                    "{hashtags}"
                ],
                "hooks": [
                    "Weekend Feast Alert!",
                    "Family Weekend Special",
                    "TGIF Special Offer",
                    "Weekend Vibes at {business_name}"
                ],
                "cta": ["Book now!", "Limited seats!", "Order today!", "Don't miss out!"]
            },
            "new_dish": {
                "structure": [
                    "🆕 NEW ARRIVAL! 🍽️",
                    "",
                    "Introducing {dish_name}",
                    "{description}",
                    "",
                    "✅ 100% HALAL",
                    "✅ {unique_features}",
                    "✅ Available for dine-in & delivery",
                    "",
                    "Try it today at {business_name}!",
                    "",
                    "{hashtags}"
                ]
            },
            "delivery_promo": {
                "structure": [
                    "🚗 FREE DELIVERY ALERT! 🎉",
                    "",
                    "{offer_details}",
                    "",
                    "📱 Order through:",
                    "• Talabat",
                    "• Deliveroo", 
                    "• Direct call: {phone}",
                    "",
                    "⏰ {validity}",
                    "📍 Delivery areas: {areas}",
                    "",
                    "{hashtags}"
                ]
            }
        }
        
        template_type = content_type.lower()
        if template_type not in templates:
            template_type = "weekend_special"  # Default
            
        template = templates[template_type]
        
        result = {
            "template_type": content_type,
            "structure": template["structure"],
            "customization_tips": [
                "Replace {placeholders} with actual content",
                "Add emojis relevant to your cuisine",
                "Include high-quality food images",
                "Mention HALAL certification prominently"
            ],
            "kuwait_specific_elements": [
                "Prayer time awareness",
                "Family-friendly emphasis",
                "Air conditioning mention (summer)",
                "Delivery platform integration"
            ]
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error generating template: {str(e)}")
        return f"Error generating template: {str(e)}"


@tool("Hashtag Optimizer Tool")
def optimize_hashtags(content_topic: str, target_audience: str) -> str:
    """
    Generates optimized hashtag sets for Kuwait F&B content.
    Topics: food_post, restaurant_promo, delivery, family_dining, healthy_food
    Audiences: families, young_professionals, foodies, health_conscious
    """
    try:
        # Base Kuwait hashtags
        kuwait_general = ["#Kuwait", "#Q8", "#الكويت", "#KuwaitFood", "#Q8Food"]
        
        # Topic-specific hashtags
        topic_hashtags = {
            "food_post": ["#InstaFood", "#FoodStagram", "#Foodie", "#Delicious", "#طعام"],
            "restaurant_promo": ["#KuwaitRestaurants", "#Q8Restaurants", "#DineInKuwait", "#مطاعم_الكويت"],
            "delivery": ["#KuwaitDelivery", "#OrderNow", "#FoodDelivery", "#توصيل", "#Talabat"],
            "family_dining": ["#FamilyTime", "#KidsMenu", "#FamilyRestaurant", "#عائلة"],
            "healthy_food": ["#HealthyEating", "#CleanEating", "#HealthyKuwait", "#صحي"]
        }
        
        # Audience-specific hashtags
        audience_hashtags = {
            "families": ["#KuwaitFamilies", "#FamilyFriendly", "#KidsEatFree", "#WeekendFamily"],
            "young_professionals": ["#LunchBreak", "#QuickBites", "#WorkLunch", "#Q8Life"],
            "foodies": ["#FoodBlogger", "#KuwaitFoodie", "#MustTry", "#FoodGram"],
            "health_conscious": ["#FitFood", "#ProteinPower", "#LowCarb", "#GymFood"]
        }
        
        # Trending seasonal hashtags
        current_month = datetime.now().month
        seasonal = []
        if current_month in [6, 7, 8]:  # Summer
            seasonal = ["#SummerVibes", "#BeatTheHeat", "#صيف"]
        elif current_month in [3, 4]:  # Ramadan period
            seasonal = ["#Ramadan", "#Iftar", "#Suhoor", "#رمضان"]
            
        # Combine hashtags
        selected_hashtags = kuwait_general.copy()
        selected_hashtags.extend(topic_hashtags.get(content_topic, topic_hashtags["food_post"]))
        selected_hashtags.extend(audience_hashtags.get(target_audience, audience_hashtags["families"]))
        selected_hashtags.extend(seasonal)
        
        # Mix Arabic and English
        result = {
            "primary_hashtags": selected_hashtags[:10],
            "secondary_hashtags": selected_hashtags[10:20],
            "total_count": len(selected_hashtags),
            "tips": [
                "Use 20-30 hashtags on Instagram",
                "Place hashtags in first comment for cleaner look",
                "Mix popular and niche hashtags",
                "Include location-specific tags"
            ],
            "performance_forecast": "Expected reach increase: 40-60%"
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error optimizing hashtags: {str(e)}")
        return f"Error optimizing hashtags: {str(e)}"


@tool("Emoji Food Expert Tool")
def suggest_food_emojis(dish_type: str, mood: str) -> str:
    """
    Suggests appropriate emojis for F&B content based on dish type and mood.
    Dish types: burger, pizza, seafood, arabic, dessert, beverage, healthy
    Moods: exciting, family_friendly, premium, casual, urgent
    """
    try:
        # Dish-specific emojis
        dish_emojis = {
            "burger": ["🍔", "🍟", "🥤", "🧀", "🥓"],
            "pizza": ["🍕", "🧀", "🍅", "🌶️", "🇮🇹"],
            "seafood": ["🦐", "🐟", "🦞", "🦑", "🌊"],
            "arabic": ["🥙", "🍖", "🥘", "🍚", "🫓"],
            "dessert": ["🍰", "🍮", "🍨", "🧁", "🍪"],
            "beverage": ["☕", "🥤", "🧃", "🍹", "🧋"],
            "healthy": ["🥗", "🥑", "🥦", "🍳", "💪"]
        }
        
        # Mood-specific emojis
        mood_emojis = {
            "exciting": ["🎉", "🔥", "✨", "🌟", "💥"],
            "family_friendly": ["👨‍👩‍👧‍👦", "❤️", "😊", "🏠", "👶"],
            "premium": ["💎", "⭐", "🏆", "👑", "✨"],
            "casual": ["😎", "👍", "🤤", "😋", "🙌"],
            "urgent": ["⏰", "🏃", "📢", "⚡", "🔥"]
        }
        
        # Kuwait-specific emojis
        kuwait_emojis = ["🇰🇼", "🕌", "🌴", "☀️", "🏖️"]
        
        # Service emojis
        service_emojis = {
            "delivery": ["🚗", "📱", "🛵"],
            "dine_in": ["🍽️", "🪑", "🏠"],
            "takeaway": ["🥡", "🛍️", "📦"]
        }
        
        selected_dish = dish_emojis.get(dish_type, dish_emojis["arabic"])
        selected_mood = mood_emojis.get(mood, mood_emojis["casual"])
        
        result = {
            "dish_emojis": selected_dish,
            "mood_emojis": selected_mood,
            "kuwait_touch": random.sample(kuwait_emojis, 2),
            "suggested_combinations": [
                f"{selected_mood[0]} {selected_dish[0]} {selected_mood[1]}",
                f"{kuwait_emojis[0]} {selected_dish[0]} {selected_dish[1]} {selected_mood[0]}",
                f"{selected_mood[0]} {' '.join(selected_dish[:3])} {kuwait_emojis[0]}"
            ],
            "usage_tips": [
                "Don't overuse emojis - 5-8 per post is ideal",
                "Place emojis at line beginnings for structure",
                "Use food emojis near dish descriptions",
                "Add flag emoji for local pride"
            ]
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error suggesting emojis: {str(e)}")
        return f"Error suggesting emojis: {str(e)}"


@tool("Caption Enhancement Tool")
def enhance_caption(original_caption: str, enhancement_type: str) -> str:
    """
    Enhances existing captions with Kuwait F&B best practices.
    Enhancement types: add_arabic, add_cta, add_urgency, add_social_proof, add_benefits
    """
    try:
        enhancements = {
            "add_arabic": {
                "method": "Add Arabic translation of key points",
                "example": "Delicious! → Delicious! لذيذ! 😋"
            },
            "add_cta": {
                "method": "Add clear call-to-action",
                "options": [
                    "📞 Call now: [PHONE]",
                    "📱 Order via link in bio",
                    "💬 DM us to reserve",
                    "🏃 Walk-ins welcome!"
                ]
            },
            "add_urgency": {
                "method": "Create time sensitivity",
                "phrases": [
                    "⏰ Today only!",
                    "🔥 Limited time offer",
                    "⚡ While supplies last",
                    "📅 This weekend only"
                ]
            },
            "add_social_proof": {
                "method": "Include customer validation",
                "phrases": [
                    "⭐ Rated 4.9/5 by 500+ customers",
                    "🏆 Winner of Best [Cuisine] 2024",
                    "❤️ Kuwait's favorite [dish]",
                    "👥 Join 10,000+ satisfied customers"
                ]
            },
            "add_benefits": {
                "method": "Highlight customer benefits",
                "benefits": [
                    "✅ 100% HALAL certified",
                    "❄️ Fully air-conditioned",
                    "👨‍👩‍👧‍👦 Family section available",
                    "🚗 Free parking",
                    "📱 Easy online ordering"
                ]
            }
        }
        
        enhancement = enhancements.get(enhancement_type, enhancements["add_cta"])
        
        result = {
            "original": original_caption,
            "enhancement_type": enhancement_type,
            "enhancement_method": enhancement["method"],
            "suggested_additions": enhancement.get("options", enhancement.get("phrases", enhancement.get("benefits", []))),
            "example_enhanced": f"{original_caption}\n\n{random.choice(enhancement.get('options', enhancement.get('phrases', enhancement.get('benefits', []))))}",
            "best_practices": [
                "Keep first line attention-grabbing",
                "Include HALAL mention for trust",
                "Add delivery options clearly",
                "End with clear CTA",
                "Use line breaks for readability"
            ]
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error enhancing caption: {str(e)}")
        return f"Error enhancing caption: {str(e)}"