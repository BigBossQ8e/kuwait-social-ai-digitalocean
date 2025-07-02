"""
Compliance Tools for Kuwait Cultural and Religious Requirements
"""

from crewai.tools import tool
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, time
import pytz

@tool("Halal Verification")
def halal_verification_tool(content: str, restaurant_type: str, ingredients: Optional[List[str]] = None) -> str:
    """Verify halal compliance and suggest improvements for Kuwait F&B content"""
    ingredients = ingredients or []
    
    # Halal/Haram keywords
    halal_positive = ["halal", "حلال", "zabiha", "ذبيحة", "halal certified", "100% halal"]
    haram_items = ["pork", "خنزير", "alcohol", "wine", "beer", "vodka", "whiskey", "bacon", "ham", "lard"]
    questionable_items = ["gelatin", "vanilla extract", "marshmallow", "certain e-numbers"]
    
    # Check content
    content_lower = content.lower()
    issues = []
    suggestions = []
    
    # Check for haram items
    for item in haram_items:
        if item in content_lower or item in str(ingredients).lower():
            issues.append(f"Content contains haram item: {item}")
    
    # Check for halal mentions
    has_halal_mention = any(term in content_lower for term in halal_positive)
    
    # Restaurant type specific checks
    if restaurant_type.lower() in ["steakhouse", "burger", "chicken", "meat"]:
        if not has_halal_mention:
            suggestions.append("Add 'حلال 100%' or 'All meat is Halal certified' prominently")
            suggestions.append("Mention specific halal certification if available")
    
    if restaurant_type.lower() in ["bakery", "dessert", "cafe"]:
        suggestions.append("Clarify that no alcohol is used in desserts")
        suggestions.append("Mention if vanilla extract is alcohol-free")
    
    # Check ingredients
    for ingredient in ingredients:
        if ingredient.lower() in questionable_items:
            suggestions.append(f"Clarify the source of {ingredient} (must be halal-certified)")
    
    # Generate recommendations
    if not has_halal_mention and not issues:
        suggestions.append("Consider adding halal assurance for Muslim customers")
    
    halal_phrases = {
        "english": [
            "100% Halal Certified",
            "All our meat is Zabiha Halal",
            "Proudly serving Halal food",
            "Halal - Hand slaughtered",
            "Certified Halal by [Authority]"
        ],
        "arabic": [
            "حلال ١٠٠٪",
            "جميع اللحوم حلال",
            "ذبح حلال",
            "مصدق حلال",
            "نفتخر بتقديم الطعام الحلال"
        ]
    }
    
    result = {
        "is_compliant": len(issues) == 0,
        "has_halal_mention": has_halal_mention,
        "issues": issues,
        "suggestions": suggestions,
        "recommended_phrases": halal_phrases,
        "placement_tips": [
            "Place halal mention in first 2 lines",
            "Use halal emoji: 🥩✅ or 🍖✅",
            "Include in image if possible",
            "Add to restaurant bio"
        ]
    }
    
    return json.dumps(result, indent=2)

@tool("Cultural Check")
def cultural_check_tool(content: str, content_type: str, target_audience: str = "general") -> str:
    """Ensure content respects Kuwait cultural norms and values"""
    
    # Cultural sensitivity checks
    inappropriate_content = {
        "romantic": ["dating", "valentine", "couples", "romantic dinner", "date night"],
        "alcohol_related": ["happy hour", "wine pairing", "cocktail", "beer", "champagne"],
        "inappropriate_imagery": ["revealing clothing", "bikini", "shorts", "mini skirt"],
        "offensive_language": ["damn", "hell", "jesus", "oh my god"],
        "political": ["government", "politics", "protest", "democracy"],
        "controversial": ["lgbt", "pride", "israel", "palestine"]
    }
    
    # Positive cultural elements
    positive_elements = {
        "family": ["family", "عائلة", "kids", "children", "family-friendly"],
        "traditional": ["traditional", "تقليدي", "authentic", "heritage", "تراث"],
        "religious": ["bismillah", "بسم الله", "alhamdulillah", "الحمد لله", "blessed"],
        "community": ["gathering", "تجمع", "sharing", "together", "community"],
        "hospitality": ["welcome", "أهلا وسهلا", "generous", "كرم", "hospitality"]
    }
    
    content_lower = content.lower()
    issues = []
    warnings = []
    positive_aspects = []
    
    # Check for inappropriate content
    for category, terms in inappropriate_content.items():
        for term in terms:
            if term in content_lower:
                if category in ["romantic", "inappropriate_imagery"]:
                    warnings.append(f"Content may be too {category}: '{term}'")
                else:
                    issues.append(f"Inappropriate content detected ({category}): '{term}'")
    
    # Check for positive elements
    for category, terms in positive_elements.items():
        for term in terms:
            if term in content_lower:
                positive_aspects.append(f"Good use of {category} values: '{term}'")
    
    # Content type specific checks
    if content_type == "image":
        warnings.append("Ensure all people are modestly dressed")
        warnings.append("Avoid male-female interactions that might be misinterpreted")
    
    # Target audience considerations
    if target_audience == "youth":
        suggestions = ["Use trendy but respectful language", "Reference local youth culture appropriately"]
    elif target_audience == "families":
        suggestions = ["Emphasize family values", "Highlight kid-friendly options"]
    else:
        suggestions = ["Keep content universally appropriate", "Balance modern and traditional elements"]
    
    # Language recommendations
    language_tips = {
        "greetings": {
            "arabic": ["أهلاً وسهلاً", "مرحباً", "تفضل"],
            "english": ["Welcome", "Greetings", "We're honored to serve you"]
        },
        "appreciation": {
            "arabic": ["شكراً", "الحمد لله", "بارك الله فيك"],
            "english": ["Thank you", "We appreciate you", "Grateful"]
        }
    }
    
    result = {
        "is_appropriate": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "positive_aspects": positive_aspects,
        "suggestions": suggestions,
        "language_recommendations": language_tips,
        "general_guidelines": [
            "Respect Islamic values and traditions",
            "Emphasize family and community",
            "Use modest imagery and language",
            "Avoid controversial topics",
            "Celebrate local culture appropriately"
        ]
    }
    
    return json.dumps(result, indent=2)

