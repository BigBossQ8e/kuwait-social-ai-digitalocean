"""
Compliance and Scheduling Tools for Kuwait F&B - CrewAI v0.5.0 Compatible
"""

from crewai.tools import tool
import json
from datetime import datetime, time, timedelta
import logging

logger = logging.getLogger(__name__)

@tool("Halal Verification Tool")
def verify_halal_compliance(content: str, menu_items: str) -> str:
    """
    Verifies that content and menu items comply with Halal standards.
    Checks for: proper certification mentions, ingredient compliance, and messaging appropriateness.
    """
    try:
        # Keywords to check
        halal_keywords = ["halal", "حلال", "certified", "100% halal"]
        non_compliant = ["pork", "alcohol", "wine", "beer", "bacon", "ham"]
        
        content_lower = content.lower()
        items_lower = menu_items.lower()
        
        # Check for halal mentions
        has_halal_mention = any(keyword in content_lower for keyword in halal_keywords)
        
        # Check for non-compliant items
        violations = [item for item in non_compliant if item in items_lower or item in content_lower]
        
        result = {
            "status": "COMPLIANT" if not violations and has_halal_mention else "NEEDS_ATTENTION",
            "halal_mention_found": has_halal_mention,
            "violations_found": violations,
            "recommendations": [],
            "suggested_text": "✅ 100% HALAL Certified"
        }
        
        if not has_halal_mention:
            result["recommendations"].append("Add clear HALAL certification mention")
            result["recommendations"].append("Use '100% HALAL' for stronger trust signal")
            
        if violations:
            result["recommendations"].append(f"Remove non-halal references: {', '.join(violations)}")
            result["status"] = "NON_COMPLIANT"
            
        result["compliance_checklist"] = {
            "halal_certification_mentioned": has_halal_mention,
            "no_alcohol_references": "alcohol" not in violations,
            "no_pork_products": not any(p in violations for p in ["pork", "bacon", "ham"]),
            "family_friendly_messaging": True  # Assumed for this example
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error in halal verification: {str(e)}")
        return f"Error verifying halal compliance: {str(e)}"


@tool("Cultural Appropriateness Checker")
def check_cultural_appropriateness(content: str, target_date: str = None) -> str:
    """
    Checks content for cultural appropriateness in Kuwait context.
    Considers religious sensitivities, local customs, and special periods like Ramadan.
    """
    try:
        # Cultural sensitivity checks
        sensitive_topics = {
            "dating": "Avoid romantic dating references, focus on family",
            "alcohol": "No alcohol references or bar imagery",
            "revealing": "Ensure modest presentation in images",
            "political": "Avoid political statements",
            "religious": "Respect religious sentiments"
        }
        
        # Check for Ramadan period (approximate)
        is_ramadan = False
        if target_date:
            # Simplified Ramadan check (would need proper Islamic calendar in production)
            month = datetime.strptime(target_date, "%Y-%m-%d").month
            is_ramadan = month == 3 or month == 4  # Approximate
            
        content_lower = content.lower()
        issues_found = []
        
        for topic, guidance in sensitive_topics.items():
            if topic in content_lower:
                issues_found.append({"topic": topic, "guidance": guidance})
                
        result = {
            "status": "APPROPRIATE" if not issues_found else "NEEDS_REVIEW",
            "is_ramadan_period": is_ramadan,
            "cultural_issues": issues_found,
            "recommendations": []
        }
        
        if is_ramadan:
            result["recommendations"].extend([
                "Focus on Iftar and Suhoor timings",
                "Emphasize family gathering aspects",
                "Consider special Ramadan offers",
                "Respect fasting hours in messaging"
            ])
            
        result["best_practices"] = [
            "Emphasize family values",
            "Use respectful language",
            "Include Arabic translations",
            "Respect prayer times",
            "Highlight HALAL certification"
        ]
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error in cultural check: {str(e)}")
        return f"Error checking cultural appropriateness: {str(e)}"


@tool("Prayer Time Scheduler")
def get_prayer_time_schedule(date: str, location: str = "Kuwait City") -> str:
    """
    Returns prayer times to avoid for social media posting.
    Helps schedule posts to respect prayer times in Kuwait.
    Date format: YYYY-MM-DD
    """
    try:
        # Approximate prayer times for Kuwait (these would be fetched from an API in production)
        prayer_times = {
            "Fajr": {"start": "04:30", "end": "05:00"},
            "Dhuhr": {"start": "11:45", "end": "12:15"},
            "Asr": {"start": "15:00", "end": "15:30"},
            "Maghrib": {"start": "17:45", "end": "18:15"},
            "Isha": {"start": "19:15", "end": "19:45"}
        }
        
        # Adjust slightly for summer/winter (simplified)
        month = datetime.strptime(date, "%Y-%m-%d").month
        if month in [6, 7, 8]:  # Summer months
            # Adjust Maghrib and Isha later
            prayer_times["Maghrib"] = {"start": "18:30", "end": "19:00"}
            prayer_times["Isha"] = {"start": "20:00", "end": "20:30"}
            
        result = {
            "date": date,
            "location": location,
            "prayer_times": prayer_times,
            "posting_windows": [
                {"window": "Morning", "time": "07:00 - 11:00", "quality": "Good"},
                {"window": "Afternoon", "time": "13:00 - 14:30", "quality": "Moderate"},
                {"window": "Evening", "time": "16:00 - 17:30", "quality": "Excellent"},
                {"window": "Night", "time": "20:30 - 22:00", "quality": "Good"}
            ],
            "avoid_times": [
                f"{prayer} prayer: {times['start']} - {times['end']}" 
                for prayer, times in prayer_times.items()
            ],
            "best_practices": [
                "Schedule posts 30 mins after prayer ends",
                "Avoid posting during Maghrib (Iftar time)",
                "Best engagement after Isha prayer",
                "Friday prayers (Jumu'ah) 12:00-13:00"
            ]
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting prayer times: {str(e)}")
        return f"Error getting prayer schedule: {str(e)}"


@tool("Weather-Aware Scheduler")
def get_weather_based_recommendations(date: str, menu_type: str) -> str:
    """
    Provides weather-aware content recommendations for Kuwait.
    Menu types: hot_food, cold_beverages, outdoor_dining, delivery_only
    """
    try:
        # Get month to determine season
        month = datetime.strptime(date, "%Y-%m-%d").month
        
        # Kuwait weather patterns
        weather_data = {
            "summer": {
                "months": [5, 6, 7, 8, 9],
                "temp_range": "40-50°C",
                "conditions": "Extremely hot, dusty",
                "recommendations": {
                    "hot_food": [
                        "Emphasize air-conditioned dining",
                        "Promote lighter, refreshing options",
                        "Highlight indoor family sections"
                    ],
                    "cold_beverages": [
                        "Perfect timing! Push refreshing drinks",
                        "Emphasize ice-cold options",
                        "Promote fresh juices and smoothies"
                    ],
                    "outdoor_dining": [
                        "Not recommended during day",
                        "Promote evening outdoor seating only",
                        "Emphasize misting systems if available"
                    ],
                    "delivery_only": [
                        "Ideal for summer heat",
                        "Emphasize cold packaging",
                        "Promote lunch delivery heavily"
                    ]
                }
            },
            "winter": {
                "months": [11, 12, 1, 2],
                "temp_range": "10-25°C",
                "conditions": "Pleasant, occasional rain",
                "recommendations": {
                    "hot_food": [
                        "Perfect for comfort food",
                        "Promote soups and grills",
                        "Emphasize warm, hearty meals"
                    ],
                    "outdoor_dining": [
                        "Best season for outdoor dining",
                        "Promote garden and terrace seating",
                        "Highlight shisha if available"
                    ]
                }
            }
        }
        
        # Determine season
        season = "summer" if month in weather_data["summer"]["months"] else "winter"
        if month in [3, 4, 10]:
            season = "spring/fall"
            
        weather_info = weather_data.get(season, weather_data["winter"])
        recommendations = weather_info["recommendations"].get(menu_type, [
            "Adapt menu promotion to weather",
            "Consider customer comfort",
            "Emphasize appropriate amenities"
        ])
        
        result = {
            "date": date,
            "season": season,
            "weather_conditions": weather_info.get("conditions", "Moderate"),
            "temperature_range": weather_info.get("temp_range", "20-35°C"),
            "content_recommendations": recommendations,
            "timing_suggestions": {
                "summer": "Focus on evening posts (after 6 PM)",
                "winter": "Lunch and dinner times equally good",
                "general": "Avoid midday in summer months"
            },
            "seasonal_menu_ideas": {
                "summer": ["Salads", "Cold mezze", "Fresh juices", "Ice cream"],
                "winter": ["Grills", "Soups", "Hot beverages", "Comfort foods"]
            }
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error in weather scheduler: {str(e)}")
        return f"Error getting weather recommendations: {str(e)}"