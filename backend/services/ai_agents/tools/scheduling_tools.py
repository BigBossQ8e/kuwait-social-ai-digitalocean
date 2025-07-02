"""
Scheduling Tools for Kuwait Social Media Optimization
"""

from crewai.tools import tool
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta, time
import pytz
import random

@tool("Prayer Time Scheduler")
def prayer_time_scheduler_tool(desired_time: str, date: str, content_type: str = "post") -> str:
    """Find optimal posting times that avoid Kuwait prayer times"""
    
    # Parse date
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        is_friday = target_date.weekday() == 4
        is_ramadan = _is_ramadan(target_date)
    except:
        target_date = datetime.now()
        is_friday = False
        is_ramadan = False
    
    # Kuwait prayer times (adjusted for season/Ramadan)
    if is_ramadan:
        prayer_times = {
            "Fajr": {"start": "04:00", "end": "04:30", "buffer": 15},
            "Dhuhr": {"start": "11:45", "end": "12:15", "buffer": 15},
            "Asr": {"start": "15:00", "end": "15:30", "buffer": 15},
            "Maghrib": {"start": "18:00", "end": "18:45", "buffer": 30},  # Iftar time - longer buffer
            "Isha": {"start": "19:30", "end": "20:00", "buffer": 15},
            "Taraweeh": {"start": "20:00", "end": "21:30", "buffer": 15}
        }
    else:
        prayer_times = {
            "Fajr": {"start": "04:30", "end": "05:00", "buffer": 15},
            "Dhuhr": {"start": "11:45", "end": "12:15", "buffer": 15},
            "Asr": {"start": "15:00", "end": "15:30", "buffer": 15},
            "Maghrib": {"start": "17:45", "end": "18:15", "buffer": 15},
            "Isha": {"start": "19:15", "end": "19:45", "buffer": 15}
        }
    
    # Friday prayer special handling
    if is_friday:
        prayer_times["Jummah"] = {"start": "11:30", "end": "13:00", "buffer": 30}
    
    # Check if desired time conflicts
    conflicts = _check_prayer_conflicts(desired_time, prayer_times)
    
    # Get optimal slots based on content type
    optimal_slots = _get_optimal_slots(content_type, is_ramadan, is_friday)
    
    # Find best alternative if conflict
    if conflicts:
        recommended_time = _find_next_safe_time(desired_time, prayer_times, optimal_slots)
    else:
        recommended_time = desired_time
    
    # Get engagement prediction
    engagement_score = _predict_engagement(recommended_time, content_type, is_ramadan)
    
    result = {
        "requested_time": desired_time,
        "recommended_time": recommended_time,
        "is_safe": len(conflicts) == 0,
        "conflicts": conflicts,
        "date_info": {
            "date": date,
            "is_friday": is_friday,
            "is_ramadan": is_ramadan,
            "is_weekend": target_date.weekday() in [4, 5]
        },
        "optimal_slots": optimal_slots,
        "engagement_prediction": engagement_score,
        "posting_strategy": _get_posting_strategy(content_type, is_ramadan),
        "buffer_recommendation": "Post 15-30 minutes after prayer ends for best reach"
    }
    
    return json.dumps(result, indent=2)
    
def _is_ramadan(date: datetime) -> bool:
    """Check if date falls in Ramadan (simplified)"""
    # In production, use actual Islamic calendar
    # This is a placeholder
    month = date.month
    return month in [3, 4]  # Approximate Ramadan months
    
def _check_prayer_conflicts(time_str: str, prayer_times: Dict) -> List[Dict]:
    """Check if time conflicts with prayers"""
    conflicts = []
    try:
        hour, minute = map(int, time_str.split(':'))
        check_time = hour * 60 + minute
        
        for prayer, times in prayer_times.items():
            start_h, start_m = map(int, times["start"].split(':'))
            end_h, end_m = map(int, times["end"].split(':'))
            buffer = times["buffer"]
            
            prayer_start = start_h * 60 + start_m - buffer
            prayer_end = end_h * 60 + end_m + buffer
            
            if prayer_start <= check_time <= prayer_end:
                conflicts.append({
                    "prayer": prayer,
                    "time_range": f"{times['start']}-{times['end']}",
                    "reason": f"Too close to {prayer} prayer time"
                })
    except:
        pass
    
    return conflicts
    
