"""
AI Content generation routes - New implementation
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
import logging

from models import db, User, Client, Post
from services import get_ai_service
from utils.decorators import client_required

logger = logging.getLogger(__name__)

ai_content_bp = Blueprint('ai_content', __name__, url_prefix='/api/ai')

@ai_content_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_content():
    """
    Generate AI-powered content for social media posts
    
    Expected JSON payload:
    {
        "prompt": "Ramadan special offers for restaurant",
        "platform": "instagram",
        "tone": "enthusiastic",
        "include_arabic": true,
        "include_hashtags": true,
        "business_type": "restaurant",
        "additional_context": {
            "target_audience": "families",
            "campaign_goal": "increase foot traffic"
        }
    }
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role', 'client')
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        # Validate required fields
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
            
        # Extract parameters with defaults
        platform = data.get('platform', 'instagram')
        tone = data.get('tone', 'professional')
        include_arabic = data.get('include_arabic', False)
        include_hashtags = data.get('include_hashtags', True)
        business_type = data.get('business_type')
        additional_context = data.get('additional_context', {})
        
        # Check user limits if client
        if user_role == 'client':
            client = Client.query.filter_by(user_id=current_user_id).first()
            if not client:
                return jsonify({'error': 'Client profile not found'}), 404
                
            # Check monthly limits
            if client.monthly_posts_used >= client.monthly_posts_limit:
                return jsonify({
                    'error': 'Monthly post limit reached',
                    'limit': client.monthly_posts_limit,
                    'used': client.monthly_posts_used
                }), 403
        
        # Generate content using AI service
        # Get AI service instance
        ai_service = get_ai_service()
        result = ai_service.generate_content(
            prompt=prompt,
            platform=platform,
            tone=tone,
            include_arabic=include_arabic,
            include_hashtags=include_hashtags,
            business_type=business_type,
            additional_context=additional_context
        )
        
        # Update usage for clients
        if user_role == 'client':
            client.monthly_posts_used += 1
            client.last_active = datetime.utcnow()
            db.session.commit()
            
            # Add usage info to response
            result['usage'] = {
                'posts_used': client.monthly_posts_used,
                'posts_limit': client.monthly_posts_limit,
                'posts_remaining': client.monthly_posts_limit - client.monthly_posts_used
            }
        
        # Log the generation
        logger.info(f"Content generated for user {current_user_id}, platform: {platform}")
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        return jsonify({'error': 'Failed to generate content', 'message': str(e)}), 500


