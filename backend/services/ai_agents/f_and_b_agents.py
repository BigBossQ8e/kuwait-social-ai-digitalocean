"""
Kuwait F&B Specialized Agents
Multi-agent team for food & beverage social media management
"""

from typing import List, Dict, Any
from .base_agent import KuwaitBaseAgent
from .tools.research_tools import (
    CompetitorAnalysisTool, TrendAnalysisTool, AreaInsightsTool
)
from .tools.content_tools import (
    TemplateGeneratorTool, HashtagOptimizerTool, EmojiFoodExpertTool
)
from .tools.compliance_tools import (
    HalalVerificationTool, CulturalCheckTool, PrayerTimeAwarenessTool
)
from .tools.scheduling_tools import (
    PrayerTimeSchedulerTool, PeakTimeAnalyzerTool, WeatherAwareSchedulerTool
)
from .tools.analytics_tools import (
    EngagementAnalyzerTool, OrderAttributionTool, ABTestingTool
)

class KuwaitFBAgents:
    """Specialized agents for Kuwait F&B social media management"""
    
    def __init__(self):
        # Agent 1: Market Research Specialist
        self.market_researcher = KuwaitBaseAgent(
            role='Kuwait F&B Market Research Specialist',
            goal='Identify trending dishes, popular times, and competitor strategies in Kuwait',
            backstory="""You are an expert in Kuwait's food scene with deep knowledge of:
            - Every trending restaurant from Avenues to small local eateries
            - Popular dishes among different demographics (locals, expats, youth)
            - Cultural food preferences and seasonal trends
            - Competition analysis across all major areas
            You understand what makes Kuwaitis choose one restaurant over another.""",
            tools=[
                CompetitorAnalysisTool,
                TrendAnalysisTool,
                AreaInsightsTool
            ],
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 2: Cultural Compliance Officer
        self.cultural_compliance = KuwaitBaseAgent(
            role='Kuwait Cultural & Religious Compliance Expert',
            goal='Ensure all content respects Islamic values and Kuwait cultural norms',
            backstory="""You are deeply knowledgeable about:
            - Islamic dietary laws (halal/haram)
            - Kuwait's conservative social values
            - Appropriate imagery and language for public content
            - Prayer times and religious observances
            - Cultural sensitivities during Ramadan and other occasions
            You ensure content is respectful while remaining engaging.""",
            tools=[
                HalalVerificationTool,
                CulturalCheckTool,
                PrayerTimeAwarenessTool
            ],
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 3: Content Creation Specialist
        self.content_creator = KuwaitBaseAgent(
            role='F&B Social Media Content Creator for Kuwait',
            goal='Create compelling, hunger-inducing content that drives orders',
            backstory="""You are a master at creating food content specifically for Kuwait audiences:
            - You know which Arabic and English words trigger cravings
            - You understand platform-specific content (Instagram stories vs posts)
            - You're an expert at food photography descriptions
            - You know trending formats and challenges in Kuwait
            - You balance professional quality with authentic, relatable content
            Your content makes people immediately want to order.""",
            tools=[
                TemplateGeneratorTool,
                HashtagOptimizerTool,
                EmojiFoodExpertTool
            ],
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 4: Timing Optimization Expert
        self.timing_expert = KuwaitBaseAgent(
            role='Kuwait Social Media Timing Expert',
            goal='Schedule posts for maximum engagement avoiding prayer times',
            backstory="""You are an expert in Kuwait's unique social media patterns:
            - You know exactly when Kuwaitis check Instagram, Twitter, TikTok
            - You understand meal decision times (lunch at work, family dinners)
            - You respect and work around all five daily prayer times
            - You know weekend (Thursday-Friday) vs weekday patterns
            - You factor in weather (summer indoor dining vs winter outdoor)
            Your timing strategies maximize reach and engagement.""",
            tools=[
                PrayerTimeSchedulerTool,
                PeakTimeAnalyzerTool,
                WeatherAwareSchedulerTool
            ],
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 5: Performance Optimization Agent
        self.performance_optimizer = KuwaitBaseAgent(
            role='Campaign Performance Optimizer for Kuwait F&B',
            goal='Analyze results and continuously improve content strategy',
            backstory="""You are data-driven and understand Kuwait F&B success metrics:
            - You track what content drives actual orders vs just likes
            - You identify which dishes become bestsellers from social posts
            - You understand platform-specific metrics (Instagram saves, story exits)
            - You know Kuwait's unique engagement patterns
            - You can predict viral potential based on local trends
            You turn data into actionable improvements.""",
            tools=[
                EngagementAnalyzerTool,
                OrderAttributionTool,
                ABTestingTool
            ],
            verbose=True,
            allow_delegation=False
        )
        
        # Agent 6: Arabic Content Specialist
        self.arabic_specialist = KuwaitBaseAgent(
            role='Arabic Content & Localization Expert',
            goal='Create authentic Arabic content that resonates with Kuwaiti audience',
            backstory="""You are a native Arabic speaker specializing in:
            - Kuwaiti dialect and expressions
            - Translating marketing content while keeping it catchy
            - Arabic food terminology and descriptions
            - Local slang and trending phrases
            - Balancing formal and casual Arabic appropriately
            You ensure Arabic content feels natural, not translated.""",
            tools=[
                TemplateGeneratorTool,
                HashtagOptimizerTool
            ],
            verbose=True,
            allow_delegation=False
        )
    
    def get_all_agents(self) -> List[KuwaitBaseAgent]:
        """Return all agents as a list"""
        return [
            self.market_researcher,
            self.cultural_compliance,
            self.content_creator,
            self.timing_expert,
            self.performance_optimizer,
            self.arabic_specialist
        ]
    
    def get_content_team(self) -> List[KuwaitBaseAgent]:
        """Get agents focused on content creation"""
        return [
            self.content_creator,
            self.arabic_specialist,
            self.cultural_compliance
        ]
    
    def get_strategy_team(self) -> List[KuwaitBaseAgent]:
        """Get agents focused on strategy and analysis"""
        return [
            self.market_researcher,
            self.timing_expert,
            self.performance_optimizer
        ]
    
    def assign_agent_by_task(self, task_type: str) -> KuwaitBaseAgent:
        """Assign the most appropriate agent based on task type"""
        task_agent_mapping = {
            'research': self.market_researcher,
            'content': self.content_creator,
            'arabic': self.arabic_specialist,
            'compliance': self.cultural_compliance,
            'timing': self.timing_expert,
            'analytics': self.performance_optimizer,
            'translation': self.arabic_specialist,
            'campaign': self.market_researcher,  # Start with research
            'hashtags': self.content_creator,
            'scheduling': self.timing_expert
        }
        
        # Find best match
        task_lower = task_type.lower()
        for key, agent in task_agent_mapping.items():
            if key in task_lower:
                return agent
        
        # Default to content creator
        return self.content_creator