def _get_optimal_slots(content_type: str, is_ramadan: bool, is_friday: bool) -> List[Dict]:
    """Get optimal posting slots"""
    if is_ramadan:
        slots = [
            {"time": "10:00-11:30", "reason": "Pre-lunch hunger", "score": 85},
            {"time": "14:00-15:00", "reason": "Afternoon cravings", "score": 75},
            {"time": "16:30-17:45", "reason": "Pre-iftar planning", "score": 95},
            {"time": "21:30-23:00", "reason": "Post-iftar active time", "score": 90},
            {"time": "00:00-01:00", "reason": "Late night Ramadan activity", "score": 80}
        ]
    elif is_friday:
        slots = [
            {"time": "08:00-10:00", "reason": "Weekend morning browsing", "score": 80},
            {"time": "14:00-16:00", "reason": "Post-Jummah family time", "score": 85},
            {"time": "19:00-22:00", "reason": "Weekend evening peak", "score": 90}
        ]
    else:
        slots = [
            {"time": "07:00-09:00", "reason": "Morning commute", "score": 75},
            {"time": "12:30-14:30", "reason": "Lunch decisions", "score": 85},
            {"time": "17:00-17:30", "reason": "Evening commute", "score": 80},
            {"time": "20:00-22:00", "reason": "Evening browsing", "score": 90}
        ]
    
    return sorted(slots, key=lambda x: x["score"], reverse=True)
    
def _find_next_safe_time(current_time: str, prayer_times: Dict, optimal_slots: List) -> str:
    """Find next safe posting time"""
    try:
        hour, minute = map(int, current_time.split(':'))
        current_minutes = hour * 60 + minute
        
        # Check optimal slots first
        for slot in optimal_slots:
            slot_start = slot["time"].split('-')[0]
            s_hour, s_min = map(int, slot_start.split(':'))
            slot_minutes = s_hour * 60 + s_min
            
            if slot_minutes > current_minutes:
                # Verify no prayer conflict
                if not _check_prayer_conflicts(slot_start, prayer_times):
                    return slot_start
        
        # If no optimal slot, find any safe time
        return "20:00"  # Default safe evening time
    except:
        return "20:00"
    
def _predict_engagement(time: str, content_type: str, is_ramadan: bool) -> Dict:
    """Predict engagement based on timing"""
    base_scores = {
        "07:00-09:00": 70,
        "10:00-12:00": 75,
        "12:00-14:00": 85,
        "14:00-17:00": 65,
        "17:00-19:00": 80,
        "19:00-22:00": 90,
        "22:00-24:00": 60
    }
    
    # Ramadan adjustments
    if is_ramadan:
        base_scores["16:00-18:00"] = 95  # Pre-iftar
        base_scores["21:00-23:00"] = 90  # Post-iftar
    
    # Get score for time
    hour = int(time.split(':')[0])
    score = 75  # default
    
    for time_range, range_score in base_scores.items():
        start, end = time_range.split('-')
        start_h = int(start.split(':')[0])
        end_h = int(end.split(':')[0])
        
        if start_h <= hour < end_h:
            score = range_score
            break
    
    return {
        "score": score,
        "rating": "Excellent" if score >= 85 else "Good" if score >= 70 else "Fair",
        "tips": _get_engagement_tips(score, content_type)
    }
    
def _get_engagement_tips(score: int, content_type: str) -> List[str]:
    """Get tips for improving engagement"""
    tips = []
    
    if score < 70:
        tips.append("Consider posting during peak hours (12-2 PM or 7-10 PM)")
    
    if content_type == "story":
        tips.append("Stories perform best in evening hours (7-11 PM)")
    elif content_type == "reel":
        tips.append("Reels get more views when posted 6-8 PM")
    
    tips.append("Include trending Kuwait hashtags for this time slot")
    tips.append("Engage with comments in first 30 minutes")
    
    return tips
    
