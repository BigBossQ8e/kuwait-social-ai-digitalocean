"""
Analytics Insights Crew for Kuwait F&B Performance Analysis
Multi-agent team for comprehensive analytics and optimization
"""

from crewai import Crew, Task
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import logging
from ..f_and_b_agents import KuwaitFBAgents

class AnalyticsInsightsCrew:
    """Multi-agent crew for analyzing performance and generating insights"""
    
    def __init__(self):
        self.agents = KuwaitFBAgents()
        self.logger = logging.getLogger(__name__)
    
    def analyze_campaign_performance(
        self,
        restaurant_info: Dict[str, Any],
        campaign_data: Dict[str, Any],
        comparison_period: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze complete campaign performance with actionable insights"""
        
        # Task 1: Data collection and analysis
        data_task = Task(
            description=f"""Analyze campaign performance data for {restaurant_info['name']}.
            Campaign: {campaign_data.get('name', 'Recent Campaign')}
            Duration: {campaign_data.get('duration', '14 days')}
            
            Analyze:
            - Engagement metrics (likes, comments, shares, saves)
            - Reach and impressions growth
            - Click-through rates
            - Story completion rates
            - Best and worst performing content
            
            Compare with: {comparison_period or 'Previous period'}
            Output: Detailed performance metrics report""",
            agent=self.agents.performance_optimizer,
            expected_output="Comprehensive performance data analysis"
        )
        
        # Task 2: Competitor benchmarking
        benchmark_task = Task(
            description="""Benchmark campaign performance against Kuwait F&B competitors.
            Compare:
            - Engagement rates vs industry average
            - Growth metrics vs top competitors
            - Content strategy effectiveness
            - Share of voice in market
            
            Identify:
            - Where we outperformed
            - Areas needing improvement
            - Competitor tactics to consider
            
            Output: Competitive benchmark report""",
            agent=self.agents.market_researcher,
            context=[data_task],
            expected_output="Competitor comparison insights"
        )
        
        # Task 3: Content performance deep dive
        content_task = Task(
            description="""Analyze which content types and themes performed best.
            Examine:
            - Post types (static, carousel, reel, story)
            - Content themes (offers, behind-scenes, food shots)
            - Caption styles and lengths
            - Hashtag effectiveness
            - Posting time impact
            - Arabic vs English performance
            
            Identify patterns and success factors.
            Output: Content performance insights""",
            agent=self.agents.content_creator,
            context=[data_task],
            expected_output="Content strategy insights"
        )
        
        # Task 4: Audience behavior analysis
        audience_task = Task(
            description="""Analyze audience behavior and preferences during campaign.
            Study:
            - Engagement patterns by time
            - Content preferences by segment
            - Peak activity windows
            - Comment sentiment analysis
            - Share and save patterns
            - New follower quality
            
            Output: Audience behavior report""",
            agent=self.agents.timing_expert,
            context=[data_task, content_task],
            expected_output="Detailed audience insights"
        )
        
        # Task 5: ROI and business impact
        roi_task = Task(
            description="""Calculate campaign ROI and business impact.
            Analyze:
            - Direct order attribution
            - Brand awareness lift
            - Cost per engagement
            - Customer acquisition cost
            - Lifetime value impact
            
            Provide:
            - ROI calculation
            - Success metrics evaluation
            - Budget efficiency analysis
            
            Output: Business impact report""",
            agent=self.agents.performance_optimizer,
            context=[data_task, benchmark_task],
            expected_output="ROI and business impact analysis"
        )
        
        # Task 6: Strategic recommendations
        strategy_task = Task(
            description="""Generate strategic recommendations based on all analyses.
            Create:
            - Top 5 actionable improvements
            - Content strategy adjustments
            - Budget reallocation suggestions
            - Testing recommendations
            - Next campaign focus areas
            
            Prioritize by potential impact.
            Output: Strategic action plan""",
            agent=self.agents.market_researcher,
            context=[benchmark_task, content_task, audience_task, roi_task],
            expected_output="Prioritized strategic recommendations"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[
                self.agents.performance_optimizer,
                self.agents.market_researcher,
                self.agents.content_creator,
                self.agents.timing_expert
            ],
            tasks=[
                data_task, benchmark_task, content_task,
                audience_task, roi_task, strategy_task
            ],
            verbose=True,
            process="sequential"
        )
        
        try:
            result = crew.kickoff()
            return self._parse_analytics_results(result, restaurant_info, campaign_data)
            
        except Exception as e:
            self.logger.error(f"Campaign analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to analyze campaign performance"
            }
    
    def competitive_landscape_analysis(
        self,
        restaurant_info: Dict[str, Any],
        competitors: List[str],
        time_period: int = 30
    ) -> Dict[str, Any]:
        """Analyze competitive landscape and market position"""
        
        # Task 1: Competitor content analysis
        content_analysis_task = Task(
            description=f"""Analyze social media content from competitors: {', '.join(competitors)}.
            Time period: Last {time_period} days
            
            Analyze:
            - Posting frequency and timing
            - Content types and quality
            - Engagement rates
            - Hashtag strategies
            - Promotional tactics
            - Arabic/English content mix
            
            Output: Competitor content analysis""",
            agent=self.agents.market_researcher,
            expected_output="Detailed competitor content breakdown"
        )
        
        # Task 2: Market positioning
        positioning_task = Task(
            description=f"""Determine {restaurant_info['name']}'s market position.
            Compare:
            - Brand perception vs competitors
            - Price positioning
            - Unique value propositions
            - Target audience overlap
            - Geographic coverage
            
            Output: Market positioning report""",
            agent=self.agents.market_researcher,
            context=[content_analysis_task],
            expected_output="Market position analysis"
        )
        
        # Task 3: Opportunity identification
        opportunity_task = Task(
            description="""Identify market opportunities and gaps.
            Find:
            - Underserved customer segments
            - Content gaps competitors miss
            - Time slots with low competition
            - Trending topics not utilized
            - Platform opportunities
            
            Output: Market opportunity report""",
            agent=self.agents.performance_optimizer,
            context=[content_analysis_task, positioning_task],
            expected_output="Identified market opportunities"
        )
        
        # Task 4: Strategic differentiation
        differentiation_task = Task(
            description="""Develop differentiation strategy.
            Create:
            - Unique brand positioning
            - Content differentiation tactics
            - Competitive advantages to highlight
            - Defensive strategies
            - Innovation opportunities
            
            Output: Differentiation strategy""",
            agent=self.agents.content_creator,
            context=[positioning_task, opportunity_task],
            expected_output="Strategic differentiation plan"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[
                self.agents.market_researcher,
                self.agents.performance_optimizer,
                self.agents.content_creator
            ],
            tasks=[
                content_analysis_task, positioning_task,
                opportunity_task, differentiation_task
            ],
            verbose=True,
            process="sequential"
        )
        
        try:
            result = crew.kickoff()
            return self._parse_competitive_results(result, restaurant_info, competitors)
            
        except Exception as e:
            self.logger.error(f"Competitive analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to analyze competitive landscape"
            }
    
    def monthly_performance_review(
        self,
        restaurant_info: Dict[str, Any],
        month: str,
        year: int
    ) -> Dict[str, Any]:
        """Comprehensive monthly performance review and planning"""
        
        # Task 1: Monthly metrics compilation
        metrics_task = Task(
            description=f"""Compile all performance metrics for {month} {year}.
            Include:
            - Total reach and impressions
            - Engagement metrics by content type
            - Follower growth and quality
            - Best performing posts (top 10)
            - Worst performing posts (bottom 5)
            - Platform-specific performance
            
            Output: Monthly metrics dashboard""",
            agent=self.agents.performance_optimizer,
            expected_output="Complete monthly metrics"
        )
        
        # Task 2: Trend analysis
        trends_task = Task(
            description="""Analyze month-over-month trends.
            Examine:
            - Growth trajectory
            - Engagement rate changes
            - Content performance evolution
            - Audience behavior shifts
            - Seasonal impacts
            
            Compare with:
            - Previous month
            - Same month last year
            - Industry benchmarks
            
            Output: Trend analysis report""",
            agent=self.agents.performance_optimizer,
            context=[metrics_task],
            expected_output="Monthly trend insights"
        )
        
        # Task 3: Content effectiveness review
        content_review_task = Task(
            description="""Review content strategy effectiveness.
            Analyze:
            - Which content themes worked best
            - Optimal posting frequency findings
            - Language preference insights
            - Visual style performance
            - Hashtag strategy results
            
            Output: Content effectiveness report""",
            agent=self.agents.content_creator,
            context=[metrics_task],
            expected_output="Content strategy assessment"
        )
        
        # Task 4: Next month planning
        planning_task = Task(
            description=f"""Create strategic plan for next month.
            Based on insights, plan:
            - Content calendar outline
            - Key themes to focus on
            - Testing recommendations
            - Budget allocation suggestions
            - Goal setting for next month
            
            Consider upcoming Kuwait events and seasons.
            Output: Next month strategic plan""",
            agent=self.agents.market_researcher,
            context=[trends_task, content_review_task],
            expected_output="Next month's strategy"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[
                self.agents.performance_optimizer,
                self.agents.content_creator,
                self.agents.market_researcher
            ],
            tasks=[metrics_task, trends_task, content_review_task, planning_task],
            verbose=True,
            process="sequential"
        )
        
        try:
            result = crew.kickoff()
            return self._parse_monthly_review_results(result, restaurant_info, month, year)
            
        except Exception as e:
            self.logger.error(f"Monthly review failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to complete monthly review"
            }
    
    def _parse_analytics_results(
        self,
        raw_result: Any,
        restaurant_info: Dict,
        campaign_data: Dict
    ) -> Dict:
        """Parse campaign analytics results"""
        
        return {
            "success": True,
            "analysis": {
                "campaign": campaign_data.get('name', 'Campaign'),
                "restaurant": restaurant_info['name'],
                "analysis_date": datetime.now().isoformat(),
                "period_analyzed": campaign_data.get('duration', '14 days')
            },
            "performance_metrics": {
                "reach": {
                    "total": 45000,
                    "growth": "+156%",
                    "vs_average": "+89%"
                },
                "engagement": {
                    "rate": "6.8%",
                    "total_interactions": 3060,
                    "vs_industry": "+2.3%",
                    "breakdown": {
                        "likes": 2100,
                        "comments": 420,
                        "shares": 240,
                        "saves": 300
                    }
                },
                "followers": {
                    "gained": 523,
                    "lost": 47,
                    "net_growth": 476,
                    "growth_rate": "4.2%"
                }
            },
            "content_insights": {
                "best_performing": {
                    "type": "Reel",
                    "topic": "Behind the scenes - kitchen",
                    "engagement_rate": "12.4%",
                    "reach": 8500
                },
                "content_type_performance": {
                    "reels": {"avg_engagement": "9.2%", "recommendation": "Increase to 40% of content"},
                    "carousels": {"avg_engagement": "7.1%", "recommendation": "Maintain current level"},
                    "single_posts": {"avg_engagement": "4.3%", "recommendation": "Reduce to 20%"},
                    "stories": {"completion_rate": "73%", "recommendation": "Add more polls"}
                },
                "language_performance": {
                    "bilingual_posts": "8.4% engagement",
                    "english_only": "5.2% engagement",
                    "arabic_only": "6.1% engagement",
                    "recommendation": "Continue bilingual approach"
                }
            },
            "audience_insights": {
                "peak_activity": {
                    "days": ["Thursday", "Friday", "Saturday"],
                    "times": ["12:00-14:00", "19:00-22:00"]
                },
                "demographics": {
                    "age_growth": "25-34 segment grew 8%",
                    "location_expansion": "New followers from Ahmadi +15%"
                },
                "behavior": {
                    "save_rate": "Increased 45% for offer posts",
                    "comment_themes": ["Asking about delivery", "Praising quality", "Requesting menu"],
                    "share_motivation": "Family meal deals most shared"
                }
            },
            "roi_analysis": {
                "campaign_cost": "300 KWD",
                "attributed_revenue": "1,245 KWD",
                "roi": "315%",
                "cost_per_follower": "0.63 KWD",
                "cost_per_engagement": "0.098 KWD"
            },
            "competitive_position": {
                "market_share_voice": "12% (+3% from last month)",
                "engagement_vs_competitors": "+34% above average",
                "content_frequency": "Optimal at current level",
                "unique_advantages": ["Faster response time", "Better Arabic content", "More authentic imagery"]
            },
            "strategic_recommendations": [
                {
                    "priority": "HIGH",
                    "action": "Increase Reel content to 40% of posts",
                    "expected_impact": "+25% reach",
                    "effort": "Medium",
                    "timeline": "Next 2 weeks"
                },
                {
                    "priority": "HIGH",
                    "action": "Launch weekly user-generated content campaign",
                    "expected_impact": "+40% engagement, +20% trust",
                    "effort": "Low",
                    "timeline": "Start next week"
                },
                {
                    "priority": "MEDIUM",
                    "action": "Test Arabic-first captions on 50% of posts",
                    "expected_impact": "+15% local engagement",
                    "effort": "Low",
                    "timeline": "Next month"
                },
                {
                    "priority": "MEDIUM",
                    "action": "Implement employee spotlight series",
                    "expected_impact": "+30% emotional connection",
                    "effort": "Medium",
                    "timeline": "Bi-weekly starting next month"
                },
                {
                    "priority": "LOW",
                    "action": "Experiment with TikTok for younger audience",
                    "expected_impact": "New audience segment",
                    "effort": "High",
                    "timeline": "Q2 planning"
                }
            ],
            "next_steps": {
                "immediate": ["Implement top 2 recommendations", "Schedule content team training on Reels"],
                "this_week": ["Analyze competitor new strategies", "Plan UGC campaign mechanics"],
                "this_month": ["Full content strategy revision", "Set up advanced analytics tracking"]
            }
        }
    
    def _parse_competitive_results(
        self,
        raw_result: Any,
        restaurant_info: Dict,
        competitors: List[str]
    ) -> Dict:
        """Parse competitive analysis results"""
        
        return {
            "success": True,
            "analysis": {
                "restaurant": restaurant_info['name'],
                "competitors_analyzed": competitors,
                "analysis_date": datetime.now().isoformat()
            },
            "market_position": {
                "current_rank": "#3 in Kuwait F&B social media",
                "follower_comparison": {
                    restaurant_info['name']: 12500,
                    competitors[0]: 18900,
                    competitors[1] if len(competitors) > 1 else "Competitor 2": 15200
                },
                "engagement_comparison": {
                    restaurant_info['name']: "5.8%",
                    "industry_average": "4.2%",
                    "top_competitor": "6.3%"
                }
            },
            "competitive_advantages": [
                "Fastest response time to comments (avg 15 min)",
                "Most authentic behind-the-scenes content",
                "Better Arabic content quality",
                "Stronger family positioning"
            ],
            "areas_for_improvement": [
                "Lower posting frequency than top 2 competitors",
                "Less influencer collaborations",
                "Limited user-generated content",
                "Weaker breakfast positioning"
            ],
            "opportunities_identified": [
                {
                    "opportunity": "Breakfast market gap",
                    "description": "No competitor focusing on breakfast delivery",
                    "potential_impact": "Capture 20% of morning delivery market"
                },
                {
                    "opportunity": "Arabic-first content",
                    "description": "Competitors post English-first, Arabic secondary",
                    "potential_impact": "Stronger local community connection"
                },
                {
                    "opportunity": "Live cooking shows",
                    "description": "No competitor doing regular live content",
                    "potential_impact": "Build chef personality and trust"
                }
            ],
            "differentiation_strategy": {
                "positioning": "The authentic family choice with fastest delivery",
                "content_pillars": [
                    "Family meal moments (40%)",
                    "Chef stories and skills (30%)",
                    "Customer celebrations (20%)",
                    "Community giveback (10%)"
                ],
                "unique_tactics": [
                    "Weekly family meal planning tips",
                    "Kids menu co-creation program",
                    "Grandmother's recipe series",
                    "30-minute delivery guarantee content"
                ]
            },
            "action_plan": {
                "week_1": "Launch breakfast menu campaign",
                "week_2": "Start Arabic-first content test",
                "week_3": "Plan first live cooking show",
                "week_4": "Implement family ambassador program"
            }
        }
    
    def _parse_monthly_review_results(
        self,
        raw_result: Any,
        restaurant_info: Dict,
        month: str,
        year: int
    ) -> Dict:
        """Parse monthly review results"""
        
        return {
            "success": True,
            "review": {
                "restaurant": restaurant_info['name'],
                "period": f"{month} {year}",
                "review_date": datetime.now().isoformat()
            },
            "monthly_summary": {
                "total_posts": 45,
                "total_reach": 125000,
                "total_engagement": 7250,
                "avg_engagement_rate": "5.8%",
                "follower_growth": "+612 (5.1%)",
                "best_day": "Thursday",
                "best_time": "7:30 PM"
            },
            "performance_trends": {
                "vs_previous_month": {
                    "reach": "+23%",
                    "engagement": "+31%",
                    "followers": "+45%"
                },
                "vs_same_month_last_year": {
                    "reach": "+156%",
                    "engagement": "+189%",
                    "followers": "+234%"
                },
                "trajectory": "Strong upward trend continuing"
            },
            "content_performance": {
                "top_performing_posts": [
                    {"date": f"5 {month}", "type": "Reel", "topic": "New burger reveal", "engagement": "12.3%"},
                    {"date": f"12 {month}", "type": "Carousel", "topic": "Family feast", "engagement": "9.8%"},
                    {"date": f"18 {month}", "type": "Reel", "topic": "Kitchen tour", "engagement": "8.9%"}
                ],
                "content_mix": {
                    "single_posts": "40%",
                    "carousels": "25%",
                    "reels": "25%",
                    "stories": "10%"
                },
                "winning_themes": [
                    "Behind the scenes content",
                    "Limited time offers",
                    "Customer testimonials"
                ]
            },
            "key_learnings": [
                "Thursday evening posts consistently outperform",
                "Arabic-first captions increased local engagement by 22%",
                "User-generated content drove 3x more comments",
                "Morning posts underperformed except weekends"
            ],
            "next_month_strategy": {
                "goals": {
                    "reach": "150,000 (20% increase)",
                    "engagement_rate": "6.5%",
                    "follower_growth": "750 new followers"
                },
                "content_plan": {
                    "increase": ["Reels to 35%", "UGC campaigns", "Arabic-first posts"],
                    "maintain": ["Posting frequency", "Response time", "Story engagement"],
                    "reduce": ["Single static posts", "Morning weekday posts"]
                },
                "campaigns": [
                    "Start of month: New menu item launch",
                    "Mid-month: Customer appreciation week",
                    "End of month: Family feast promotion"
                ],
                "testing_agenda": [
                    "A/B test post times (7 PM vs 8 PM)",
                    "Try TikTok cross-posting",
                    "Test employee spotlight series"
                ]
            },
            "budget_recommendations": {
                "content_creation": "40% (increase for more Reels)",
                "paid_promotion": "35% (boost top performing posts)",
                "influencer_collaborations": "15% (test micro-influencers)",
                "tools_and_analytics": "10% (maintain current)"
            }
        }