@ai_content_bp.route('/translate', methods=['POST'])
@jwt_required()
def translate_content():
    """
    Translate content between languages
    
    Expected JSON payload:
    {
        "text": "Hello Kuwait!",
        "source_lang": "en",
        "target_lang": "ar"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        text = data.get('text')
        if not text:
            return jsonify({'error': 'Text is required'}), 400
            
        source_lang = data.get('source_lang', 'en')
        target_lang = data.get('target_lang', 'ar')
        
        # Perform translation
        # Get AI service instance
        ai_service = get_ai_service()
        translated_text = ai_service.translate_content(text, source_lang, target_lang)
        
        return jsonify({
            'success': True,
            'data': {
                'original_text': text,
                'translated_text': translated_text,
                'source_lang': source_lang,
                'target_lang': target_lang
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error translating content: {str(e)}")
        return jsonify({'error': 'Failed to translate content', 'message': str(e)}), 500


@ai_content_bp.route('/hashtags', methods=['POST'])
@jwt_required()
def generate_hashtags():
    """
    Generate hashtag suggestions for content
    
    Expected JSON payload:
    {
        "content": "Check out our new menu items!",
        "platform": "instagram",
        "business_type": "restaurant"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        content = data.get('content')
        if not content:
            return jsonify({'error': 'Content is required'}), 400
            
        platform = data.get('platform', 'instagram')
        business_type = data.get('business_type')
        
        # Generate hashtags
        # Get AI service instance
        ai_service = get_ai_service()
        hashtags = ai_service.generate_hashtags(content, platform, business_type)
        
        # Categorize hashtags by volume (mock data for now)
        categorized_hashtags = {
            'high_volume': [tag for tag in hashtags[:3]],  # First 3 as high volume
            'medium_volume': [tag for tag in hashtags[3:8]],  # Next 5 as medium
            'niche': [tag for tag in hashtags[8:]],  # Rest as niche
            'all': hashtags
        }
        
        return jsonify({
            'success': True,
            'data': {
                'hashtags': categorized_hashtags,
                'total_count': len(hashtags),
                'platform': platform
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating hashtags: {str(e)}")
        return jsonify({'error': 'Failed to generate hashtags', 'message': str(e)}), 500


@ai_content_bp.route('/enhance', methods=['POST'])
@jwt_required()
def enhance_content():
    """
    Enhance existing content for better engagement
    
    Expected JSON payload:
    {
        "content": "Visit our restaurant today",
        "enhancement_type": "engagement"  // grammar, tone, engagement, localization
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        content = data.get('content')
        if not content:
            return jsonify({'error': 'Content is required'}), 400
            
        enhancement_type = data.get('enhancement_type', 'grammar')
        
        # Validate enhancement type
        valid_types = ['grammar', 'tone', 'engagement', 'localization']
        if enhancement_type not in valid_types:
            return jsonify({'error': f'Invalid enhancement type. Choose from: {", ".join(valid_types)}'}), 400
        
        # Enhance content
        # Get AI service instance
        ai_service = get_ai_service()
        result = ai_service.enhance_content(content, enhancement_type)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error enhancing content: {str(e)}")
        return jsonify({'error': 'Failed to enhance content', 'message': str(e)}), 500


@ai_content_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_content_templates():
    """
    Get content templates for different business types and occasions
    """
    try:
        platform = request.args.get('platform', 'instagram')
        business_type = request.args.get('business_type', 'general')
        
        # Template examples - in production, these would come from database
        templates = {
            'restaurant': [
                {
                    'id': 1,
                    'name': 'New Menu Launch',
                    'prompt': 'Announce new menu items with mouth-watering descriptions',
                    'example': '🍽️ Introducing our NEW [Item Name]! Made with [ingredients], this dish brings you [unique selling point]. Limited time only!',
                    'tags': ['product_launch', 'food']
                },
                {
                    'id': 2,
                    'name': 'Ramadan Special',
                    'prompt': 'Ramadan iftar special offers and family meals',
                    'example': '🌙 Ramadan Kareem! Join us for iftar with our special family feast. Book now!',
                    'tags': ['ramadan', 'cultural', 'promotion']
                },
                {
                    'id': 3,
                    'name': 'Weekend Brunch',
                    'prompt': 'Promote weekend brunch with family-friendly atmosphere',
                    'example': '🥞 Weekend Brunch Alert! Join us Friday & Saturday for our all-you-can-eat family brunch. Kids eat free!',
                    'tags': ['weekend', 'brunch', 'family']
                },
                {
                    'id': 4,
                    'name': 'Delivery Promotion',
                    'prompt': 'Highlight delivery service with special offers',
                    'example': '🚗 Too hot outside? We deliver! Order now and get 20% off. Free delivery over 5 KWD!',
                    'tags': ['delivery', 'promotion', 'convenience']
                },
                {
                    'id': 5,
                    'name': 'Chef Special',
                    'prompt': 'Feature chef recommendations and signature dishes',
                    'example': "👨‍🍳 Chef's Special: Try our signature [dish name] - a perfect blend of [flavors]. Available today only!",
                    'tags': ['chef_special', 'signature', 'limited']
                }
            ],
            'cafe': [
                {
                    'id': 6,
                    'name': 'Coffee Morning',
                    'prompt': 'Promote morning coffee and breakfast deals',
                    'example': '☕ Good morning Kuwait! Start your day right with our artisan coffee and fresh pastries. Buy 2 get 1 free before 11 AM!',
                    'tags': ['coffee', 'morning', 'breakfast']
                },
                {
                    'id': 7,
                    'name': 'Dessert Special',
                    'prompt': 'Showcase desserts and sweet treats',
                    'example': '🍰 Sweet tooth calling? Our [dessert name] is the perfect afternoon treat. Made fresh daily!',
                    'tags': ['dessert', 'sweets', 'afternoon']
                }
            ],
            'f&b': [
                {
                    'id': 8,
                    'name': 'Happy Hour',
                    'prompt': 'Announce happy hour deals and timing',
                    'example': '⏰ Happy Hour Alert! 3-6 PM daily. Special prices on selected items. See you there!',
                    'tags': ['happy_hour', 'deals', 'timing']
                },
                {
                    'id': 9,
                    'name': 'Catering Services',
                    'prompt': 'Promote catering for events and gatherings',
                    'example': '🎉 Planning an event? Let us cater! From corporate meetings to family gatherings. Halal certified.',
                    'tags': ['catering', 'events', 'service']
                },
                {
                    'id': 10,
                    'name': 'Seasonal Menu',
                    'prompt': 'Introduce seasonal items and limited-time offers',
                    'example': '🌟 Summer is here! Cool down with our refreshing [item]. Limited time only!',
                    'tags': ['seasonal', 'limited_time', 'summer']
                }
            ],
            'retail': [
                {
                    'id': 3,
                    'name': 'Sale Announcement',
                    'prompt': 'Announce sales and discounts to drive foot traffic',
                    'example': '🛍️ SALE ALERT! Up to [X]% OFF on selected items. This weekend only!',
                    'tags': ['sale', 'promotion']
                },
                {
                    'id': 4,
                    'name': 'New Arrival',
                    'prompt': 'Showcase new product arrivals',
                    'example': '✨ NEW IN! Check out our latest [product category]. Shop now!',
                    'tags': ['product_launch', 'new_arrival']
                }
            ],
            'general': [
                {
                    'id': 5,
                    'name': 'National Day',
                    'prompt': 'Kuwait National Day celebration post',
                    'example': '🇰🇼 Happy National Day Kuwait! Celebrating [X] years of independence.',
                    'tags': ['national_day', 'cultural']
                },
                {
                    'id': 6,
                    'name': 'Customer Appreciation',
                    'prompt': 'Thank customers for their support',
                    'example': '❤️ Thank you for your continued support! We appreciate each one of you.',
                    'tags': ['engagement', 'appreciation']
                }
            ]
        }
        
        # Get templates for requested business type or general
        selected_templates = templates.get(business_type, templates['general'])
        
        return jsonify({
            'success': True,
            'data': {
                'templates': selected_templates,
                'business_type': business_type,
                'platform': platform
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}")
        return jsonify({'error': 'Failed to fetch templates', 'message': str(e)}), 500


@ai_content_bp.route('/trending', methods=['GET'])
@jwt_required()
def get_trending_topics():
    """
    Get trending topics and hashtags for Kuwait
    """
    try:
        # In production, this would fetch from social media APIs or trend databases
        trending_data = {
            'topics': [
                {
                    'topic': 'Hala February',
                    'description': 'Kuwait shopping festival',
                    'relevance': 'high',
                    'hashtags': ['#HalaFebruary', '#هلا_فبراير', '#KuwaitShopping']
                },
                {
                    'topic': 'Kuwait Premier League',
                    'description': 'Local football matches',
                    'relevance': 'medium',
                    'hashtags': ['#KuwaitFootball', '#الدوري_الكويتي']
                },
                {
                    'topic': 'Weekend Getaways',
                    'description': 'Local tourism and staycations',
                    'relevance': 'medium',
                    'hashtags': ['#KuwaitTourism', '#WeekendVibes', '#Q8Travel']
                }
            ],
            'hashtags': {
                'trending_now': ['#Kuwait', '#Q8', '#الكويت', '#KuwaitCity', '#Q8Life'],
                'evergreen': ['#KuwaitBusiness', '#MadeInKuwait', '#Q8Food', '#KuwaitStyle'],
                'seasonal': ['#KuwaitWinter', '#Q8Events']
            },
            'updated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': trending_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching trending topics: {str(e)}")
        return jsonify({'error': 'Failed to fetch trending topics', 'message': str(e)}), 500