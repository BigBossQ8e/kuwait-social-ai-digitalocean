"""
Analytics Tools for Kuwait F&B Performance Tracking
"""

from crewai.tools import tool
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta
import random

@tool("Engagement Analyzer")
def engagement_analyzer_tool(platform: str, post_ids: Optional[List[str]] = None, time_period: int = 7) -> str:
    """Analyze engagement patterns and performance metrics for Kuwait F&B content"""
    post_ids = post_ids or []
        
    
    # Mock analytics data (in production, fetch from platform APIs)
    analytics = {
            "platform": platform,
            "period": f"Last {time_period} days",
            "total_posts": len(post_ids) if post_ids else 15,
            "metrics": {
                "total_reach": random.randint(10000, 50000),
                "total_impressions": random.randint(15000, 75000),
                "total_engagement": random.randint(1000, 5000),
                "avg_engagement_rate": round(random.uniform(3.5, 7.5), 2),
                "follower_growth": random.randint(50, 500),
                "follower_growth_rate": round(random.uniform(1.5, 5.0), 2)
            },
            "top_performing_content": [],
            "content_type_performance": {},
            "optimal_posting_times": [],
            "audience_insights": {}
        }
    
    # Generate top performing posts
    content_types = ["food_photo", "reel", "carousel", "story", "offer_post"]
    for i in range(5):
        analytics["top_performing_content"].append({
                "post_id": f"post_{i+1}",
                "type": random.choice(content_types),
                "engagement_rate": round(random.uniform(5, 12), 2),
                "reach": random.randint(2000, 10000),
                "likes": random.randint(100, 1000),
                "comments": random.randint(10, 100),
                "shares": random.randint(5, 50),
                "saves": random.randint(20, 200),
                "content_theme": random.choice(["new_dish", "offer", "behind_scenes", "customer_review"])
            })
    
    # Content type performance
    for content_type in content_types:
        analytics["content_type_performance"][content_type] = {
                "avg_engagement": round(random.uniform(3, 8), 2),
                "best_time": random.choice(["12:00 PM", "7:00 PM", "9:00 PM"]),
                "frequency": random.randint(1, 5),
                "recommendation": _get_content_recommendation(content_type)
            }
    
    # Optimal posting times based on engagement
    analytics["optimal_posting_times"] = [
            {"time": "12:30 PM", "day": "Sunday", "engagement_index": 92},
            {"time": "7:00 PM", "day": "Tuesday", "engagement_index": 88},
            {"time": "8:30 PM", "day": "Thursday", "engagement_index": 95},
            {"time": "9:00 PM", "day": "Friday", "engagement_index": 97},
            {"time": "2:00 PM", "day": "Saturday", "engagement_index": 85}
        ]
    
    # Audience insights
    analytics["audience_insights"] = {
            "demographics": {
                "age_groups": {
                    "18-24": "15%",
                    "25-34": "35%",
                    "35-44": "30%",
                    "45+": "20%"
                },
                "gender": {
                    "male": "45%",
                    "female": "55%"
                },
                "top_locations": [
                    "Salmiya (18%)",
                    "Kuwait City (15%)",
                    "Hawally (12%)",
                    "Farwaniya (10%)"
                ]
            },
            "behavior": {
                "most_active_times": ["12-2 PM", "7-10 PM"],
                "preferred_content": ["Food photos", "Offers", "Reels"],
                "avg_session_duration": "3.5 minutes"
            }
        }
    
    # Generate insights and recommendations
    analytics["insights"] = _generate_insights(analytics)
    analytics["recommendations"] = _generate_recommendations(analytics)
    
    return json.dumps(analytics, indent=2)
    
def _get_content_recommendation(content_type: str) -> str:
    """Get content-specific recommendations"""
    recommendations = {
            "food_photo": "Use natural lighting and close-up shots for better engagement",
            "reel": "Keep under 30 seconds with trending audio for maximum reach",
            "carousel": "Use 5-7 slides with a strong hook on first slide",
            "story": "Add polls and questions for interaction",
            "offer_post": "Create urgency with time limits and clear CTAs"
    }
    return recommendations.get(content_type, "Focus on quality and consistency")
    