def _get_posting_strategy(content_type: str, is_ramadan: bool) -> Dict:
    """Get posting strategy recommendations"""
    if is_ramadan:
        strategy = {
            "frequency": "2-3 times daily",
            "key_times": ["Pre-iftar (5-6 PM)", "Post-iftar (9-10 PM)"],
            "content_focus": ["Iftar specials", "Suhoor options", "Family meals"],
            "avoid": ["Lunch posts", "Daytime food imagery"]
        }
    else:
        strategy = {
            "frequency": "1-2 times daily",
            "key_times": ["Lunch (12-2 PM)", "Dinner (7-9 PM)"],
            "content_focus": ["Daily specials", "New items", "Promotions"],
            "avoid": ["Prayer times", "Very early morning"]
        }
    
    return strategy

@tool("Peak Time Analyzer")
def peak_time_analyzer_tool(platform: str, business_type: str, target_audience: str = "general") -> str:
    """Identify peak engagement times for different platforms and audiences in Kuwait"""
    
    # Platform-specific peak times for Kuwait
    platform_peaks = {
        "instagram": {
            "weekday": {
                "morning": {"time": "07:00-09:00", "engagement": 70, "best_content": "stories, quick posts"},
                "lunch": {"time": "12:00-14:00", "engagement": 85, "best_content": "food photos, offers"},
                "evening": {"time": "19:00-22:00", "engagement": 90, "best_content": "reels, carousel posts"},
                "late_night": {"time": "22:00-00:00", "engagement": 65, "best_content": "stories"}
            },
            "weekend": {
                "morning": {"time": "09:00-11:00", "engagement": 75, "best_content": "brunch posts"},
                "afternoon": {"time": "14:00-17:00", "engagement": 80, "best_content": "family content"},
                "evening": {"time": "19:00-23:00", "engagement": 95, "best_content": "all content types"}
            }
        },
        "tiktok": {
            "weekday": {
                "morning": {"time": "06:00-08:00", "engagement": 60, "best_content": "quick tips"},
                "lunch": {"time": "12:00-13:00", "engagement": 75, "best_content": "food trends"},
                "evening": {"time": "18:00-21:00", "engagement": 90, "best_content": "viral content"},
                "late_night": {"time": "21:00-01:00", "engagement": 85, "best_content": "entertainment"}
            }
        },
        "twitter": {
            "weekday": {
                "morning": {"time": "08:00-10:00", "engagement": 75, "best_content": "news, updates"},
                "lunch": {"time": "12:00-13:00", "engagement": 70, "best_content": "quick updates"},
                "evening": {"time": "20:00-22:00", "engagement": 80, "best_content": "discussions"}
            }
        }
    }
    
    # Business type adjustments
    business_adjustments = {
        "cafe": {"morning": +10, "afternoon": +5},
        "restaurant": {"lunch": +10, "dinner": +15},
        "dessert": {"afternoon": +10, "evening": +10},
        "fast_food": {"lunch": +15, "late_night": +10},
        "bakery": {"morning": +15, "afternoon": +5}
    }
    
    # Get platform data
    platform_data = platform_peaks.get(platform.lower(), platform_peaks["instagram"])
    
    # Analyze for specific business type
    peak_times = []
    for day_type in ["weekday", "weekend"]:
        for period, data in platform_data.get(day_type, {}).items():
            engagement = data["engagement"]
            
            # Apply business type adjustments
            if business_type.lower() in business_adjustments:
                for adjust_period, adjustment in business_adjustments[business_type.lower()].items():
                    if adjust_period in period:
                        engagement += adjustment
            
            peak_times.append({
                "day_type": day_type,
                "period": period,
                "time": data["time"],
                "engagement_score": min(engagement, 100),
                "best_content": data["best_content"]
            })
    
    # Sort by engagement
    peak_times.sort(key=lambda x: x["engagement_score"], reverse=True)
    
    # Audience-specific insights
    audience_insights = _get_audience_insights(target_audience)
    
    result = {
        "platform": platform,
        "business_type": business_type,
        "top_3_peaks": peak_times[:3],
        "detailed_schedule": {
            "weekday": [p for p in peak_times if p["day_type"] == "weekday"][:4],
            "weekend": [p for p in peak_times if p["day_type"] == "weekend"][:4]
        },
        "audience_insights": audience_insights,
        "optimization_tips": [
            f"Post {business_type} content during lunch rush (12-2 PM) on weekdays",
            "Weekend evenings (7-11 PM) show highest engagement",
            "Avoid posting during prayer times",
            f"Use {platform} analytics to refine these times for your specific audience"
        ],
        "content_calendar_suggestion": _generate_calendar_suggestion(platform, business_type)
    }
    
    return json.dumps(result, indent=2)
    
