"""
Research Tools for Kuwait F&B Market Analysis - CrewAI v0.5.0 Compatible
Using LangChain Tool pattern
"""

from langchain.tools import Tool
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def competitor_analysis_func(query: str) -> str:
    """
    Analyzes competitor restaurants in Kuwait for social media strategies and performance.
    """
    try:
        # Parse the query to extract restaurant type and area
        area = "Kuwait"  # Default
        cuisine_type = None
        
        # Simple keyword extraction
        if "Salmiya" in query:
            area = "Salmiya"
        elif "Kuwait City" in query:
            area = "Kuwait City"
        elif "Hawally" in query:
            area = "Hawally"
            
        if "burger" in query.lower():
            cuisine_type = "burger"
        elif "lebanese" in query.lower():
            cuisine_type = "Lebanese"
        elif "italian" in query.lower():
            cuisine_type = "Italian"
        
        # Simulate competitor analysis
        analysis = {
            "query": query,
            "area": area,
            "cuisine_type": cuisine_type,
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "top_competitors": [
                {
                    "name": f"Top {cuisine_type or 'Restaurant'} 1",
                    "instagram_followers": "45.2K",
                    "posting_frequency": "2x daily",
                    "best_performing_content": "Behind-the-scenes kitchen videos",
                    "average_engagement": "8.5%"
                },
                {
                    "name": f"Popular {cuisine_type or 'Restaurant'} 2",
                    "instagram_followers": "38.7K",
                    "posting_frequency": "Daily",
                    "best_performing_content": "Customer testimonials",
                    "average_engagement": "7.2%"
                }
            ],
            "insights": {
                "trending_content": ["Reels showing food preparation", "Family meal deals", "Delivery promotions"],
                "optimal_posting_times": ["12:30 PM - 1:30 PM", "7:00 PM - 9:00 PM"],
                "successful_hashtags": ["#KuwaitFood", "#Q8Eats", f"#{area}Restaurants"],
                "pricing_insights": "Most competitors offer family meals between 15-25 KWD"
            }
        }
        
        return json.dumps(analysis, indent=2)
        
    except Exception as e:
        logger.error(f"Error in competitor analysis: {str(e)}")
        return f"Error analyzing competitors: {str(e)}"


def trend_analysis_func(topic: str) -> str:
    """
    Analyzes current food trends in Kuwait social media.
    """
    try:
        # Simulate trend analysis
        trends = {
            "topic": topic,
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "trending_now": [
                {
                    "trend": "Protein-packed meals",
                    "growth": "+45% in last 30 days",
                    "popular_hashtags": ["#ProteinKuwait", "#HealthyQ8", "#FitnessFood"],
                    "opportunity": "Create high-protein menu items with clear nutritional info"
                },
                {
                    "trend": "Nostalgic Kuwaiti dishes",
                    "growth": "+32% engagement",
                    "popular_hashtags": ["#KuwaitiCuisine", "#TraditionalFood", "#Q8Heritage"],
                    "opportunity": "Feature traditional dishes with modern presentation"
                }
            ],
            "content_recommendations": [
                "Short-form video content (15-30 seconds)",
                "Behind-the-scenes kitchen content",
                "User-generated content campaigns",
                "Influencer collaborations with micro-influencers (10K-50K followers)"
            ],
            "seasonal_opportunities": {
                "upcoming": "Back-to-school season - family meal deals",
                "current": "Summer promotions - refreshing beverages and light meals"
            }
        }
        
        return json.dumps(trends, indent=2)
        
    except Exception as e:
        logger.error(f"Error in trend analysis: {str(e)}")
        return f"Error analyzing trends: {str(e)}"


def area_demographics_func(area_name: str) -> str:
    """
    Provides demographic insights for specific areas in Kuwait.
    """
    try:
        # Kuwait area demographics (simulated data)
        demographics = {
            "Salmiya": {
                "population_density": "High",
                "primary_demographics": ["Young professionals", "Families", "Expats"],
                "average_income": "Medium-High",
                "food_preferences": ["International cuisine", "Fast casual", "Delivery-friendly"],
                "peak_dining_times": ["1:00 PM - 2:30 PM", "7:30 PM - 10:00 PM"],
                "popular_cuisines": ["Lebanese", "Indian", "American", "Japanese"]
            },
            "Kuwait City": {
                "population_density": "Very High",
                "primary_demographics": ["Business professionals", "Tourists", "Government employees"],
                "average_income": "High",
                "food_preferences": ["Premium dining", "Business lunch", "Coffee shops"],
                "peak_dining_times": ["12:00 PM - 2:00 PM", "8:00 PM - 11:00 PM"],
                "popular_cuisines": ["International", "Kuwaiti traditional", "Italian", "Seafood"]
            },
            "Hawally": {
                "population_density": "Very High",
                "primary_demographics": ["Students", "Young families", "Budget-conscious diners"],
                "average_income": "Medium",
                "food_preferences": ["Affordable options", "Fast food", "Shawarma & grills"],
                "peak_dining_times": ["12:30 PM - 2:00 PM", "6:00 PM - 9:00 PM"],
                "popular_cuisines": ["Arabic", "Indian", "Filipino", "Egyptian"]
            }
        }
        
        area_info = demographics.get(area_name, {
            "population_density": "Medium",
            "primary_demographics": ["Mixed residential"],
            "average_income": "Medium",
            "food_preferences": ["Variety of cuisines"],
            "peak_dining_times": ["1:00 PM - 2:00 PM", "7:00 PM - 9:00 PM"],
            "popular_cuisines": ["Mixed international"]
        })
        
        result = {
            "area": area_name,
            "demographics": area_info,
            "marketing_recommendations": [
                f"Target {area_info['primary_demographics'][0]} with specialized offers",
                f"Peak promotion times: {area_info['peak_dining_times'][0]}",
                f"Focus on {area_info['food_preferences'][0]} menu items"
            ]
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error in area demographics: {str(e)}")
        return f"Error analyzing area demographics: {str(e)}"


# Create Tool instances using LangChain's Tool.from_function
competitor_analysis_tool = Tool.from_function(
    func=competitor_analysis_func,
    name="Competitor Analysis",
    description="Analyzes competitor restaurants in Kuwait for social media strategies and performance. Input should be a query like 'Analyze burger restaurants in Salmiya'"
)

trend_analysis_tool = Tool.from_function(
    func=trend_analysis_func,
    name="Trend Analysis",
    description="Analyzes current food trends in Kuwait social media. Input should be a topic like 'healthy eating trends Kuwait'"
)

area_demographics_tool = Tool.from_function(
    func=area_demographics_func,
    name="Area Demographics",
    description="Provides demographic insights for specific areas in Kuwait. Input should be area name like 'Salmiya', 'Kuwait City', or 'Hawally'"
)

# Export all tools
RESEARCH_TOOLS = [
    competitor_analysis_tool,
    trend_analysis_tool,
    area_demographics_tool
]