def _generate_insights(data: Dict) -> List[str]:
    """Generate insights from analytics data"""
    insights = []
    
    # Engagement insights
    if data["metrics"]["avg_engagement_rate"] > 5:
        insights.append("Your engagement rate is above Kuwait F&B industry average (5%)")
    else:
        insights.append("Focus on increasing engagement through interactive content")
    
    # Content type insights
    top_content = max(data["content_type_performance"].items(), 
                     key=lambda x: x[1]["avg_engagement"])
    insights.append(f"{top_content[0].replace('_', ' ').title()} generates highest engagement")
    
    # Timing insights
    insights.append("Thursday and Friday evenings show highest engagement")
    
    # Audience insights
    insights.append("Your primary audience is 25-34 year olds in Salmiya and Kuwait City")
    
    return insights
    
def _generate_recommendations(data: Dict) -> List[Dict]:
    """Generate actionable recommendations"""
    recommendations = [
            {
                "priority": "high",
                "action": "Increase Reel content to 3-4 per week",
                "expected_impact": "+25% reach",
                "reason": "Reels showing 3x higher reach than static posts"
            },
            {
                "priority": "high",
                "action": "Post during 7-9 PM on weekdays",
                "expected_impact": "+15% engagement",
                "reason": "Peak audience activity detected"
            },
            {
                "priority": "medium",
                "action": "Add Arabic captions to all content",
                "expected_impact": "+20% local engagement",
                "reason": "55% of audience prefers bilingual content"
            },
            {
                "priority": "medium",
                "action": "Feature customer testimonials weekly",
                "expected_impact": "+30% trust score",
                "reason": "UGC content shows 2x higher saves"
            }
    ]
    
    return recommendations

@tool("Order Attribution")
def order_attribution_tool(time_period: int, platform: Optional[str] = None) -> str:
    """Analyze which social media posts and campaigns drive actual food orders in Kuwait"""
    
    # Mock order attribution data
    attribution_data = {
            "analysis_period": f"Last {time_period} days",
            "total_social_attributed_orders": random.randint(500, 2000),
            "total_order_value": f"{random.randint(5000, 20000)} KWD",
            "attribution_by_platform": {},
            "top_converting_posts": [],
            "campaign_performance": [],
            "customer_journey_insights": {}
        }
    
    # Platform attribution
    platforms = ["instagram", "tiktok", "twitter", "facebook"]
    if platform:
        platforms = [platform]
    
    total_orders = attribution_data["total_social_attributed_orders"]
    remaining_orders = total_orders
    
    for i, plat in enumerate(platforms):
        if i == len(platforms) - 1:
            orders = remaining_orders
        else:
            orders = random.randint(int(remaining_orders * 0.2), int(remaining_orders * 0.5))
            remaining_orders -= orders
        
        attribution_data["attribution_by_platform"][plat] = {
                "orders": orders,
                "conversion_rate": round(random.uniform(1.5, 4.5), 2),
                "avg_order_value": f"{random.randint(8, 15)} KWD",
                "best_content_type": random.choice(["offer_posts", "food_reels", "menu_highlights"]),
                "peak_conversion_time": random.choice(["lunch_hours", "dinner_time", "late_night"])
            }
    
    # Top converting posts
    post_types = [
        {"type": "limited_offer", "theme": "Weekend Special"},
        {"type": "new_item_launch", "theme": "Truffle Burger Launch"},
        {"type": "combo_deal", "theme": "Family Feast"},
        {"type": "flash_sale", "theme": "2-Hour Flash Sale"},
        {"type": "loyalty_program", "theme": "Points Reward"}
    ]
    
    for i in range(5):
        post = random.choice(post_types)
        attribution_data["top_converting_posts"].append({
                "post_id": f"converting_post_{i+1}",
                "type": post["type"],
                "theme": post["theme"],
                "direct_orders": random.randint(20, 100),
                "influenced_orders": random.randint(50, 200),
                "revenue_generated": f"{random.randint(200, 1000)} KWD",
                "conversion_rate": f"{round(random.uniform(2, 6), 2)}%",
                "key_success_factors": _get_success_factors(post["type"])
            })
    
    # Campaign performance
    campaigns = [
        "Ramadan Special Menu",
        "Summer Cooling Treats",
        "Weekend Family Deals",
        "Lunch Hour Express"
    ]
    
    for campaign in campaigns:
        attribution_data["campaign_performance"].append({
                "campaign_name": campaign,
                "duration": f"{random.randint(7, 30)} days",
                "total_orders": random.randint(100, 500),
                "roi": f"{random.randint(150, 400)}%",
                "best_performing_element": random.choice([
                    "Time-limited offers",
                    "Bundle pricing",
                    "Free delivery",
                    "Exclusive items"
                ])
            })
    
    # Customer journey insights
    attribution_data["customer_journey_insights"] = {
            "avg_touchpoints_before_order": random.randint(3, 6),
            "common_paths": [
                "Instagram Story → Profile → Order (35%)",
                "TikTok Video → Instagram → Order (25%)",
                "Instagram Post → Saved → Order Later (20%)",
                "Friend Share → Profile Visit → Order (20%)"
            ],
            "time_to_conversion": {
                "immediate": "25%",
                "within_1_hour": "35%",
                "within_24_hours": "25%",
                "over_24_hours": "15%"
            },
            "repeat_order_trigger": "New item announcements and exclusive offers"
        }
    
    # Add insights and recommendations
    attribution_data["key_insights"] = _generate_attribution_insights(attribution_data)
    attribution_data["optimization_recommendations"] = _generate_attribution_recommendations(attribution_data)
    
    return json.dumps(attribution_data, indent=2)
    
