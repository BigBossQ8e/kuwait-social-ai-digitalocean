"""
Enhanced content generation routes for F&B templates
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime
import json
from extensions import db
from models import Post, Client
from services.content_generator import ContentGenerator
from utils.decorators import client_required

content_enhanced_bp = Blueprint('content_enhanced', __name__)

# F&B template structures
TEMPLATE_STRUCTURES = {
    "ultimate-craving": {
        "structure": [
            "headline",  # Attention-grabbing question
            "sensory",   # Sensory details (sight, smell, texture)
            "cta"        # Direct and urgent call-to-action
        ],
        "tone": "exciting, sensory-focused",
        "emoji_style": "food-focused"
    },
    "social-gathering": {
        "structure": [
            "headline_arabic",  # Focus on togetherness with Arabic phrases
            "sharing",         # Emphasize dishes for sharing
            "booking"         # Pre-ordering or booking CTA
        ],
        "tone": "warm, family-oriented",
        "emoji_style": "family-friendly"
    },
    "ramadan-greeting": {
        "structure": [
            "greeting_arabic",  # Traditional Arabic greeting
            "offering",        # Respectful announcement
            "booking_info"     # Timings and booking
        ],
        "tone": "respectful, traditional",
        "emoji_style": "minimal, respectful"
    }
}

# Enhanced hashtag recommendations based on context
def get_contextual_hashtags(template_id, cuisine_type=None, location=None, language='en'):
    """Get contextual hashtags based on template and parameters"""
    hashtags = []
    
    # Always include tier 1 hashtags
    tier1 = ["#مطاعم_الكويت", "#الكويت", "#اكل_كويتي", "#foodie", "#kuwaitfood"]
    hashtags.extend(tier1[:3])  # Top 3 general hashtags
    
    # Template-specific hashtags
    template_hashtags = {
        "friday-lunch": ["#جمعة_أهل", "#يمعة_اهل", "#fridaylunch"],
        "dewaniya-platter": ["#ديوانية", "#زوارة", "#latenightkw"],
        "office-lunch": ["#غداء_عمل", "#quicklunch", "#kuwaitoffice"],
        "habbah-of-month": ["#ترند_الكويت", "#musttry", "#kuwaittrending"],
        "ramadan-offer": ["#فطور_رمضان", "#غبقة", "#سحور_رمضان", "#ramadankw"],
        "national-day": ["#هلا_فبراير", "#العيد_الوطني_الكويتي", "#kuwaitnationalday"],
        "ingredient-spotlight": ["#مكونات_طازجة", "#freshingredients", "#qualityfood"],
        "how-its-made": ["#behindthescenes", "#foodprep", "#كواليس_المطبخ"]
    }
    
    if template_id in template_hashtags:
        hashtags.extend(template_hashtags[template_id][:2])
    
    # Cuisine-specific hashtags
    if cuisine_type:
        cuisine_hashtags = {
            "burger": ["#برجر_الكويت", "#burgerkuwait"],
            "pasta": ["#باستا_الكويت", "#pastakuwait"],
            "coffee": ["#قهوة_مختصة", "#specialtycoffeekw"],
            "arabic": ["#اكل_عربي", "#arabicfood"],
            "indian": ["#مطعم_هندي", "#indianfoodkw"],
            "italian": ["#ايطالي", "#italianfoodkw"]
        }
        if cuisine_type in cuisine_hashtags:
            hashtags.extend(cuisine_hashtags[cuisine_type])
    
    # Location hashtags
    if location:
        location_hashtags = {
            "salmiya": ["#السالمية", "#salmiya"],
            "sharq": ["#شرق", "#sharq"],
            "avenues": ["#مجمع_الافنيوز", "#theavenues"],
            "kuwait_city": ["#مدينة_الكويت", "#kuwaitcity"]
        }
        location_key = location.lower().replace(' ', '_')
        if location_key in location_hashtags:
            hashtags.append(location_hashtags[location_key][0])
    
    return list(dict.fromkeys(hashtags))  # Remove duplicates while preserving order

@content_enhanced_bp.route('/generate', methods=['POST'])
@jwt_required()
@client_required
def generate_fb_content():
    """Generate F&B content with enhanced templates"""
    data = request.get_json()
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    # Get template details
    template_id = data.get('template_id')
    template_type = data.get('template_type', 'social-gathering')
    prompt = data.get('prompt')
    
    # Context parameters
    restaurant_context = data.get('restaurant_context', '')
    target_audience = data.get('target_audience', 'families')
    posting_time = data.get('posting_time', 'dinner')
    language = data.get('language', 'en')
    selected_hashtags = data.get('hashtags', [])
    include_emojis = data.get('include_emojis', True)
    include_cta = data.get('include_cta', True)
    visual_cue = data.get('visual_cue', '')
    
    # Build enhanced prompt with F&B context
    enhanced_prompt = f"""
    Create a social media post for a restaurant in Kuwait.
    
    Template Type: {template_type}
    Base Request: {prompt}
    Restaurant Context: {restaurant_context}
    Target Audience: {target_audience}
    Posting Time: {posting_time}
    Language: {language}
    
    Content Structure Requirements:
    {json.dumps(TEMPLATE_STRUCTURES.get(template_type, {}), indent=2)}
    
    Visual Suggestion to mention: {visual_cue}
    
    Additional Requirements:
    - Include emojis: {include_emojis}
    - Include call-to-action: {include_cta}
    - If language is 'ar' or 'both', include Arabic text
    - For 'both', provide English followed by Arabic
    - Make it Instagram-optimized (engaging, visual-focused)
    - Consider Kuwait culture and dining preferences
    - If it's a Ramadan template, include appropriate greetings
    - For National Day, include patriotic elements
    """
    
    try:
        # Initialize content generator
        generator = ContentGenerator()
        
        # Generate content with the enhanced prompt
        generated_content = generator.generate_content(
            prompt=enhanced_prompt,
            platform='instagram',
            tone=TEMPLATE_STRUCTURES.get(template_type, {}).get('tone', 'friendly'),
            include_hashtags=False  # We'll add our curated hashtags
        )
        
        # Add contextual hashtags
        if selected_hashtags:
            # Use user-selected hashtags
            hashtags = selected_hashtags
        else:
            # Auto-generate contextual hashtags
            cuisine_type = _extract_cuisine_type(restaurant_context, prompt)
            location = _extract_location(restaurant_context)
            hashtags = get_contextual_hashtags(template_id, cuisine_type, location, language)
        
        # Combine content with hashtags
        final_content = generated_content
        if hashtags:
            final_content += "\n\n" + " ".join(hashtags)
        
        # Save as draft post
        post = Post(
            client_id=client_id,
            content=final_content,
            platform='instagram',
            status='draft',
            created_at=datetime.utcnow(),
            metadata={
                'template_id': template_id,
                'template_type': template_type,
                'target_audience': target_audience,
                'posting_time': posting_time,
                'language': language,
                'visual_cue': visual_cue
            }
        )
        db.session.add(post)
        db.session.commit()
        
        # Prepare response with additional insights
        response = {
            'success': True,
            'content': final_content,
            'post_id': post.id,
            'hashtags': hashtags,
            'visual_suggestion': visual_cue,
            'optimal_posting_time': _get_optimal_time(posting_time),
            'content_tips': _get_content_tips(template_type, target_audience),
            'character_count': len(final_content),
            'estimated_reach': _estimate_reach(target_audience, len(hashtags))
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Content generation failed',
            'message': str(e)
        }), 500

@content_enhanced_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_fb_templates():
    """Get all available F&B templates"""
    # This would typically come from a database
    templates = {
        "Dish Promotion": [
            {
                "id": "friday-lunch",
                "title": "Friday Lunch Special",
                "description": "Generate a caption for a Friday family gathering dish",
                "optimal_time": "11:00 AM - 1:00 PM",
                "estimated_engagement": "High"
            },
            {
                "id": "dewaniya-platter",
                "title": "Dewaniya Platter",
                "description": "Create an exciting post for late-night gatherings",
                "optimal_time": "After 10:00 PM",
                "estimated_engagement": "Very High"
            },
            {
                "id": "office-lunch",
                "title": "Quick Office Lunch",
                "description": "Write a concise post for busy professionals",
                "optimal_time": "11:00 AM - 1:00 PM",
                "estimated_engagement": "Medium"
            },
            {
                "id": "habbah-of-month",
                "title": "Habbah of the Month",
                "description": "Generate hype for a new trendy item",
                "optimal_time": "4:00 PM - 6:00 PM",
                "estimated_engagement": "Very High"
            }
        ],
        "Special Offers & Events": [
            {
                "id": "ramadan-offer",
                "title": "Ramadan Offer",
                "description": "Draft a post for Iftar, Suhoor, or Ghabga menu",
                "optimal_time": "2-3 hours before Maghrib",
                "estimated_engagement": "Very High"
            },
            {
                "id": "national-day",
                "title": "National Day Special",
                "description": "Create a celebratory post for National & Liberation Day",
                "optimal_time": "All Day",
                "estimated_engagement": "High"
            },
            {
                "id": "new-branch",
                "title": "New Branch Opening",
                "description": "Announce a new location with excitement",
                "optimal_time": "All Day",
                "estimated_engagement": "High"
            }
        ],
        "Engagement & Behind the Scenes": [
            {
                "id": "ingredient-spotlight",
                "title": "Ingredient Spotlight",
                "description": "Focus on fresh, high-quality ingredients",
                "optimal_time": "6:30 PM - 9:00 PM",
                "estimated_engagement": "Medium"
            },
            {
                "id": "how-its-made",
                "title": "How It's Made",
                "description": "Create a script for a 'making-of' video",
                "optimal_time": "6:30 PM - 9:00 PM",
                "estimated_engagement": "Very High"
            },
            {
                "id": "ask-audience",
                "title": "Ask The Audience",
                "description": "Boost engagement with interactive questions",
                "optimal_time": "4:00 PM - 6:00 PM",
                "estimated_engagement": "High"
            }
        ]
    }
    
    return jsonify(templates), 200

@content_enhanced_bp.route('/hashtag-suggestions', methods=['POST'])
@jwt_required()
@client_required
def get_hashtag_suggestions():
    """Get hashtag suggestions based on content"""
    data = request.get_json()
    content = data.get('content', '')
    template_id = data.get('template_id')
    restaurant_type = data.get('restaurant_type')
    location = data.get('location')
    
    suggestions = {
        'recommended': get_contextual_hashtags(template_id, restaurant_type, location),
        'trending': [
            "#الكويت_تاكل", "#kuwaitfoodiesq8", "#q8food",
            "#kuwaitrestaurants", "#مطاعم_جديدة"
        ],
        'performance_data': {
            '#مطاعم_الكويت': {'usage': 125000, 'engagement': '4.2%'},
            '#الكويت': {'usage': 500000, 'engagement': '3.1%'},
            '#kuwaitfood': {'usage': 98000, 'engagement': '3.8%'}
        }
    }
    
    return jsonify(suggestions), 200

# Helper functions
def _extract_cuisine_type(context, prompt):
    """Extract cuisine type from context and prompt"""
    text = (context + " " + prompt).lower()
    
    cuisine_keywords = {
        'burger': ['burger', 'beef', 'برجر', 'برغر'],
        'pasta': ['pasta', 'italian', 'pizza', 'باستا', 'ايطالي'],
        'coffee': ['coffee', 'latte', 'cappuccino', 'قهوة', 'كافيه'],
        'arabic': ['arabic', 'majboos', 'machboos', 'عربي', 'مجبوس'],
        'indian': ['indian', 'curry', 'biryani', 'هندي', 'برياني']
    }
    
    for cuisine, keywords in cuisine_keywords.items():
        if any(keyword in text for keyword in keywords):
            return cuisine
    
    return None

def _extract_location(context):
    """Extract location from context"""
    text = context.lower()
    
    locations = ['salmiya', 'sharq', 'avenues', 'kuwait city', 'hawalli', 
                 'السالمية', 'شرق', 'الافنيوز', 'حولي']
    
    for location in locations:
        if location in text:
            return location.replace('ال', '').strip()
    
    return None

def _get_optimal_time(posting_time):
    """Get optimal posting time with details"""
    optimal_times = {
        'breakfast': '7:30 AM - Best for morning commuters',
        'lunch': '12:30 PM - Peak lunch decision time',
        'afternoon': '4:30 PM - Coffee break time',
        'dinner': '7:30 PM - Prime dinner planning time',
        'late-night': '10:30 PM - Dewaniya gathering time',
        'iftar': '30 minutes before Maghrib prayer',
        'ghabga': '9:30 PM - Post-Iftar social time',
        'suhoor': '12:30 AM - Late night meal planning'
    }
    
    return optimal_times.get(posting_time, '7:30 PM - General best time')

def _get_content_tips(template_type, target_audience):
    """Get content tips based on template and audience"""
    tips = []
    
    # Template-specific tips
    if template_type == 'ultimate-craving':
        tips.extend([
            'Focus on close-up shots showing texture',
            'Include action shots (cheese pulls, sizzling)',
            'Use words that trigger senses'
        ])
    elif template_type == 'social-gathering':
        tips.extend([
            'Show multiple hands reaching for food',
            'Include group dining setup',
            'Emphasize portion sizes for sharing'
        ])
    elif template_type == 'ramadan-greeting':
        tips.extend([
            'Use elegant, respectful imagery',
            'Include traditional elements',
            'Show complete Iftar spread'
        ])
    
    # Audience-specific tips
    if target_audience == 'families':
        tips.append('Highlight kid-friendly options')
    elif target_audience == 'youth':
        tips.append('Use trendy presentation styles')
    elif target_audience == 'professionals':
        tips.append('Emphasize quick service and quality')
    
    return tips

def _estimate_reach(target_audience, hashtag_count):
    """Estimate potential reach based on audience and hashtags"""
    base_reach = {
        'families': 5000,
        'youth': 8000,
        'professionals': 4000,
        'tourists': 3000,
        'all': 6000
    }
    
    # Each relevant hashtag adds 10-15% reach
    hashtag_multiplier = 1 + (hashtag_count * 0.12)
    
    estimated = int(base_reach.get(target_audience, 5000) * hashtag_multiplier)
    
    return {
        'min': int(estimated * 0.8),
        'max': int(estimated * 1.3),
        'average': estimated
    }