def _get_audience_insights(target_audience: str) -> Dict:
    """Get audience-specific insights"""
    audience_data = {
        "families": {
            "peak_times": ["Weekend afternoons", "Weekday evenings after 7 PM"],
            "content_preference": ["Family meals", "Kids options", "Value deals"],
            "avoid": ["Very late night posts", "Single-person meals"]
        },
        "young_professionals": {
            "peak_times": ["Lunch hours", "Late evenings", "Weekend nights"],
            "content_preference": ["Quick meals", "Trendy items", "Coffee"],
            "avoid": ["Early morning posts", "Heavy traditional meals during work hours"]
        },
        "students": {
            "peak_times": ["Late morning", "Late night", "Weekend afternoons"],
            "content_preference": ["Budget options", "Study-friendly cafes", "Group deals"],
            "avoid": ["Early morning", "Expensive items"]
        }
    }
    
    return audience_data.get(target_audience, {
        "peak_times": ["Lunch and dinner hours"],
        "content_preference": ["Varied content"],
        "avoid": ["Prayer times"]
    })
    
def _generate_calendar_suggestion(platform: str, business_type: str) -> Dict:
    """Generate posting calendar suggestion"""
    if platform.lower() == "instagram":
        return {
            "posts_per_week": 7,
            "stories_per_day": 3,
            "reels_per_week": 3,
            "best_days": ["Sunday", "Tuesday", "Thursday"],
            "schedule": {
                "Monday": "12:30 PM - Lunch special",
                "Tuesday": "7:00 PM - New item feature",
                "Wednesday": "2:00 PM - Behind the scenes",
                "Thursday": "8:00 PM - Weekend preview",
                "Friday": "6:00 PM - Family meal deals",
                "Saturday": "7:30 PM - Saturday night specials",
                "Sunday": "12:00 PM - Week starter"
            }
        }
    else:
        return {
            "posts_per_week": 5,
            "best_days": ["Sunday", "Wednesday", "Thursday"],
            "general_schedule": "Post during peak hours identified above"
        }

@tool("Weather Aware Scheduler")
def weather_aware_scheduler_tool(date: str, content_category: str) -> str:
    """Optimize posting schedule based on Kuwait weather and seasonal patterns"""
    
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        month = target_date.month
    except:
        month = datetime.now().month
    
    # Kuwait seasonal patterns
    if month in [6, 7, 8]:  # Summer (June-August)
        season = "summer"
        weather = {
            "temperature": "45-50°C",
            "conditions": "Extreme heat, sandstorms possible",
            "behavior": "Indoor preference, late night activities",
            "food_preferences": ["Cold beverages", "Ice cream", "Light meals", "Salads"]
        }
    elif month in [11, 12, 1, 2]:  # Winter (November-February)
        season = "winter"
        weather = {
            "temperature": "10-25°C",
            "conditions": "Pleasant, occasional rain",
            "behavior": "Outdoor dining popular, earlier activities",
            "food_preferences": ["Hot beverages", "Soups", "Grills", "Heavy meals"]
        }
    else:  # Spring/Fall
        season = "mild"
        weather = {
            "temperature": "25-35°C",
            "conditions": "Mild, occasional dust",
            "behavior": "Mixed indoor/outdoor",
            "food_preferences": ["Varied menu items", "Seasonal specials"]
        }
    
    # Content recommendations based on weather
    content_recommendations = _get_weather_content_recs(season, content_category)
    
    # Timing adjustments
    timing_adjustments = _get_weather_timing(season)
    
    result = {
        "date": date,
        "season": season,
        "weather": weather,
        "content_recommendations": content_recommendations,
        "timing_adjustments": timing_adjustments,
        "posting_strategy": {
            "frequency": "Increase posts on extreme weather days" if season == "summer" else "Normal frequency",
            "focus": weather["food_preferences"],
            "messaging": _get_weather_messaging(season, content_category)
        },
        "engagement_tips": [
            f"Emphasize {'air conditioning and indoor comfort' if season == 'summer' else 'outdoor seating'} in posts",
            f"Feature {weather['food_preferences'][0]} prominently",
            "Include weather-related emojis and references",
            "Adjust delivery messaging based on weather conditions"
        ]
    }
    
    return json.dumps(result, indent=2)
    