@tool("Prayer Time Awareness")
def prayer_time_awareness_tool(posting_time: str, day_type: str = "weekday") -> str:
    """Check if content timing respects prayer times in Kuwait"""
    
    # Kuwait prayer time windows (approximate, varies by season)
    prayer_times = {
        "fajr": {"start": "04:00", "end": "05:30", "name_ar": "الفجر"},
        "dhuhr": {"start": "11:45", "end": "12:30", "name_ar": "الظهر"},
        "asr": {"start": "15:00", "end": "15:45", "name_ar": "العصر"},
        "maghrib": {"start": "17:30", "end": "18:15", "name_ar": "المغرب"},
        "isha": {"start": "19:00", "end": "19:45", "name_ar": "العشاء"}
    }
    
    # Friday prayer special consideration
    friday_prayer = {"start": "11:30", "end": "13:00", "name_ar": "صلاة الجمعة"}
    
    # Parse posting time
    try:
        post_hour = int(posting_time.split(':')[0])
        post_minute = int(posting_time.split(':')[1])
        post_time = time(post_hour, post_minute)
    except:
        return json.dumps({"error": "Invalid time format. Use HH:MM"})
    
    # Check conflicts
    conflicts = []
    warnings = []
    
    # Check regular prayer times
    for prayer, times in prayer_times.items():
        start_hour, start_min = map(int, times["start"].split(':'))
        end_hour, end_min = map(int, times["end"].split(':'))
        
        prayer_start = time(start_hour, start_min)
        prayer_end = time(end_hour, end_min)
        
        # Simple time comparison (doesn't handle midnight crossover)
        if prayer_start <= post_time <= prayer_end:
            conflicts.append({
                "prayer": prayer,
                "prayer_ar": times["name_ar"],
                "time_range": f"{times['start']}-{times['end']}"
            })
    
    # Special Friday check
    if day_type.lower() == "friday" and "11:30" <= posting_time <= "13:00":
        conflicts.append({
            "prayer": "friday_prayer",
            "prayer_ar": friday_prayer["name_ar"],
            "time_range": f"{friday_prayer['start']}-{friday_prayer['end']}",
            "note": "Critical time - most men attend mosque"
        })
    
    # Generate recommendations
    optimal_times = []
    if post_hour < 11:
        optimal_times.extend(["09:00", "10:00", "10:30"])
    elif 13 <= post_hour < 15:
        optimal_times.extend(["13:30", "14:00", "14:30"])
    elif 16 <= post_hour < 17:
        optimal_times.extend(["16:00", "16:30", "17:00"])
    elif post_hour >= 20:
        optimal_times.extend(["20:00", "20:30", "21:00"])
    
    # Ramadan considerations
    ramadan_tips = [
        "During Ramadan, best times are just before Iftar (sunset)",
        "Avoid posting about food during fasting hours",
        "Late night (after Tarawih) sees high engagement"
    ]
    
    result = {
        "posting_time": posting_time,
        "has_conflicts": len(conflicts) > 0,
        "prayer_conflicts": conflicts,
        "warnings": warnings,
        "optimal_times_nearby": optimal_times[:3],
        "best_times_overall": {
            "weekday": ["10:00", "14:00", "20:00"],
            "friday": ["14:00", "16:00", "20:00"],
            "weekend": ["10:00", "15:00", "20:00"]
        },
        "ramadan_considerations": ramadan_tips,
        "general_advice": [
            "Avoid posting during prayer times",
            "Friday prayers (11:30-13:00) are especially important",
            "Evening times generally see higher engagement",
            "Consider your specific audience's routine"
        ]
    }
    
    return json.dumps(result, indent=2)


# Create tool instances for backward compatibility
HalalVerificationTool = halal_verification_tool
CulturalCheckTool = cultural_check_tool
PrayerTimeAwarenessTool = prayer_time_awareness_tool