def _get_success_factors(post_type: str) -> List[str]:
    """Get success factors for different post types"""
    factors = {
            "limited_offer": ["Urgency messaging", "Clear time limit", "Exclusive pricing"],
            "new_item_launch": ["High-quality visuals", "Ingredient focus", "Launch day buzz"],
            "combo_deal": ["Value proposition", "Family appeal", "Easy ordering"],
            "flash_sale": ["Push notifications", "Story countdown", "Limited quantity"],
            "loyalty_program": ["Points visualization", "Reward tiers", "Easy redemption"]
    }
    return factors.get(post_type, ["Engaging content", "Clear CTA", "Mobile-optimized"])
    
def _generate_attribution_insights(data: Dict) -> List[str]:
    """Generate attribution insights"""
    insights = []
    
    # Platform insights
    top_platform = max(data["attribution_by_platform"].items(), 
                      key=lambda x: x[1]["orders"])
    insights.append(f"{top_platform[0].title()} drives {top_platform[1]['orders']} orders ({round(top_platform[1]['orders']/data['total_social_attributed_orders']*100)}% of total)")
    
    # Content insights
    insights.append("Limited-time offers show 3x higher conversion than regular posts")
    
    # Timing insights
    insights.append("Lunch hour posts (11:30 AM - 1:30 PM) generate immediate orders")
    
    # Journey insights
    insights.append("60% of orders happen within 1 hour of seeing social content")
    
    return insights
    
def _generate_attribution_recommendations(data: Dict) -> List[Dict]:
    """Generate recommendations for improving attribution"""
    return [
            {
                "area": "Content Strategy",
                "recommendation": "Increase limited-time offers to 2-3 per week",
                "expected_impact": "+40% direct orders",
                "implementation": "Use Instagram Stories countdown for urgency"
            },
            {
                "area": "Platform Focus",
                "recommendation": f"Allocate 60% of content budget to {list(data['attribution_by_platform'].keys())[0]}",
                "expected_impact": "+25% ROI",
                "implementation": "Platform showing highest conversion"
            },
            {
                "area": "Timing Optimization",
                "recommendation": "Schedule offer posts 30 minutes before peak meal times",
                "expected_impact": "+35% immediate orders",
                "implementation": "11:30 AM for lunch, 6:30 PM for dinner"
            },
            {
                "area": "Tracking Enhancement",
                "recommendation": "Implement UTM parameters and promo codes for each post",
                "expected_impact": "95% attribution accuracy",
                "implementation": "Unique codes per platform and campaign"
            }
    ]

