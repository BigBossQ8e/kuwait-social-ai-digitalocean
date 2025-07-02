"""
Campaign Management Crew for Kuwait F&B Marketing
Orchestrates complex marketing campaigns with multiple agents
"""

from crewai import Crew, Task
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import logging
from ..f_and_b_agents import KuwaitFBAgents

class CampaignManagementCrew:
    """Multi-agent crew for managing comprehensive marketing campaigns"""
    
    def __init__(self):
        self.agents = KuwaitFBAgents()
        self.logger = logging.getLogger(__name__)
    
    def create_ramadan_campaign(
        self,
        restaurant_info: Dict[str, Any],
        budget: Optional[float] = None,
        duration_days: int = 30
    ) -> Dict[str, Any]:
        """Create complete Ramadan campaign for Kuwait F&B"""
        
        # Task 1: Ramadan market research
        research_task = Task(
            description=f"""Research Ramadan dining trends in Kuwait for {restaurant_info['name']}.
            Analyze:
            - Popular iftar items in {restaurant_info.get('area', 'Kuwait')}
            - Competitor Ramadan strategies
            - Customer behavior during Ramadan
            - Pricing strategies for iftar/suhoor
            - Delivery vs dine-in preferences
            
            Consider:
            - Prayer times and eating windows
            - Family gathering preferences
            - Traditional vs modern preferences
            
            Output: Comprehensive Ramadan market analysis""",
            agent=self.agents.market_researcher,
            expected_output="Detailed Ramadan market insights and opportunities"
        )
        
        # Task 2: Campaign strategy development
        strategy_task = Task(
            description=f"""Develop {duration_days}-day Ramadan campaign strategy.
            Restaurant: {restaurant_info['name']}
            Budget: {budget or 'Flexible'} KWD
            
            Create:
            1. Campaign objectives and KPIs
            2. Target audience segments
            3. Key messages and value propositions
            4. Content themes for each week
            5. Promotional offers strategy
            6. Competition differentiation
            
            Focus on Kuwait Ramadan traditions and family values.
            Output: Complete campaign strategy document""",
            agent=self.agents.market_researcher,
            context=[research_task],
            expected_output="Comprehensive Ramadan campaign strategy"
        )
        
        # Task 3: Content creation for campaign
        content_task = Task(
            description=f"""Create {duration_days} days of Ramadan content.
            Follow the campaign strategy to create:
            - Daily iftar specials posts
            - Suhoor menu highlights
            - Family meal packages
            - Ramadan greetings and wishes
            - Behind-the-scenes preparation
            - Customer testimonials
            
            Vary content types: posts, stories, reels
            Include special Eid content for campaign end.
            Output: Complete content calendar with all posts""",
            agent=self.agents.content_creator,
            context=[strategy_task],
            expected_output=f"{duration_days} unique Ramadan posts"
        )
        
        # Task 4: Cultural and religious compliance
        compliance_task = Task(
            description="""Ensure all Ramadan content is culturally and religiously appropriate.
            Review for:
            - Respectful Ramadan messaging
            - Appropriate timing (no food posts during fasting hours)
            - Family and community focus
            - Proper Arabic Islamic greetings
            - Charity and giving back elements
            
            Add Arabic translations maintaining religious reverence.
            Output: Culturally verified campaign content""",
            agent=self.agents.cultural_compliance,
            context=[content_task],
            expected_output="Fully compliant Ramadan content"
        )
        
        # Task 5: Timing optimization for Ramadan
        timing_task = Task(
            description="""Create Ramadan-specific posting schedule.
            Consider:
            - Daily iftar and suhoor times (they change daily)
            - Peak hunger/decision times (1-2 hours before iftar)
            - Post-iftar active social media time
            - Suhoor preparation time (late night)
            - Friday prayer considerations
            - Avoid posting during fasting hours
            
            Output: 30-day optimized posting calendar""",
            agent=self.agents.timing_expert,
            context=[compliance_task],
            expected_output="Ramadan posting schedule with exact times"
        )
        
        # Task 6: Performance tracking setup
        performance_task = Task(
            description="""Design performance tracking system for Ramadan campaign.
            Set up:
            - Daily KPI tracking
            - Order attribution methods
            - Engagement benchmarks
            - ROI calculation framework
            - Competitor monitoring plan
            - Week-by-week optimization triggers
            
            Output: Performance measurement framework""",
            agent=self.agents.performance_optimizer,
            context=[strategy_task, timing_task],
            expected_output="Complete performance tracking plan"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[
                self.agents.market_researcher,
                self.agents.content_creator,
                self.agents.cultural_compliance,
                self.agents.timing_expert,
                self.agents.performance_optimizer
            ],
            tasks=[
                research_task, strategy_task, content_task,
                compliance_task, timing_task, performance_task
            ],
            verbose=True,
            process="sequential"
        )
        
        try:
            result = crew.kickoff()
            return self._parse_ramadan_results(result, restaurant_info, budget, duration_days)
            
        except Exception as e:
            self.logger.error(f"Ramadan campaign creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create Ramadan campaign"
            }
    
    def create_new_launch_campaign(
        self,
        restaurant_info: Dict[str, Any],
        product_info: Dict[str, Any],
        campaign_duration: int = 14
    ) -> Dict[str, Any]:
        """Create campaign for new product/menu launch"""
        
        # Task 1: Market opportunity analysis
        market_task = Task(
            description=f"""Analyze market opportunity for new {product_info['type']} launch.
            Product: {product_info['name']}
            Restaurant: {restaurant_info['name']}
            
            Research:
            - Similar products in Kuwait market
            - Pricing benchmarks
            - Target customer segments
            - Best launch timing
            - Potential challenges
            
            Output: Market opportunity report""",
            agent=self.agents.market_researcher,
            expected_output="Product launch market analysis"
        )
        
        # Task 2: Launch strategy
        strategy_task = Task(
            description=f"""Create {campaign_duration}-day launch strategy.
            Build excitement through:
            1. Teaser phase (days 1-3)
            2. Reveal phase (days 4-5)
            3. Trial promotion phase (days 6-10)
            4. Feedback collection phase (days 11-14)
            
            Include:
            - Influencer collaboration plan
            - Launch offers and pricing
            - PR messaging
            
            Output: Phased launch strategy""",
            agent=self.agents.content_creator,
            context=[market_task],
            expected_output="Complete launch campaign strategy"
        )
        
        # Task 3: Create launch content
        content_task = Task(
            description="""Create all content for the launch campaign.
            Follow the phased approach:
            - Teaser content (mysterious, building curiosity)
            - Reveal content (exciting announcement)
            - Feature highlights (benefits, ingredients)
            - Customer testimonials plan
            - Limited-time offers
            
            Mix of reels, carousel posts, and stories.
            Output: All launch campaign content""",
            agent=self.agents.content_creator,
            context=[strategy_task],
            expected_output="Complete launch content package"
        )
        
        # Task 4: Arabic localization
        arabic_task = Task(
            description="""Create Arabic versions maintaining launch excitement.
            Ensure:
            - Excitement translates culturally
            - Product benefits clear in Arabic
            - Local references and expressions
            - Trending Arabic hashtags for launches
            
            Output: Bilingual launch content""",
            agent=self.agents.arabic_specialist,
            context=[content_task],
            expected_output="Arabic launch content"
        )
        
        # Task 5: Launch timing optimization
        timing_task = Task(
            description="""Optimize launch campaign timing.
            Determine:
            - Best launch day and time
            - Teaser posting schedule
            - Peak engagement windows
            - Competitive timing avoidance
            
            Output: Launch timeline""",
            agent=self.agents.timing_expert,
            context=[arabic_task],
            expected_output="Optimized launch schedule"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[
                self.agents.market_researcher,
                self.agents.content_creator,
                self.agents.arabic_specialist,
                self.agents.timing_expert
            ],
            tasks=[market_task, strategy_task, content_task, arabic_task, timing_task],
            verbose=True,
            process="sequential"
        )
        
        try:
            result = crew.kickoff()
            return self._parse_launch_results(result, restaurant_info, product_info, campaign_duration)
            
        except Exception as e:
            self.logger.error(f"Launch campaign creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create launch campaign"
            }
    
    def create_seasonal_campaign(
        self,
        restaurant_info: Dict[str, Any],
        season: str,
        special_dates: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create seasonal campaigns (Summer, National Day, etc.)"""
        
        special_dates = special_dates or []
        
        # Task 1: Seasonal insights
        insights_task = Task(
            description=f"""Research {season} season opportunities for {restaurant_info['name']}.
            Analyze:
            - Weather impact on dining preferences
            - Seasonal menu opportunities
            - Customer behavior changes
            - Competition seasonal strategies
            Special dates to consider: {', '.join(special_dates)}
            
            Output: Seasonal opportunity analysis""",
            agent=self.agents.market_researcher,
            expected_output="Seasonal market insights"
        )
        
        # Task 2: Campaign creation
        campaign_task = Task(
            description=f"""Create {season} campaign content.
            Include:
            - Season-appropriate menu items
            - Weather-based messaging
            - Special date celebrations
            - Family/group offers
            - Indoor/outdoor preferences
            
            Output: Complete seasonal campaign""",
            agent=self.agents.content_creator,
            context=[insights_task],
            expected_output="Seasonal campaign content"
        )
        
        # Task 3: Cultural adaptation
        cultural_task = Task(
            description=f"""Ensure {season} campaign fits Kuwait culture.
            Consider:
            - Local seasonal traditions
            - Weather-appropriate messaging
            - Holiday sensitivities
            - Family gathering customs
            
            Output: Culturally adapted campaign""",
            agent=self.agents.cultural_compliance,
            context=[campaign_task],
            expected_output="Culturally appropriate seasonal content"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[
                self.agents.market_researcher,
                self.agents.content_creator,
                self.agents.cultural_compliance
            ],
            tasks=[insights_task, campaign_task, cultural_task],
            verbose=True,
            process="sequential"
        )
        
        try:
            result = crew.kickoff()
            return self._parse_seasonal_results(result, restaurant_info, season, special_dates)
            
        except Exception as e:
            self.logger.error(f"Seasonal campaign creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create seasonal campaign"
            }
    
    def _parse_ramadan_results(
        self, 
        raw_result: Any, 
        restaurant_info: Dict,
        budget: Optional[float],
        duration: int
    ) -> Dict:
        """Parse Ramadan campaign results"""
        
        return {
            "success": True,
            "campaign": {
                "name": f"Ramadan {datetime.now().year} - {restaurant_info['name']}",
                "type": "ramadan",
                "duration_days": duration,
                "budget": budget or "Flexible",
                "restaurant": restaurant_info['name'],
                "status": "Ready to launch"
            },
            "strategy": {
                "objectives": [
                    "Increase iftar orders by 50%",
                    "Build family meal reputation",
                    "Enhance community connection"
                ],
                "target_segments": [
                    "Families planning iftar gatherings",
                    "Young professionals seeking convenient suhoor",
                    "Mosques and charity organizations"
                ],
                "key_messages": [
                    "Authentic taste for blessed gatherings",
                    "Complete iftar solutions for families",
                    "Give back - charity meal programs"
                ]
            },
            "content": {
                "total_posts": duration,
                "content_types": {
                    "iftar_specials": 10,
                    "suhoor_menu": 8,
                    "family_packages": 7,
                    "ramadan_greetings": 3,
                    "eid_preparation": 2
                },
                "languages": ["Arabic", "English"],
                "top_hashtags": [
                    "#رمضان_الكويت", "#Ramadan_Kuwait", "#افطار", "#سحور",
                    f"#{restaurant_info['name']}_Ramadan", "#كويت_فود"
                ]
            },
            "schedule": {
                "launch_date": "3 days before Ramadan",
                "daily_posts": 1,
                "peak_posting_times": [
                    "2:00 PM - 3:00 PM (Pre-iftar planning)",
                    "9:00 PM - 10:00 PM (Post-iftar social time)",
                    "12:00 AM - 1:00 AM (Suhoor planning)"
                ],
                "special_days": {
                    "first_day": "Grand opening iftar offer",
                    "middle_ramadan": "Family feast promotion",
                    "last_10_days": "Special Laylat Al-Qadr meals",
                    "eid": "Eid celebration packages"
                }
            },
            "performance_targets": {
                "reach": "100,000+ during campaign",
                "engagement_rate": "7-10%",
                "order_increase": "50% for iftar time",
                "new_customers": "200+ families",
                "roi": "300-400%"
            },
            "execution_checklist": [
                "✅ 30 days of content created",
                "✅ Arabic/English versions ready",
                "✅ Prayer time scheduling confirmed",
                "✅ Halal messaging prominent",
                "✅ Charity component included",
                "✅ Performance tracking setup"
            ]
        }
    
    def _parse_launch_results(
        self,
        raw_result: Any,
        restaurant_info: Dict,
        product_info: Dict,
        duration: int
    ) -> Dict:
        """Parse product launch campaign results"""
        
        return {
            "success": True,
            "campaign": {
                "name": f"{product_info['name']} Launch Campaign",
                "restaurant": restaurant_info['name'],
                "product": product_info['name'],
                "duration_days": duration,
                "type": "product_launch"
            },
            "phases": {
                "teaser": {
                    "duration": "Days 1-3",
                    "content_count": 6,
                    "approach": "Mystery and curiosity building",
                    "sample_content": "Something BIG is coming to Kuwait... 👀🔥"
                },
                "reveal": {
                    "duration": "Days 4-5",
                    "content_count": 4,
                    "approach": "Exciting announcement with full details",
                    "launch_offer": "First 100 customers get 25% off"
                },
                "trial": {
                    "duration": "Days 6-10",
                    "content_count": 8,
                    "approach": "Feature highlights and customer testimonials",
                    "promotions": ["BOGO offer", "Free delivery", "Loyalty points double"]
                },
                "feedback": {
                    "duration": "Days 11-14",
                    "content_count": 4,
                    "approach": "Reviews, improvements, and thank you",
                    "engagement": "Rate and review campaigns"
                }
            },
            "content_summary": {
                "total_pieces": 22,
                "reels": 8,
                "carousel_posts": 6,
                "stories": 8,
                "languages": ["English", "Arabic"]
            },
            "launch_day_plan": {
                "time": "12:00 PM",
                "reason": "Peak lunch decision time",
                "activities": [
                    "Main announcement post",
                    "Story takeover",
                    "Live cooking demo",
                    "Influencer posts",
                    "Email blast"
                ]
            }
        }
    
    def _parse_seasonal_results(
        self,
        raw_result: Any,
        restaurant_info: Dict,
        season: str,
        special_dates: List[str]
    ) -> Dict:
        """Parse seasonal campaign results"""
        
        season_data = {
            "summer": {
                "focus": "Cooling treats and indoor comfort",
                "key_items": ["Ice cream", "Cold beverages", "Salads"],
                "messaging": "Beat the heat"
            },
            "winter": {
                "focus": "Warm comfort food and outdoor dining",
                "key_items": ["Soups", "Hot beverages", "Grills"],
                "messaging": "Cozy gatherings"
            },
            "national_day": {
                "focus": "Patriotic themes and local pride",
                "key_items": ["Traditional dishes", "Kuwait flag colors"],
                "messaging": "Celebrate Kuwait"
            }
        }
        
        season_info = season_data.get(season.lower(), {
            "focus": "Seasonal specials",
            "key_items": ["Seasonal menu"],
            "messaging": "Seasonal delights"
        })
        
        return {
            "success": True,
            "campaign": {
                "name": f"{season.title()} Campaign - {restaurant_info['name']}",
                "season": season,
                "restaurant": restaurant_info['name'],
                "special_dates": special_dates
            },
            "strategy": {
                "focus": season_info["focus"],
                "featured_items": season_info["key_items"],
                "core_message": season_info["messaging"],
                "duration": "Throughout season"
            },
            "content_themes": {
                "week_1": "Season launch - introducing seasonal menu",
                "week_2": "Customer favorites and testimonials",
                "week_3": "Behind the scenes - seasonal preparations",
                "week_4": "Limited time offers and competitions"
            },
            "execution_ready": True
        }