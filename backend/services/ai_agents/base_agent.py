"""
Base Agent Class for Kuwait Social AI
Provides common functionality for all specialized agents
"""

from crewai import Agent
from typing import List, Dict, Any, Optional, ClassVar
from langchain.tools import Tool
import logging
from config.platform_config import PlatformConfig

class KuwaitBaseAgent(Agent):
    """Base agent with Kuwait-specific context and capabilities"""
    
    # Class-level Kuwait context (shared by all instances)
    kuwait_context: ClassVar[Dict[str, Any]] = {
        'country': 'Kuwait',
        'timezone': 'Asia/Kuwait',
        'currency': 'KWD',
        'languages': ['Arabic', 'English'],
        'weekend': ['Friday', 'Saturday'],
        'business_days': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday'],
        'cultural_considerations': [
            'Islamic values and halal requirements',
            'Prayer time awareness',
            'Conservative social norms',
            'Family-oriented culture',
            'Respect for traditions'
        ],
        'major_areas': [
            'Kuwait City', 'Hawally', 'Salmiya', 'Farwaniya',
            'Ahmadi', 'Jahra', 'Mubarak Al-Kabeer'
        ],
        'food_delivery_platforms': [
            'Talabat', 'Deliveroo', 'Carriage', 'Bilbayt'
        ]
    }
    
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        tools: List[Tool] = None,
        **kwargs
    ):
        # Enhance backstory with Kuwait context
        enhanced_backstory = f"{backstory}\n\nYou operate in Kuwait and understand the local market deeply. " \
                            f"You are aware of Islamic values, local customs, and the unique aspects of Kuwait's " \
                            f"food and beverage industry. You respect prayer times and cultural sensitivities."
        
        # Initialize parent Agent
        super().__init__(
            role=role,
            goal=goal,
            backstory=enhanced_backstory,
            tools=tools or [],
            **kwargs
        )
    
    def add_kuwait_context(self, prompt: str) -> str:
        """Add Kuwait-specific context to any prompt"""
        kuwait_info = f"""
        Context: Operating in Kuwait
        - Primary languages: Arabic and English
        - Currency: KWD (Kuwaiti Dinar)
        - Weekend: Friday-Saturday
        - Key consideration: Halal compliance and prayer times
        - Popular areas: {', '.join(self.kuwait_context['major_areas'][:3])}
        """
        return f"{kuwait_info}\n\n{prompt}"
    
    def validate_cultural_appropriateness(self, content: str) -> Dict[str, Any]:
        """Check if content is culturally appropriate for Kuwait"""
        issues = []
        warnings = []
        
        # Check for potentially inappropriate content
        inappropriate_terms = [
            'pork', 'alcohol', 'wine', 'beer', 'bacon',
            'non-halal', 'dating', 'nightclub', 'bar'
        ]
        
        content_lower = content.lower()
        for term in inappropriate_terms:
            if term in content_lower:
                issues.append(f"Contains potentially inappropriate term: '{term}'")
        
        # Check for positive cultural elements
        positive_terms = ['halal', 'حلال', 'family', 'traditional', 'authentic']
        has_positive = any(term in content_lower for term in positive_terms)
        
        if not has_positive and 'food' in content_lower:
            warnings.append("Consider mentioning 'halal' or 'حلال' for food content")
        
        return {
            'is_appropriate': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'has_cultural_markers': has_positive
        }
    
    def format_bilingual_content(self, english_text: str, arabic_text: str) -> str:
        """Format content in both English and Arabic appropriately"""
        return f"{english_text}\n\n{arabic_text}"
    
    def get_optimal_posting_times(self, day: str) -> List[str]:
        """Get optimal posting times considering Kuwait's schedule"""
        # Kuwait-specific optimal times (avoiding prayer times)
        weekday_times = [
            "08:00", "11:00", "14:00", "17:00", "20:00", "22:00"
        ]
        weekend_times = [
            "10:00", "13:00", "16:00", "19:00", "21:00", "23:00"
        ]
        
        if day in ['Friday', 'Saturday']:
            return weekend_times
        return weekday_times
    
    def localize_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure content is properly localized for Kuwait"""
        # Add Kuwait-specific hashtags if not present
        kuwait_hashtags = ['#Kuwait', '#الكويت', '#Q8']
        
        if 'hashtags' in content:
            for tag in kuwait_hashtags:
                if tag not in content['hashtags']:
                    content['hashtags'].append(tag)
        
        # Add location context if missing
        if 'location' not in content and 'area' in content:
            content['location'] = f"{content['area']}, Kuwait"
        
        return content