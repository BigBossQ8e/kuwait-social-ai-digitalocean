"""
AI Service for content generation, translation, and enhancement
Supports OpenAI and Claude APIs with Multi-Agent Orchestration
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from openai import OpenAI
from anthropic import Anthropic
import re

# Import F&B configuration
try:
    from config.f_b_config import (
        F_B_BUSINESS_TYPES, KUWAIT_CUISINES, F_B_HASHTAGS,
        F_B_KEYWORDS, KUWAIT_MEAL_TIMES, F_B_EMOJIS
    )
except ImportError:
    # Fallback if config not found
    F_B_BUSINESS_TYPES = ['restaurant', 'cafe', 'food', 'f&b']
    F_B_HASHTAGS = {'general': ['#KuwaitFood', '#Q8Food']}

logger = logging.getLogger(__name__)

# Import agent framework
try:
    from .ai_agents.crews import (
        ContentCreationCrew, CampaignManagementCrew, AnalyticsInsightsCrew
    )
    AGENTS_AVAILABLE = True
except (ImportError, TypeError) as e:
    AGENTS_AVAILABLE = False
    logger.warning(f"Agent framework not available: {str(e)}. Using direct AI generation only.")

class AIService:
    """Service for AI-powered content generation and processing"""
    
    def __init__(self):
        # Initialize API clients
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.default_provider = os.getenv('AI_PROVIDER', 'openai')  # 'openai' or 'anthropic'
        
        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)
            
        if self.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=self.anthropic_api_key)
        
        # Initialize agent crews if available
        self.agents_enabled = AGENTS_AVAILABLE and os.getenv('ENABLE_AGENTS', 'true').lower() == 'true'
        if self.agents_enabled:
            try:
                self.content_crew = ContentCreationCrew()
                self.campaign_crew = CampaignManagementCrew()
                self.analytics_crew = AnalyticsInsightsCrew()
                logger.info("Agent framework initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize agent framework: {str(e)}")
                self.agents_enabled = False
                
        # Kuwait-specific configurations
        self.kuwait_context = {
            'country': 'Kuwait',
            'currency': 'KWD',
            'language': 'Arabic and English',
            'culture': 'Islamic, conservative',
            'business_hours': 'Sunday-Thursday',
            'local_hashtags': ['#Kuwait', '#Q8', '#الكويت'],
            'prayer_times': ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha'],
            'food_hashtags': ['#KuwaitFood', '#Q8Food', '#KuwaitRestaurants', '#Q8Restaurants', 
                             '#KuwaitFoodies', '#مطاعم_الكويت', '#طعام_الكويت', '#Q8Eats',
                             '#KuwaitDining', '#FoodieKuwait', '#KuwaitCafe', '#Q8Cafe'],
            'food_terms': ['halal', 'family-friendly', 'delivery', 'dine-in', 'takeaway',
                          'iftar', 'suhoor', 'authentic', 'traditional', 'modern fusion'],
            'popular_cuisines': ['Kuwaiti', 'Lebanese', 'Indian', 'Italian', 'Japanese', 
                               'Turkish', 'Egyptian', 'Persian', 'American', 'Asian fusion']
        }
        
        # Platform specifications
        self.platform_specs = {
            'instagram': {
                'max_length': 2200,
                'hashtag_limit': 30,
                'best_practices': 'Use high-quality visuals, stories, and reels'
            },
            'twitter': {
                'max_length': 280,
                'hashtag_limit': 2,
                'best_practices': 'Keep it concise, use threads for longer content'
            },
            'snapchat': {
                'max_length': 250,
                'hashtag_limit': 1,
                'best_practices': 'Focus on visual content, use geofilters'
            },
            'tiktok': {
                'max_length': 2200,
                'hashtag_limit': 10,
                'best_practices': 'Use trending sounds, keep videos short and engaging'
            }
        }
        
    def generate_content(self, 
                        prompt: str,
                        platform: str = 'instagram',
                        tone: str = 'professional',
                        include_arabic: bool = False,
                        include_hashtags: bool = True,
                        business_type: Optional[str] = None,
                        additional_context: Optional[Dict] = None) -> Dict:
        """
        Generate social media content based on prompt and parameters
        
        Args:
            prompt: The main content request
            platform: Target social media platform
            tone: Writing tone (professional, casual, enthusiastic, formal)
            include_arabic: Whether to include Arabic translation
            include_hashtags: Whether to include hashtag suggestions
            business_type: Type of business (restaurant, retail, service, etc.)
            additional_context: Any additional context for generation
            
        Returns:
            Dict containing generated content, translations, and hashtags
        """
        try:
            # Check if should use agents for this request
            if self._should_use_agents(prompt, {
                'platform': platform,
                'business_type': business_type,
                'additional_context': additional_context
            }):
                # Extract restaurant info from context
                restaurant_info = {
                    'name': additional_context.get('restaurant_name', 'Restaurant') if additional_context else 'Restaurant',
                    'cuisine_type': business_type or 'general',
                    'area': additional_context.get('area', 'Kuwait') if additional_context else 'Kuwait'
                }
                
                # Determine use case from prompt
                use_case = 'single_post'
                if 'campaign' in prompt.lower():
                    if 'ramadan' in prompt.lower():
                        use_case = 'ramadan_campaign'
                    elif 'launch' in prompt.lower():
                        use_case = 'product_launch'
                    else:
                        use_case = 'campaign'
                elif 'weekly' in prompt.lower() or 'week' in prompt.lower():
                    use_case = 'weekly_content'
                elif 'analyze' in prompt.lower() or 'performance' in prompt.lower():
                    use_case = 'performance_analysis'
                
                # Use agents
                agent_result = self.generate_with_agents(
                    prompt=prompt,
                    use_case=use_case,
                    restaurant_info=restaurant_info,
                    platform=platform,
                    tone=tone,
                    include_arabic=include_arabic,
                    include_hashtags=include_hashtags
                )
                
                # Return agent result if successful
                if agent_result.get('success'):
                    return agent_result
                    
            # Continue with regular generation
            # Build comprehensive prompt
            system_prompt = self._build_system_prompt(platform, tone, business_type)
            user_prompt = self._build_user_prompt(prompt, platform, additional_context)
            
            # Generate content
            if self.default_provider == 'anthropic' and self.anthropic_api_key:
                content = self._generate_with_claude(system_prompt, user_prompt)
            else:
                content = self._generate_with_openai(system_prompt, user_prompt)
            
            # Process and structure the response
            result = {
                'content': content,
                'platform': platform,
                'tone': tone,
                'character_count': len(content)
            }
            
            # Generate Arabic translation if requested
            if include_arabic:
                result['arabic_content'] = self.translate_content(content, 'en', 'ar')
                
            # Generate hashtags if requested
            if include_hashtags:
                result['hashtags'] = self.generate_hashtags(content, platform, business_type)
                
            # Add platform-specific recommendations
            result['recommendations'] = self._get_platform_recommendations(platform, content)
            
            # Add posting time suggestions
            result['optimal_posting_times'] = self._get_optimal_posting_times(platform)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise
            
    def translate_content(self, text: str, source_lang: str = 'en', target_lang: str = 'ar') -> str:
        """
        Translate content between languages with cultural adaptation
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text
        """
        try:
            translation_prompt = f"""
            Translate the following text from {source_lang} to {target_lang}.
            Maintain the marketing tone and adapt it culturally for Kuwait.
            Preserve any brand names, hashtags, and emojis.
            
            Text: {text}
            """
            
            if self.default_provider == 'anthropic' and self.anthropic_api_key:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": translation_prompt}]
                )
                return response.content[0].text.strip()
            else:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "user", "content": translation_prompt}],
                    max_tokens=1000,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
                
        except Exception as e:
            logger.error(f"Error translating content: {str(e)}")
            return text  # Return original text if translation fails
            
    def generate_hashtags(self, content: str, platform: str, business_type: Optional[str] = None) -> List[str]:
        """
        Generate relevant hashtags for the content
        
        Args:
            content: The post content
            platform: Target platform
            business_type: Type of business
            
        Returns:
            List of relevant hashtags
        """
        try:
            limit = self.platform_specs.get(platform, {}).get('hashtag_limit', 30)
            
            hashtag_prompt = f"""
            Generate {limit} hashtags for this {platform} post for a {business_type or 'business'} in Kuwait.
            Mix popular Kuwait hashtags with niche ones.
            Include both English and Arabic hashtags.
            
            Content: {content}
            
            Return only the hashtags, one per line, starting with #.
            """
            
            if self.default_provider == 'anthropic' and self.anthropic_api_key:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=500,
                    messages=[{"role": "user", "content": hashtag_prompt}]
                )
                hashtags_text = response.content[0].text
            else:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "user", "content": hashtag_prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
                hashtags_text = response.choices[0].message.content
                
            # Extract hashtags from response
            hashtags = re.findall(r'#\S+', hashtags_text)
            
            # Add Kuwait-specific hashtags
            hashtags.extend(self.kuwait_context['local_hashtags'])
            
            # Add food-specific hashtags if it's F&B related
            if business_type and any(term in business_type.lower() for term in ['restaurant', 'cafe', 'food', 'f&b', 'dining']):
                hashtags.extend(self.kuwait_context['food_hashtags'][:5])
            
            # Remove duplicates and limit
            hashtags = list(dict.fromkeys(hashtags))[:limit]
            
            return hashtags
            
        except Exception as e:
            logger.error(f"Error generating hashtags: {str(e)}")
            return self.kuwait_context['local_hashtags']
            
    def enhance_content(self, content: str, enhancement_type: str = 'grammar') -> Dict:
        """
        Enhance existing content (grammar, tone, engagement)
        
        Args:
            content: Original content
            enhancement_type: Type of enhancement (grammar, tone, engagement)
            
        Returns:
            Enhanced content with suggestions
        """
        try:
            enhancement_prompts = {
                'grammar': "Fix grammar and spelling errors while maintaining the original tone and message.",
                'tone': "Adjust the tone to be more engaging and culturally appropriate for Kuwait audience.",
                'engagement': "Enhance this content to increase engagement with call-to-actions and emotional hooks.",
                'localization': "Adapt this content for Kuwait market with local references and cultural nuances."
            }
            
            prompt = f"""
            {enhancement_prompts.get(enhancement_type, enhancement_prompts['grammar'])}
            
            Original content: {content}
            
            Provide:
            1. Enhanced version
            2. List of changes made
            3. Additional suggestions
            """
            
            if self.default_provider == 'anthropic' and self.anthropic_api_key:
                response = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                result_text = response.content[0].text
            else:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.5
                )
                result_text = response.choices[0].message.content
                
            # Parse the response
            lines = result_text.strip().split('\n')
            enhanced_content = ""
            changes = []
            suggestions = []
            
            section = ""
            for line in lines:
                if "Enhanced version" in line:
                    section = "enhanced"
                elif "changes made" in line:
                    section = "changes"
                elif "suggestions" in line:
                    section = "suggestions"
                elif section == "enhanced" and line.strip():
                    enhanced_content += line + "\n"
                elif section == "changes" and line.strip() and line[0].isdigit():
                    changes.append(line.strip())
                elif section == "suggestions" and line.strip() and line[0].isdigit():
                    suggestions.append(line.strip())
                    
            return {
                'enhanced_content': enhanced_content.strip(),
                'original_content': content,
                'changes': changes,
                'suggestions': suggestions,
                'enhancement_type': enhancement_type
            }
            
        except Exception as e:
            logger.error(f"Error enhancing content: {str(e)}")
            return {
                'enhanced_content': content,
                'original_content': content,
                'changes': [],
                'suggestions': [],
                'error': str(e)
            }
            
    def _build_system_prompt(self, platform: str, tone: str, business_type: Optional[str]) -> str:
        """Build system prompt for AI model"""
        base_prompt = f"""
        You are a social media content expert specializing in the Kuwait market.
        You create engaging {platform} posts for {business_type or 'businesses'} in Kuwait.
        
        Context about Kuwait:
        - Bilingual market (Arabic and English)
        - Islamic culture, conservative values
        - High social media engagement rates
        - Active shopping culture
        - Strong family and community values
        - Prayer times are respected
        - Friday is the holy day, weekend is Friday-Saturday
        """
        
        # Add F&B specific context if it's a food-related business
        if business_type and any(term in business_type.lower() for term in ['restaurant', 'cafe', 'food', 'f&b', 'dining', 'catering']):
            base_prompt += f"""
        
        Food & Beverage specific guidelines for Kuwait:
        - Always mention if food is HALAL (this is crucial)
        - Emphasize family-friendly atmosphere
        - Highlight delivery options (very popular in Kuwait)
        - Mention special dietary options (vegan, gluten-free, etc.)
        - Reference popular meal times: Lunch (12-3 PM), Dinner (7-11 PM)
        - During Ramadan: Focus on Iftar and Suhoor offerings
        - Popular cuisines in Kuwait: {', '.join(self.kuwait_context['popular_cuisines'][:5])}
        - Use food emojis appropriately 🍽️ 🥘 ☕ 🍰
        - Mention air conditioning and indoor seating (important due to heat)
        - Family sections and private dining areas are valued
        - Include price ranges in KWD when appropriate
        """
        
        base_prompt += f"""
        
        Platform specifications for {platform}:
        - Maximum length: {self.platform_specs[platform]['max_length']} characters
        - Hashtag limit: {self.platform_specs[platform]['hashtag_limit']}
        - Best practices: {self.platform_specs[platform]['best_practices']}
        
        Write in a {tone} tone.
        """
        
        return base_prompt
        
    def _build_user_prompt(self, prompt: str, platform: str, additional_context: Optional[Dict]) -> str:
        """Build user prompt with context"""
        user_prompt = f"Create a {platform} post about: {prompt}"
        
        if additional_context:
            if 'target_audience' in additional_context:
                user_prompt += f"\nTarget audience: {additional_context['target_audience']}"
            if 'campaign_goal' in additional_context:
                user_prompt += f"\nCampaign goal: {additional_context['campaign_goal']}"
            if 'key_message' in additional_context:
                user_prompt += f"\nKey message: {additional_context['key_message']}"
                
        return user_prompt
        
    def _generate_with_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Generate content using OpenAI GPT-4 Turbo"""
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Latest GPT-4 Turbo
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2000,  # Increased for better responses
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
        
    def _generate_with_claude(self, system_prompt: str, user_prompt: str) -> str:
        """Generate content using Claude 3.5 Sonnet (Latest)"""
        response = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Updated to latest model
            max_tokens=2000,  # Increased for better responses
            temperature=0.8,  # Better for creative content
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return response.content[0].text.strip()
        
    def _get_platform_recommendations(self, platform: str, content: str) -> List[str]:
        """Get platform-specific recommendations"""
        recommendations = []
        
        if platform == 'instagram':
            recommendations.append("Add high-quality images or videos")
            recommendations.append("Consider creating a Reel for higher engagement")
            recommendations.append("Use Instagram Stories to tease the post")
        elif platform == 'twitter':
            if len(content) > 200:
                recommendations.append("Consider creating a thread for detailed content")
            recommendations.append("Add relevant GIFs or images")
            recommendations.append("Engage with replies promptly")
        elif platform == 'snapchat':
            recommendations.append("Use vertical format for better viewing")
            recommendations.append("Add location-based geofilters")
            recommendations.append("Keep content under 10 seconds")
        elif platform == 'tiktok':
            recommendations.append("Use trending sounds")
            recommendations.append("Keep videos between 15-30 seconds")
            recommendations.append("Add captions for accessibility")
            
        return recommendations
        
    def _get_optimal_posting_times(self, platform: str) -> Dict[str, List[str]]:
        """Get optimal posting times for Kuwait market"""
        # Kuwait-specific optimal times
        optimal_times = {
            'weekdays': {
                'morning': ['8:00 AM - 10:00 AM'],
                'evening': ['6:00 PM - 8:00 PM', '9:00 PM - 11:00 PM']
            },
            'weekends': {
                'morning': ['10:00 AM - 12:00 PM'],
                'evening': ['7:00 PM - 10:00 PM']
            },
            'avoid': ['During prayer times', '2:00 PM - 4:00 PM (siesta time)']
        }
        
        # Platform-specific adjustments
        if platform == 'instagram':
            optimal_times['best_days'] = ['Tuesday', 'Wednesday', 'Thursday']
        elif platform == 'twitter':
            optimal_times['best_days'] = ['Sunday', 'Wednesday']
        elif platform == 'tiktok':
            optimal_times['best_days'] = ['Tuesday', 'Thursday', 'Friday']
            
        return optimal_times
    
    # Agent-powered methods
    def generate_with_agents(self,
                           prompt: str,
                           use_case: str = 'single_post',
                           restaurant_info: Optional[Dict] = None,
                           campaign_info: Optional[Dict] = None,
                           **kwargs) -> Dict:
        """
        Generate content using multi-agent system for complex tasks
        
        Args:
            prompt: Main content request
            use_case: Type of content needed (single_post, weekly_content, campaign, etc.)
            restaurant_info: Restaurant details
            campaign_info: Campaign specific information
            
        Returns:
            Generated content with full campaign/post details
        """
        if not self.agents_enabled:
            # Fallback to regular generation
            return self.generate_content(prompt, **kwargs)
        
        try:
            restaurant_info = restaurant_info or {
                'name': 'Restaurant',
                'cuisine_type': 'general',
                'area': 'Kuwait'
            }
            
            if use_case == 'single_post':
                result = self.content_crew.create_single_post(
                    restaurant_info=restaurant_info,
                    post_type=kwargs.get('post_type', 'regular'),
                    special_requirements=kwargs.get('requirements', [])
                )
            elif use_case == 'weekly_content':
                result = self.content_crew.create_weekly_content(
                    restaurant_info=restaurant_info,
                    week_theme=kwargs.get('theme')
                )
            elif use_case == 'ramadan_campaign':
                result = self.campaign_crew.create_ramadan_campaign(
                    restaurant_info=restaurant_info,
                    budget=kwargs.get('budget'),
                    duration_days=kwargs.get('duration', 30)
                )
            elif use_case == 'product_launch':
                result = self.campaign_crew.create_new_launch_campaign(
                    restaurant_info=restaurant_info,
                    product_info=campaign_info or {'name': 'New Product', 'type': 'dish'},
                    campaign_duration=kwargs.get('duration', 14)
                )
            elif use_case == 'performance_analysis':
                result = self.analytics_crew.analyze_campaign_performance(
                    restaurant_info=restaurant_info,
                    campaign_data=campaign_info or {},
                    comparison_period=kwargs.get('comparison_period')
                )
            else:
                # Default to single post
                result = self.content_crew.create_single_post(
                    restaurant_info=restaurant_info,
                    post_type='regular'
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Agent generation failed: {str(e)}")
            # Fallback to regular generation
            return self.generate_content(prompt, **kwargs)
    
    def analyze_competitors(self, 
                          restaurant_info: Dict,
                          competitors: List[str],
                          time_period: int = 30) -> Dict:
        """Analyze competitive landscape using agent crew"""
        if not self.agents_enabled:
            return {
                'success': False,
                'message': 'Agent framework not available',
                'suggestion': 'Enable agents for competitive analysis'
            }
        
        try:
            return self.analytics_crew.competitive_landscape_analysis(
                restaurant_info=restaurant_info,
                competitors=competitors,
                time_period=time_period
            )
        except Exception as e:
            logger.error(f"Competitive analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_monthly_insights(self,
                           restaurant_info: Dict,
                           month: str,
                           year: int) -> Dict:
        """Get comprehensive monthly performance review"""
        if not self.agents_enabled:
            return {
                'success': False,
                'message': 'Agent framework not available'
            }
        
        try:
            return self.analytics_crew.monthly_performance_review(
                restaurant_info=restaurant_info,
                month=month,
                year=year
            )
        except Exception as e:
            logger.error(f"Monthly review failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _should_use_agents(self, prompt: str, kwargs: Dict) -> bool:
        """Determine if request should use agent system"""
        if not self.agents_enabled:
            return False
        
        # Keywords that trigger agent usage
        agent_triggers = [
            'campaign', 'weekly', 'monthly', 'analyze', 'competitor',
            'comprehensive', 'full', 'complete', 'strategy', 'plan',
            'ramadan', 'launch', 'performance', 'insights'
        ]
        
        # Check prompt for triggers
        prompt_lower = prompt.lower()
        if any(trigger in prompt_lower for trigger in agent_triggers):
            return True
        
        # Check if complex requirements
        if kwargs.get('duration') and kwargs['duration'] > 1:
            return True
        
        if kwargs.get('multiple_posts') or kwargs.get('campaign'):
            return True
        
        return False


# Note: No singleton instance created here
# Use get_ai_service() from services.container instead