"""
AI Content Generation Service for Kuwait Social AI
"""

from openai import OpenAI
import os
from typing import Dict, List, Optional
import json
from datetime import datetime
from deep_translator import GoogleTranslator
import re
import logging
from exceptions import (
    KuwaitSocialAIException, ContentGenerationException, TranslationException, 
    AIServiceException, ContentModerationException
)
from config.platform_config import PlatformConfig

class ContentGenerator:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise AIServiceException(service='OpenAI', reason='API key not configured')
        
        # Initialize OpenAI client with the new approach
        self.client = OpenAI(api_key=self.api_key)
        # Initialize deep-translator for more reliable translation
        self.translator = GoogleTranslator(source='en', target='ar')
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = PlatformConfig
        
        # Kuwait-specific context from config
        self.kuwait_context = {
            'culture': 'Islamic, Arabic, family-oriented',
            'language': 'Arabic (primary), English (widely spoken)',
            'business_hours': f"{self.config.KUWAIT_SETTINGS['business_days'][0]}-{self.config.KUWAIT_SETTINGS['business_days'][-1]}",
            'prayer_times': list(self.config.KUWAIT_SETTINGS['prayer_times'].keys()),
            'special_considerations': [
                'Ramadan timing adjustments',
                'Friday prayer considerations',
                'Conservative content guidelines',
                'Local holidays and celebrations'
            ]
        }
    
    def generate_content(
        self, 
        prompt: str, 
        include_arabic: bool = True,
        platform: str = 'instagram',
        content_type: str = 'post',
        tone: str = 'professional',
        include_hashtags: bool = True
    ) -> Dict:
        """Generate social media content using AI"""
        
        try:
            # Build system prompt with Kuwait context
            system_prompt = self._build_system_prompt(platform, content_type, tone)
            
            # Generate content using the new client approach
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            generated_text = response.choices[0].message.content
            
            # Parse the response
            content = self._parse_ai_response(generated_text)
            
            # Content moderation with retry
            moderation_passed = self._moderate_content_with_retry(content.get('caption_en', ''))
            if not moderation_passed:
                raise ContentModerationException(
                    "Content failed moderation check after retry",
                    content=content.get('caption_en', ''),
                    details={'retry_attempted': True}
                )
            
            # Generate Arabic version if requested
            if include_arabic and not content.get('caption_ar'):
                # Use graceful fallback for translation
                translated = self._translate_to_arabic(content['caption_en'], fallback_on_error=True)
                if translated:
                    content['caption_ar'] = translated
                else:
                    # Translation failed but we continue with the request
                    self.logger.warning("Translation to Arabic failed - continuing without Arabic version")
                    content['caption_ar'] = None
                    content['translation_warning'] = {
                        'message': 'Arabic translation temporarily unavailable',
                        'suggestion': 'Content delivered in English only'
                    }
            
            # Generate hashtags if not included
            if include_hashtags and not content.get('hashtags'):
                try:
                    content['hashtags'] = self._generate_hashtags(prompt, platform)
                except Exception as e:
                    self.logger.warning(f"Hashtag generation failed: {str(e)}")
                    # Provide default hashtags instead of failing
                    content['hashtags'] = ['#Kuwait', '#الكويت', '#Q8']
                    content['hashtag_error'] = {
                        'message': 'Using default hashtags',
                        'reason': str(e)
                    }
            
            # Add metadata
            content['metadata'] = {
                'generated_at': datetime.utcnow().isoformat(),
                'platform': platform,
                'ai_model': 'gpt-4',
                'tone': tone
            }
            
            return content
            
        except Exception as e:
            # If it's already a KuwaitSocialAIException, re-raise it
            if isinstance(e, KuwaitSocialAIException):
                raise e
            elif hasattr(e, '__class__') and 'openai' in str(e.__class__):
                self.logger.error(f"OpenAI API error: {str(e)}")
                raise AIServiceException(service='OpenAI', reason=str(e))
            else:
                self.logger.error(f"Unexpected error in content generation: {str(e)}")
                raise ContentGenerationException(
                    "Content generation failed",
                    details={'error': str(e)}
                )
    
    def generate_caption_from_image(
        self, 
        image_url: str,
        include_arabic: bool = True,
        platform: str = 'instagram'
    ) -> Dict:
        """Generate caption from image using Vision API"""
        
        try:
            # Use GPT-4 Vision to analyze image with the new client approach
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a social media expert creating captions for Kuwait-based businesses. Create engaging captions that are culturally appropriate for Kuwait."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Create a {platform} caption for this image. Include relevant hashtags."
                            },
                            {
                                "type": "image_url",
                                "image_url": image_url
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            caption_text = response.choices[0].message.content
            
            # Parse and structure the response
            content = self._parse_caption_response(caption_text)
            
            # Add Arabic translation if requested
            if include_arabic:
                # Use graceful fallback for translation
                translated = self._translate_to_arabic(content['caption_en'], fallback_on_error=True)
                if translated:
                    content['caption_ar'] = translated
                else:
                    # Translation failed but we continue with the request
                    self.logger.warning("Translation failed for image caption - continuing without Arabic version")
                    content['caption_ar'] = None
                    content['translation_warning'] = {
                        'message': 'Arabic translation temporarily unavailable',
                        'suggestion': 'Content delivered in English only'
                    }
            
            return content
            
        except Exception as e:
            # If it's already a KuwaitSocialAIException, re-raise it
            if isinstance(e, KuwaitSocialAIException):
                raise e
            elif hasattr(e, '__class__') and 'openai' in str(e.__class__):
                self.logger.error(f"OpenAI Vision API error: {str(e)}")
                raise AIServiceException(service='OpenAI Vision', reason=str(e))
            else:
                self.logger.error(f"Unexpected error in image caption generation: {str(e)}")
                raise ContentGenerationException(
                    "Image caption generation failed",
                    error_code='IMAGE_CAPTION_FAILED',
                    details={'error': str(e), 'image_url': image_url}
                )
    
    def enhance_content(self, original_content: str, improvements: List[str]) -> str:
        """Enhance existing content with specific improvements"""
        
        improvement_prompts = {
            'engagement': 'Add engaging questions or calls-to-action',
            'hashtags': 'Suggest relevant hashtags for Kuwait market',
            'emoji': 'Add appropriate emojis to make it more visually appealing',
            'cultural': 'Ensure cultural appropriateness for Kuwait audience',
            'length': 'Optimize length for the platform'
        }
        
        prompt = f"Improve this social media caption:\n\n{original_content}\n\nImprovements needed:\n"
        for improvement in improvements:
            if improvement in improvement_prompts:
                prompt += f"- {improvement_prompts[improvement]}\n"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a social media expert specializing in Kuwait market."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Content enhancement failed: {str(e)}")
    
    def generate_campaign_ideas(self, business_type: str, occasion: str = None) -> List[Dict]:
        """Generate campaign ideas for Kuwait businesses"""
        
        prompt = f"Generate 5 social media campaign ideas for a {business_type} in Kuwait."
        if occasion:
            prompt += f" Focus on {occasion}."
        prompt += " Consider local culture, trends, and consumer behavior."
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a marketing strategist specializing in Kuwait market. Generate creative, culturally appropriate campaign ideas."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.8
            )
            
            ideas_text = response.choices[0].message.content
            return self._parse_campaign_ideas(ideas_text)
            
        except Exception as e:
            raise Exception(f"Campaign idea generation failed: {str(e)}")
    
    def _build_system_prompt(self, platform: str, content_type: str, tone: str) -> str:
        """Build system prompt with Kuwait context"""
        
        # Get platform limits from config
        caption_limit = self.config.get_platform_limit(
            platform, 'caption_max_length', 2000
        )
        hashtag_limit = self.config.get_platform_limit(
            platform, 'hashtag_max_count', 30
        )
        
        return f"""You are a social media content expert specializing in the Kuwait market.
        
Create {content_type} content for {platform} with these guidelines:
- Tone: {tone}
- Character limit: {caption_limit}
- Hashtag limit: {hashtag_limit}
- Cultural context: {json.dumps(self.kuwait_context)}

Kuwait-specific requirements:
1. Be respectful of Islamic values and local customs
2. Consider prayer times and business hours (Sunday-Thursday)
3. Use bilingual approach when appropriate (Arabic/English)
4. Reference local landmarks, culture, or events when relevant
5. Avoid content that might be considered inappropriate in Kuwait

Format your response as:
Caption: [English caption]
Hashtags: [comma-separated hashtags]
"""
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response into structured format"""
        
        content = {
            'caption_en': '',
            'hashtags': [],
            'suggestions': []
        }
        
        # Extract caption
        caption_match = re.search(r'Caption:\s*(.+?)(?=Hashtags:|$)', response_text, re.DOTALL)
        if caption_match:
            content['caption_en'] = caption_match.group(1).strip()
        
        # Extract hashtags
        hashtags_match = re.search(r'Hashtags:\s*(.+?)(?=Suggestions:|$)', response_text, re.DOTALL)
        if hashtags_match:
            hashtags_text = hashtags_match.group(1).strip()
            # Clean and format hashtags
            hashtags = [tag.strip() for tag in hashtags_text.replace('#', '').split(',')]
            content['hashtags'] = ['#' + tag.replace(' ', '') for tag in hashtags if tag]
        
        return content
    
    def _translate_to_arabic(self, text: str, fallback_on_error: bool = True) -> Optional[str]:
        """Translate English text to Arabic with graceful fallback"""
        from exceptions import TranslationException
        
        attempted_services = []
        
        # First attempt: Google Translate via deep-translator
        try:
            attempted_services.append('Google Translate')
            # Use deep-translator for more reliable translation
            translated_text = self.translator.translate(text)
            if translated_text:
                return translated_text
        except Exception as e:
            # Log the error for debugging
            self.logger.warning(f"Google Translate failed: {str(e)}")
        
        # Second attempt: OpenAI GPT-4
        try:
            attempted_services.append('OpenAI GPT-4')
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator. Translate the following English text to Kuwaiti Arabic dialect, maintaining the marketing tone."
                    },
                    {"role": "user", "content": text}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content
            if translated_text:
                return translated_text
                
        except Exception as e:
            # Log the error for debugging
            self.logger.error(f"OpenAI translation failed: {str(e)}")
        
        # If both services fail and fallback is enabled, return None
        # Otherwise raise exception
        if fallback_on_error:
            self.logger.error(f"All translation services failed. Attempted: {attempted_services}")
            return None
        else:
            raise TranslationException(
                source_lang='en',
                target_lang='ar',
                original_text=text,
                attempted_services=attempted_services
            )
    
    def _generate_hashtags(self, content: str, platform: str) -> List[str]:
        """Generate relevant hashtags"""
        
        prompt = f"""Generate hashtags for this content on {platform} for Kuwait market:
        {content}
        
        Include:
        - General Kuwait hashtags
        - Industry-specific hashtags
        - Trending local hashtags
        - Arabic hashtags
        
        Return 15-20 hashtags."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a hashtag expert for Kuwait social media."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            hashtags_text = response.choices[0].message.content
            hashtags = re.findall(r'#\w+', hashtags_text)
            
            # Add default Kuwait hashtags if not present
            default_tags = ['#Kuwait', '#الكويت', '#Q8', '#KuwaitBusiness']
            for tag in default_tags:
                if tag not in hashtags and len(hashtags) < 20:
                    hashtags.append(tag)
            
            return hashtags[:20]  # Limit to 20 hashtags
            
        except:
            return ['#Kuwait', '#الكويت', '#Q8']
    
    def _parse_caption_response(self, response_text: str) -> Dict:
        """Parse caption response from vision API"""
        
        # Extract hashtags from the response
        hashtags = re.findall(r'#\w+', response_text)
        
        # Remove hashtags from caption
        caption = response_text
        for hashtag in hashtags:
            caption = caption.replace(hashtag, '')
        
        return {
            'caption_en': caption.strip(),
            'hashtags': hashtags[:20]  # Limit hashtags
        }
    
    def _parse_campaign_ideas(self, ideas_text: str) -> List[Dict]:
        """Parse campaign ideas into structured format"""
        
        ideas = []
        
        # Split by numbers (1., 2., etc.)
        idea_blocks = re.split(r'\d+\.', ideas_text)[1:]  # Skip first empty element
        
        for i, block in enumerate(idea_blocks):
            if block.strip():
                lines = block.strip().split('\n')
                title = lines[0].strip() if lines else f"Campaign Idea {i+1}"
                description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""
                
                ideas.append({
                    'title': title,
                    'description': description,
                    'id': i + 1
                })
        
        return ideas
    
    def _moderate_content_with_retry(self, content: str, max_retries: int = 2) -> bool:
        """
        Moderate content with retry logic
        Returns True if content passes moderation, False otherwise
        """
        for attempt in range(max_retries + 1):
            try:
                # Use OpenAI moderation API
                moderation_response = self.client.moderations.create(input=content)
                
                # Check if content is flagged
                is_flagged = moderation_response.results[0].flagged
                
                if not is_flagged:
                    return True
                
                # Log the moderation failure
                categories = moderation_response.results[0].categories
                flagged_categories = [cat for cat, flagged in categories.dict().items() if flagged]
                
                self.logger.warning(
                    f"Content moderation failed (attempt {attempt + 1}/{max_retries + 1}). "
                    f"Flagged categories: {flagged_categories}"
                )
                
                # If this is not the last attempt, continue to retry
                if attempt < max_retries:
                    continue
                else:
                    # Final attempt failed
                    return False
                    
            except Exception as e:
                self.logger.error(f"Content moderation error (attempt {attempt + 1}): {str(e)}")
                
                # If it's the last attempt, fail
                if attempt >= max_retries:
                    return False
                    
                # Otherwise, continue to next attempt
                continue
        
        return False
    
    def _moderate_content_advanced(self, content: str) -> Dict:
        """
        Advanced content moderation including Kuwait-specific rules
        """
        try:
            # OpenAI moderation
            moderation_response = self.client.moderations.create(input=content)
            base_result = moderation_response.results[0]
            
            # Kuwait-specific moderation
            from utils.validators import ContentModerator
            moderator = ContentModerator()
            kuwait_result = moderator.moderate(content)
            
            # Combine results
            is_appropriate = not base_result.flagged and kuwait_result['is_appropriate']
            
            result = {
                'is_appropriate': is_appropriate,
                'openai_flagged': base_result.flagged,
                'kuwait_appropriate': kuwait_result['is_appropriate'],
                'score': kuwait_result.get('score', 0),
                'issues': [],
                'suggestions': []
            }
            
            if base_result.flagged:
                categories = base_result.categories
                flagged_categories = [cat for cat, flagged in categories.dict().items() if flagged]
                result['issues'].extend([f"OpenAI flagged: {cat}" for cat in flagged_categories])
            
            if not kuwait_result['is_appropriate']:
                result['issues'].extend([
                    f"Kuwait moderation: {term}" for term in kuwait_result.get('inappropriate_terms', [])
                ])
                result['suggestions'].append(kuwait_result.get('recommendation', ''))
            
            return result
            
        except Exception as e:
            self.logger.error(f"Advanced moderation failed: {str(e)}")
            # Fallback to basic check
            return {
                'is_appropriate': True,  # Fail open for availability
                'error': str(e),
                'fallback_used': True
            }