@tool("A/B Testing")
def ab_testing_tool(test_name: str, variant_a: Dict, variant_b: Dict, sample_size: int = 1000) -> str:
    """Design and analyze A/B tests for Kuwait F&B social media content"""
    
    # Simulate test results
    results = {
            "test_name": test_name,
            "test_duration": "7 days",
            "total_sample_size": sample_size * 2,
            "variants": {
                "A": {
                    "description": variant_a,
                    "sample_size": sample_size,
                    "metrics": _generate_test_metrics(is_winner=random.random() > 0.5)
                },
                "B": {
                    "description": variant_b,
                    "sample_size": sample_size,
                    "metrics": _generate_test_metrics(is_winner=random.random() > 0.5)
                }
            },
            "statistical_significance": {},
            "winner": None,
            "insights": [],
            "recommendations": []
        }
    
    # Determine winner
    a_engagement = results["variants"]["A"]["metrics"]["engagement_rate"]
    b_engagement = results["variants"]["B"]["metrics"]["engagement_rate"]
    
    if abs(a_engagement - b_engagement) > 0.5:
        results["winner"] = "A" if a_engagement > b_engagement else "B"
        results["statistical_significance"] = {
            "confidence_level": "95%",
            "p_value": 0.03,
            "is_significant": True
        }
    else:
        results["statistical_significance"] = {
            "confidence_level": "Not significant",
            "p_value": 0.15,
            "is_significant": False
        }
    
    # Generate insights based on test type
    results["insights"] = _generate_test_insights(test_name, results)
    
    # Generate recommendations
    results["recommendations"] = _generate_test_recommendations(results)
    
    # Add Kuwait-specific insights
    results["kuwait_specific_findings"] = _get_kuwait_findings(test_name)
    
    return json.dumps(results, indent=2)
    
def _generate_test_metrics(is_winner: bool) -> Dict:
    """Generate test metrics with some variance"""
    base_engagement = 5.5 if is_winner else 4.5
    
    return {
            "impressions": random.randint(8000, 12000),
            "reach": random.randint(5000, 8000),
            "engagement_rate": round(base_engagement + random.uniform(-0.5, 0.5), 2),
            "click_through_rate": round(random.uniform(1.5, 3.5), 2),
            "conversion_rate": round(random.uniform(0.5, 2.5), 2),
            "saves": random.randint(50, 200),
            "shares": random.randint(20, 100),
            "comments": random.randint(10, 50),
            "order_attribution": random.randint(5, 30)
    }
    
def _generate_test_insights(test_name: str, results: Dict) -> List[str]:
    """Generate insights based on test results"""
    insights = []
    
    test_insights = {
            "caption_language": [
                "Bilingual captions (Arabic + English) outperform English-only by 35%",
                "Starting with Arabic greeting increases local engagement",
                "Emoji usage resonates well with Kuwait audience"
            ],
            "posting_time": [
                "Evening posts (7-9 PM) show 40% higher engagement",
                "Lunch hour posts drive immediate orders",
                "Weekend mornings underperform weekday evenings"
            ],
            "content_type": [
                "Video content generates 2.5x more engagement than static posts",
                "Behind-the-scenes content builds trust with Kuwait audience",
                "User testimonials in Arabic perform exceptionally well"
            ],
            "offer_format": [
                "Time-limited offers create urgency and drive conversions",
                "Family meal deals resonate strongly with Kuwait market",
                "Free delivery messaging increases order rates by 25%"
            ]
    }
    
    # Get relevant insights
    for key in test_insights:
        if key in test_name.lower():
            insights.extend(test_insights[key][:2])
            break
    else:
        insights.append("Clear winner identified with statistical significance")
        insights.append("Consider running follow-up tests to confirm findings")
    
    return insights
    
def _generate_test_recommendations(results: Dict) -> List[Dict]:
    """Generate recommendations based on test results"""
    recommendations = []
    
    if results["winner"]:
        winning_variant = results["variants"][results["winner"]]
        recommendations.append({
            "action": f"Implement {results['winner']} variant across all content",
            "priority": "high",
            "expected_impact": f"+{winning_variant['metrics']['engagement_rate']-4}% engagement",
            "timeline": "Immediate"
        })
    
    recommendations.extend([
        {
            "action": "Run follow-up test with larger sample size",
            "priority": "medium",
            "expected_impact": "Validate findings with 99% confidence",
            "timeline": "Next 2 weeks"
        },
        {
            "action": "Test variations on different audience segments",
            "priority": "medium",
            "expected_impact": "Personalized content strategy",
            "timeline": "Next month"
        }
    ])
    
    return recommendations
    
def _get_kuwait_findings(test_name: str) -> List[str]:
    """Get Kuwait-specific findings"""
    findings = [
        "Kuwait audiences prefer authentic, local content over generic posts",
        "Religious and cultural sensitivity significantly impacts engagement",
        "Family-oriented messaging resonates across all age groups",
        "Price transparency and value propositions are crucial for Kuwait market",
        "Local area mentions (Salmiya, Hawally) increase relevance"
    ]
    
    return random.sample(findings, 3)


# Create tool instances for backward compatibility
EngagementAnalyzerTool = engagement_analyzer_tool
OrderAttributionTool = order_attribution_tool
ABTestingTool = ab_testing_tool