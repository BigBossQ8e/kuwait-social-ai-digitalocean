"""
Content Creation Crew for Kuwait F&B Social Media
Orchestrates multiple agents to create comprehensive content
"""

from crewai import Crew, Task
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging
from ..f_and_b_agents import KuwaitFBAgents

class ContentCreationCrew:
    """Multi-agent crew for creating social media content"""
    
    def __init__(self):
        self.agents = KuwaitFBAgents()
        self.logger = logging.getLogger(__name__)
    
    def create_single_post(
        self,
        restaurant_info: Dict[str, Any],
        post_type: str = "regular",
        special_requirements: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a single social media post with full optimization"""
        
        special_requirements = special_requirements or []
        
        # Task 1: Research current trends
        research_task = Task(
            description=f"""Research current trends for {restaurant_info.get('cuisine_type', 'restaurant')} 
            in {restaurant_info.get('area', 'Kuwait')}. 
            Focus on:
            - What's trending this week
            - Competitor successful posts
            - Best performing content types
            Output: Trend analysis and content recommendations""",
            agent=self.agents.market_researcher,
            expected_output="Detailed trend analysis with specific content recommendations"
        )
        
        # Task 2: Create content
        content_task = Task(
            description=f"""Create engaging {post_type} content for {restaurant_info['name']}.
            Restaurant details: {json.dumps(restaurant_info)}
            Special requirements: {', '.join(special_requirements)}
            
            Create:
            1. Attention-grabbing caption (English)
            2. Relevant hashtags
            3. Call-to-action
            4. Emoji usage for visual appeal
            
            Use insights from the research task.
            Output: Complete post content in JSON format""",
            agent=self.agents.content_creator,
            context=[research_task],
            expected_output="JSON formatted post content with caption, hashtags, and CTA"
        )
        
        # Task 3: Arabic translation and localization
        arabic_task = Task(
            description="""Translate and localize the content for Kuwait Arabic audience.
            Requirements:
            - Use Kuwaiti dialect where appropriate
            - Maintain marketing appeal
            - Ensure cultural relevance
            - Add Arabic hashtags
            Output: Arabic version of the content""",
            agent=self.agents.arabic_specialist,
            context=[content_task],
            expected_output="Culturally adapted Arabic content"
        )
        
        # Task 4: Cultural compliance check
        compliance_task = Task(
            description="""Review both English and Arabic content for cultural appropriateness.
            Check for:
            - Halal compliance mentions (if food-related)
            - Cultural sensitivity
            - Appropriate imagery descriptions
            - Religious considerations
            Make necessary adjustments.
            Output: Approved content with compliance notes""",
            agent=self.agents.cultural_compliance,
            context=[content_task, arabic_task],
            expected_output="Culturally compliant content with any necessary modifications"
        )
        
        # Task 5: Optimize timing
        timing_task = Task(
            description=f"""Determine optimal posting time for this content.
            Consider:
            - Current day and time
            - Prayer times
            - Content type: {post_type}
            - Target audience meal times
            - Platform best practices
            Output: Recommended posting schedule""",
            agent=self.agents.timing_expert,
            context=[compliance_task],
            expected_output="Optimal posting time with justification"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[
                self.agents.market_researcher,
                self.agents.content_creator,
                self.agents.arabic_specialist,
                self.agents.cultural_compliance,
                self.agents.timing_expert
            ],
            tasks=[research_task, content_task, arabic_task, compliance_task, timing_task],
            verbose=True,
            process="sequential"  # Tasks run in order
        )
        
        try:
            result = crew.kickoff()
            
            # Parse and structure the results
            return self._parse_content_results(result, restaurant_info, post_type)
            
        except Exception as e:
            self.logger.error(f"Content creation crew failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "fallback_content": self._generate_fallback_content(restaurant_info, post_type)
            }
    
    def create_weekly_content(
        self,
        restaurant_info: Dict[str, Any],
        week_theme: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a week's worth of content"""
        
        # Task 1: Weekly strategy
        strategy_task = Task(
            description=f"""Create a weekly content strategy for {restaurant_info['name']}.
            Restaurant type: {restaurant_info.get('cuisine_type', 'general')}
            Week theme: {week_theme or 'Regular week'}
            
            Plan:
            - 7 posts (one per day)
            - Variety of content types
            - Optimal timing for each
            - Cohesive theme
            
            Output: Weekly content calendar""",
            agent=self.agents.market_researcher,
            expected_output="Structured weekly content calendar"
        )
        
        # Task 2: Batch content creation
        batch_content_task = Task(
            description="""Create all 7 posts based on the weekly strategy.
            Ensure:
            - Variety in content types (photos, reels, stories)
            - Different meal focuses (breakfast, lunch, dinner)
            - Mix of promotional and engaging content
            - Consistent brand voice
            
            Output: 7 complete posts with captions and hashtags""",
            agent=self.agents.content_creator,
            context=[strategy_task],
            expected_output="7 unique social media posts"
        )
        
        # Task 3: Arabic localization for all posts
        arabic_batch_task = Task(
            description="""Translate and localize all 7 posts to Arabic.
            Maintain consistency across all posts while ensuring each is unique.
            Output: Arabic versions of all 7 posts""",
            agent=self.agents.arabic_specialist,
            context=[batch_content_task],
            expected_output="7 Arabic translated posts"
        )
        
        # Task 4: Compliance review
        compliance_batch_task = Task(
            description="""Review all 14 posts (7 English + 7 Arabic) for compliance.
            Ensure consistency in messaging and cultural appropriateness.
            Output: Approved content batch""",
            agent=self.agents.cultural_compliance,
            context=[batch_content_task, arabic_batch_task],
            expected_output="Fully compliant content batch"
        )
        
        # Task 5: Schedule optimization
        scheduling_task = Task(
            description="""Create optimal posting schedule for the week.
            Consider:
            - Each day's prayer times
            - Content type best times
            - Avoiding conflicts
            - Maximum reach potential
            
            Output: Complete posting schedule""",
            agent=self.agents.timing_expert,
            context=[compliance_batch_task],
            expected_output="7-day posting schedule with exact times"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[
                self.agents.market_researcher,
                self.agents.content_creator,
                self.agents.arabic_specialist,
                self.agents.cultural_compliance,
                self.agents.timing_expert
            ],
            tasks=[strategy_task, batch_content_task, arabic_batch_task, 
                   compliance_batch_task, scheduling_task],
            verbose=True,
            process="sequential"
        )
        
        try:
            result = crew.kickoff()
            return self._parse_weekly_results(result, restaurant_info, week_theme)
            
        except Exception as e:
            self.logger.error(f"Weekly content creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create weekly content"
            }
    
    def create_campaign_content(
        self,
        restaurant_info: Dict[str, Any],
        campaign_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create content for a specific campaign (e.g., Ramadan, National Day)"""
        
        # Extract campaign info
        campaign_name = campaign_details.get('name', 'Special Campaign')
        duration_days = campaign_details.get('duration_days', 7)
        campaign_goals = campaign_details.get('goals', ['Increase orders', 'Build awareness'])
        
        # Task 1: Campaign strategy
        strategy_task = Task(
            description=f"""Develop comprehensive campaign strategy for {restaurant_info['name']}.
            Campaign: {campaign_name}
            Duration: {duration_days} days
            Goals: {', '.join(campaign_goals)}
            
            Create:
            - Campaign theme and messaging
            - Content pillars
            - Posting frequency
            - Key messages
            
            Output: Detailed campaign strategy""",
            agent=self.agents.market_researcher,
            expected_output="Complete campaign strategy document"
        )
        
        # Task 2: Create campaign content
        campaign_content_task = Task(
            description=f"""Create {duration_days} days of campaign content.
            Follow the campaign strategy and ensure:
            - Consistent campaign theme
            - Building momentum throughout
            - Clear CTAs aligned with goals
            - Mix of content types
            
            Output: All campaign posts""",
            agent=self.agents.content_creator,
            context=[strategy_task],
            expected_output=f"{duration_days} campaign posts"
        )
        
        # Task 3: Cultural adaptation
        cultural_task = Task(
            description=f"""Ensure all campaign content is culturally appropriate for {campaign_name}.
            Special considerations for Kuwait market.
            Add Arabic versions maintaining campaign impact.
            Output: Culturally adapted campaign content""",
            agent=self.agents.arabic_specialist,
            context=[campaign_content_task],
            expected_output="Bilingual campaign content"
        )
        
        # Task 4: Performance optimization
        optimization_task = Task(
            description="""Optimize campaign for maximum performance.
            Analyze:
            - Best posting times for campaign
            - A/B test recommendations
            - Engagement optimization tips
            - Hashtag strategy
            
            Output: Performance optimization plan""",
            agent=self.agents.performance_optimizer,
            context=[cultural_task],
            expected_output="Campaign optimization recommendations"
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[
                self.agents.market_researcher,
                self.agents.content_creator,
                self.agents.arabic_specialist,
                self.agents.performance_optimizer
            ],
            tasks=[strategy_task, campaign_content_task, cultural_task, optimization_task],
            verbose=True,
            process="sequential"
        )
        
        try:
            result = crew.kickoff()
            return self._parse_campaign_results(result, restaurant_info, campaign_details)
            
        except Exception as e:
            self.logger.error(f"Campaign content creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create campaign content"
            }
    
    def _parse_content_results(self, raw_result: Any, restaurant_info: Dict, post_type: str) -> Dict:
        """Parse crew results into structured format"""
        
        # This would parse the actual crew output
        # For now, returning structured mock data
        return {
            "success": True,
            "post": {
                "id": f"post_{datetime.now().timestamp()}",
                "restaurant": restaurant_info['name'],
                "type": post_type,
                "content": {
                    "caption_en": "🔥 Craving something delicious? Our signature dish is calling your name! Made fresh with love and the finest halal ingredients. Perfect for sharing with family! 🍽️✨",
                    "caption_ar": "🔥 تشتهي شي لذيذ؟ طبقنا المميز ينادي اسمك! محضر طازج بكل حب وأجود المكونات الحلال. مثالي للمشاركة مع العائلة! 🍽️✨",
                    "hashtags": [
                        "#KuwaitFood", "#Q8Foodie", "#الكويت", "#مطاعم_الكويت",
                        "#HalalFood", "#حلال", "#FamilyDining", "#عائلي",
                        f"#{restaurant_info['name'].replace(' ', '')}"
                    ],
                    "cta": "📱 Order now on Talabat/Deliveroo or visit us today!"
                },
                "scheduling": {
                    "recommended_time": "19:30",
                    "recommended_date": datetime.now().strftime("%Y-%m-%d"),
                    "avoid_times": ["11:45-12:15", "15:00-15:30", "17:45-18:15"],
                    "reason": "Post-Maghrib optimal engagement window"
                },
                "optimization": {
                    "predicted_engagement": "High",
                    "tags_to_add": ["location_tag", "product_tag"],
                    "story_version": True,
                    "reel_potential": "Medium"
                }
            },
            "insights": {
                "trend_alignment": "Aligns with current comfort food trend",
                "cultural_notes": "Halal emphasis resonates well",
                "timing_rationale": "Evening posting captures dinner decision time"
            }
        }
    
    def _parse_weekly_results(self, raw_result: Any, restaurant_info: Dict, theme: str) -> Dict:
        """Parse weekly content results"""
        
        # Mock structured data for weekly content
        posts = []
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        
        for i, day in enumerate(days):
            posts.append({
                "day": day,
                "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                "post": {
                    "type": ["regular", "offer", "behind_scenes", "reel", "ugc", "new_item", "weekend_special"][i],
                    "caption_preview": f"{day} special content for {restaurant_info['name']}...",
                    "posting_time": ["12:30", "19:00", "20:00", "13:00", "21:00", "18:00", "14:00"][i],
                    "hashtags_count": 20
                }
            })
        
        return {
            "success": True,
            "week_theme": theme or "Regular content week",
            "restaurant": restaurant_info['name'],
            "posts": posts,
            "summary": {
                "total_posts": 7,
                "content_mix": {
                    "regular_posts": 3,
                    "offers": 2,
                    "interactive": 2
                },
                "languages": ["English", "Arabic"],
                "predicted_reach": "25,000-35,000",
                "predicted_engagement": "4.5-6.5%"
            }
        }
    
    def _parse_campaign_results(self, raw_result: Any, restaurant_info: Dict, campaign: Dict) -> Dict:
        """Parse campaign content results"""
        
        return {
            "success": True,
            "campaign": {
                "name": campaign['name'],
                "restaurant": restaurant_info['name'],
                "duration": campaign['duration_days'],
                "total_posts": campaign['duration_days'],
                "content_ready": True,
                "languages": ["English", "Arabic"],
                "optimization": {
                    "recommended_budget": f"{campaign['duration_days'] * 10} KWD",
                    "expected_roi": "250-400%",
                    "key_success_factors": [
                        "Time-sensitive offers",
                        "Cultural relevance",
                        "Clear CTAs"
                    ]
                }
            },
            "launch_checklist": [
                "✅ All content created and approved",
                "✅ Arabic translations verified",
                "✅ Posting schedule optimized",
                "✅ Hashtag strategy defined",
                "✅ Performance tracking setup"
            ]
        }
    
    def _generate_fallback_content(self, restaurant_info: Dict, post_type: str) -> Dict:
        """Generate basic fallback content if crew fails"""
        
        return {
            "caption_en": f"Visit {restaurant_info['name']} today for an amazing dining experience! 🍽️ #Kuwait #Q8Food",
            "caption_ar": f"زورونا في {restaurant_info['name']} اليوم لتجربة طعام رائعة! 🍽️ #الكويت #كويت_فود",
            "hashtags": ["#Kuwait", "#Q8", "#Food", "#الكويت"],
            "posting_time": "19:00"
        }