def _get_weather_content_recs(season: str, category: str) -> List[Dict]:
    """Get weather-based content recommendations"""
    recs = []
    
    if season == "summer" and category in ["beverages", "desserts"]:
        recs = [
            {"content": "Iced coffee varieties", "reason": "Beat the heat", "urgency": "high"},
            {"content": "Frozen desserts", "reason": "Cooling treats", "urgency": "high"},
            {"content": "Fresh juices", "reason": "Hydration focus", "urgency": "high"},
            {"content": "Indoor seating comfort", "reason": "AC emphasis", "urgency": "medium"}
        ]
    elif season == "winter" and category in ["beverages", "mains"]:
        recs = [
            {"content": "Hot soups and stews", "reason": "Comfort food", "urgency": "high"},
            {"content": "Grilled items", "reason": "Outdoor dining weather", "urgency": "medium"},
            {"content": "Hot beverages", "reason": "Warming drinks", "urgency": "high"},
            {"content": "Outdoor seating ambiance", "reason": "Perfect weather", "urgency": "high"}
        ]
    else:
        recs = [
            {"content": "Seasonal specials", "reason": "Variety seeking", "urgency": "medium"},
            {"content": "New menu items", "reason": "Good time to experiment", "urgency": "medium"}
        ]
    
    return recs
    
def _get_weather_timing(season: str) -> Dict:
    """Get weather-based timing adjustments"""
    if season == "summer":
        return {
            "shift_recommendation": "Post later in day",
            "peak_shifts": {
                "lunch": "12:00 PM → 1:00 PM (avoid peak heat)",
                "dinner": "7:00 PM → 9:00 PM (wait for cooler evening)",
                "late_night": "10:00 PM → 12:00 AM (high activity)"
            },
            "delivery_emphasis": "Very high - emphasize AC delivery vehicles"
        }
    elif season == "winter":
        return {
            "shift_recommendation": "Post earlier in day",
            "peak_shifts": {
                "lunch": "12:00 PM (no change)",
                "dinner": "6:00 PM → 7:00 PM (earlier sunset)",
                "late_night": "Less activity after 10 PM"
            },
            "delivery_emphasis": "Medium - promote both dine-in and delivery"
        }
    else:
        return {
            "shift_recommendation": "Standard timing",
            "peak_shifts": {"lunch": "12:00-2:00 PM", "dinner": "7:00-9:00 PM"},
            "delivery_emphasis": "Balanced approach"
        }
    
def _get_weather_messaging(season: str, category: str) -> List[str]:
    """Get weather-appropriate messaging"""
    if season == "summer":
        return [
            "Beat the heat with our refreshing " + category,
            "Stay cool indoors with AC comfort",
            "Free delivery - skip the heat!",
            "Chilled to perfection"
        ]
    elif season == "winter":
        return [
            "Warm up with our cozy " + category,
            "Perfect weather for outdoor dining",
            "Comfort food for cool evenings",
            "Gather around for warmth"
        ]
    else:
        return [
            "Perfect weather for " + category,
            "Enjoy the beautiful Kuwait weather",
            "Indoor or outdoor - your choice!"
        ]


# Create tool instances for backward compatibility
PrayerTimeSchedulerTool = prayer_time_scheduler_tool
PeakTimeAnalyzerTool = peak_time_analyzer_tool
WeatherAwareSchedulerTool = weather_aware_scheduler_tool