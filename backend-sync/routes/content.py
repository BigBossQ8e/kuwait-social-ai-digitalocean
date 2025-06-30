"""
Content management routes for Kuwait Social AI
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from models import db, Post, Client
from services.content_generator import ContentGenerator
from services.image_processor import ImageProcessor
from utils.decorators import client_required
from utils.validators import (
    validate_request, validate_content_for_kuwait, 
    validate_hashtags, validate_file_upload, ContentModerator
)
from schemas import ContentGenerationSchema, TelegramContentSchema
import tempfile

content_bp = Blueprint('content', __name__)

# Initialize services
content_generator = ContentGenerator()
image_processor = ImageProcessor()
content_moderator = ContentModerator()

@content_bp.route('/generate', methods=['POST'])
@jwt_required()
@client_required
@validate_request(ContentGenerationSchema)
def generate_content(validated_data):
    """Generate AI content with validation"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    # Check if AI generation is enabled for client
    client = Client.query.get(client_id)
    if not any(f.name == 'ai_content_generation' for f in client.features if f.platform_enabled):
        return jsonify({'error': 'AI content generation not enabled for your account'}), 403
    
    try:
        # Validate prompt for Kuwait compliance
        content_validation = validate_content_for_kuwait(validated_data['prompt'])
        
        if not content_validation['is_valid']:
            return jsonify({
                'error': 'Content validation failed',
                'issues': content_validation['issues'],
                'suggestions': content_validation['suggestions']
            }), 400
        
        # Generate content
        generated = content_generator.generate_content(
            prompt=validated_data['prompt'],
            include_arabic=validated_data['include_arabic'],
            platform=validated_data['platform'],
            content_type=validated_data['content_type'],
            tone=validated_data['tone'],
            include_hashtags=validated_data['include_hashtags']
        )
        
        # Moderate generated content
        moderation_en = content_moderator.moderate(generated['caption_en'])
        
        if not moderation_en['is_appropriate']:
            # Try to regenerate with cleaner prompt
            cleaned_prompt = f"{validated_data['prompt']}. Ensure content is appropriate for Kuwait market, avoiding any references to: {', '.join(moderation_en['inappropriate_terms'])}"
            
            generated = content_generator.generate_content(
                prompt=cleaned_prompt,
                include_arabic=validated_data['include_arabic'],
                platform=validated_data['platform'],
                content_type=validated_data['content_type'],
                tone=validated_data['tone'],
                include_hashtags=validated_data['include_hashtags']
            )
        
        # Validate hashtags
        if generated.get('hashtags'):
            hashtag_validation = validate_hashtags(generated['hashtags'])
            if hashtag_validation['warnings']:
                generated['warnings'] = hashtag_validation['warnings']
            if hashtag_validation['suggestions']:
                generated['suggestions'] = hashtag_validation['suggestions']
        
        # Add content warnings if any
        if content_validation['warnings']:
            generated['content_warnings'] = content_validation['warnings']
        
        return jsonify({
            'success': True,
            'content': generated,
            'moderation_score': moderation_en['score']
        }), 200
        
    except (ContentGenerationException, TranslationException, AIServiceException) as e:
        # These are expected exceptions with proper error messages
        raise e
    except Exception as e:
        # Unexpected errors - log and wrap
        logging.error(f"Unexpected error in content generation: {str(e)}")
        raise ContentGenerationException(
            "An unexpected error occurred during content generation",
            details={'error': str(e)}
        )

@content_bp.route('/upload-image', methods=['POST'])
@jwt_required()
@client_required
def upload_image():
    """Upload and validate image for post"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file
    file_validation = validate_file_upload(file)
    if not file_validation['is_valid']:
        return jsonify({
            'error': 'File validation failed',
            'issues': file_validation['issues']
        }), 400
    
    try:
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_dir = tempfile.mkdtemp()
        filepath = os.path.join(temp_dir, filename)
        file.save(filepath)
        
        # Process image
        enhance = request.form.get('enhance', 'true').lower() == 'true'
        platform = request.form.get('platform', 'instagram')
        generate_caption = request.form.get('generate_caption', 'false').lower() == 'true'
        
        # Process image with enhancement
        processed = image_processor.process_image(
            filepath,
            enhance=enhance,
            resize_for=platform
        )
        
        result = {
            'success': True,
            'image_url': processed['url'],
            'thumbnail_url': processed.get('thumbnail_url'),
            'dimensions': processed.get('dimensions'),
            'file_size_mb': file_validation['file_size_mb']
        }
        
        # Generate caption if requested
        if generate_caption:
            try:
                caption_data = content_generator.generate_caption_from_image(
                    processed['url'],
                    include_arabic=True,
                    platform=platform
                )
                
                # Validate generated caption
                caption_validation = validate_content_for_kuwait(caption_data['caption_en'])
                if caption_validation['warnings']:
                    caption_data['warnings'] = caption_validation['warnings']
                
                result['generated_caption'] = caption_data
                
            except Exception as e:
                result['caption_error'] = str(e)
        
        # Cleanup
        os.remove(filepath)
        os.rmdir(temp_dir)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': 'Image processing failed', 'details': str(e)}), 500

@content_bp.route('/validate', methods=['POST'])
@jwt_required()
@client_required
def validate_content():
    """Validate content for Kuwait compliance"""
    data = request.get_json()
    
    if not data.get('content'):
        return jsonify({'error': 'Content is required'}), 400
    
    content = data['content']
    content_type = data.get('type', 'caption')
    
    # Validate content
    validation_result = validate_content_for_kuwait(content)
    
    # Moderate content
    moderation_result = content_moderator.moderate(content)
    
    # Validate hashtags if present
    hashtag_validation = None
    if content_type == 'caption' and '#' in content:
        hashtags = [tag for tag in content.split() if tag.startswith('#')]
        if hashtags:
            hashtag_validation = validate_hashtags(hashtags)
    
    # Check scheduled time if provided
    time_validation = None
    if data.get('scheduled_time'):
        try:
            scheduled_dt = datetime.fromisoformat(data['scheduled_time'])
            time_validation = validate_posting_time(scheduled_dt)
        except:
            time_validation = {'is_valid': False, 'issues': ['Invalid datetime format']}
    
    return jsonify({
        'content_validation': validation_result,
        'moderation': moderation_result,
        'hashtag_validation': hashtag_validation,
        'time_validation': time_validation,
        'overall_score': calculate_content_score(validation_result, moderation_result),
        'recommendations': generate_recommendations(validation_result, moderation_result, hashtag_validation)
    }), 200

@content_bp.route('/enhance', methods=['POST'])
@jwt_required()
@client_required
def enhance_content():
    """Enhance existing content with AI"""
    data = request.get_json()
    
    if not data.get('content'):
        return jsonify({'error': 'Content is required'}), 400
    
    original_content = data['content']
    improvements = data.get('improvements', ['engagement', 'hashtags', 'cultural'])
    
    try:
        # Enhance content
        enhanced = content_generator.enhance_content(original_content, improvements)
        
        # Validate enhanced content
        validation = validate_content_for_kuwait(enhanced)
        moderation = content_moderator.moderate(enhanced)
        
        return jsonify({
            'success': True,
            'original': original_content,
            'enhanced': enhanced,
            'validation': validation,
            'moderation_score': moderation['score'],
            'improvements_applied': improvements
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Content enhancement failed', 'details': str(e)}), 500

@content_bp.route('/templates', methods=['GET'])
@jwt_required()
@client_required
def get_content_templates():
    """Get content templates for Kuwait market"""
    category = request.args.get('category', 'all')
    
    templates = {
        'ramadan': [
            {
                'id': 'ramadan_greeting',
                'name': 'Ramadan Greeting',
                'prompt': 'Create a warm Ramadan greeting for our customers in Kuwait',
                'variables': ['business_name', 'special_offer'],
                'example': 'Ramadan Mubarak from [business_name]! Enjoy [special_offer] throughout the holy month.'
            },
            {
                'id': 'iftar_promotion',
                'name': 'Iftar Promotion',
                'prompt': 'Announce special Iftar offers for Kuwait families',
                'variables': ['restaurant_name', 'discount', 'timing'],
                'example': 'Break your fast at [restaurant_name]! [discount]% off Iftar buffet from [timing].'
            }
        ],
        'national_day': [
            {
                'id': 'kuwait_national_day',
                'name': 'Kuwait National Day',
                'prompt': 'Create patriotic content for Kuwait National Day celebration',
                'variables': ['business_name', 'offer'],
                'example': 'Celebrating Kuwait with pride! 🇰🇼 [business_name] offers [offer] this National Day!'
            }
        ],
        'general': [
            {
                'id': 'new_product',
                'name': 'New Product Launch',
                'prompt': 'Announce new product arrival for Kuwait market',
                'variables': ['product_name', 'features', 'price'],
                'example': 'Introducing [product_name]! Features: [features]. Starting at [price] KWD.'
            }
        ]
    }
    
    if category != 'all':
        templates = {category: templates.get(category, [])}
    
    return jsonify({'templates': templates}), 200

@content_bp.route('/telegram/process', methods=['POST'])
@jwt_required()
@client_required
@validate_request(TelegramContentSchema)
def process_telegram_content(validated_data):
    """Process content received from Telegram bot"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    try:
        result = {}
        
        if validated_data['message_type'] == 'voice':
            # Voice message already converted to text by Telegram bot
            prompt = validated_data['content']
            
        elif validated_data['message_type'] == 'text':
            prompt = validated_data['content']
            
        elif validated_data['message_type'] == 'image':
            # Process image URL
            image_url = validated_data['content']
            caption_data = content_generator.generate_caption_from_image(
                image_url,
                include_arabic=True,
                platform=validated_data['platform']
            )
            result['caption'] = caption_data
            return jsonify({'success': True, 'result': result}), 200
            
        else:
            return jsonify({'error': 'Unsupported message type'}), 400
        
        # Generate content from text/voice
        generated = content_generator.generate_content(
            prompt=prompt,
            include_arabic=True,
            platform=validated_data['platform'],
            tone='casual'  # More casual for Telegram
        )
        
        # Validate content
        validation = validate_content_for_kuwait(generated['caption_en'])
        
        result = {
            'content': generated,
            'validation': validation,
            'platform': validated_data['platform']
        }
        
        return jsonify({'success': True, 'result': result}), 200
        
    except Exception as e:
        return jsonify({'error': 'Processing failed', 'details': str(e)}), 500

# Helper functions
def calculate_content_score(validation_result, moderation_result):
    """Calculate overall content quality score"""
    score = 100
    
    # Deduct for validation issues
    score -= len(validation_result.get('issues', [])) * 10
    score -= len(validation_result.get('warnings', [])) * 5
    
    # Add moderation score
    score += moderation_result.get('score', 0) * 5
    
    # Ensure score is between 0 and 100
    return max(0, min(100, score))

def generate_recommendations(validation_result, moderation_result, hashtag_validation):
    """Generate content improvement recommendations"""
    recommendations = []
    
    # From validation
    if validation_result.get('suggestions'):
        recommendations.extend(validation_result['suggestions'])
    
    # From moderation
    if moderation_result.get('recommendation'):
        recommendations.append(moderation_result['recommendation'])
    
    # From hashtags
    if hashtag_validation and hashtag_validation.get('suggestions'):
        recommendations.extend(hashtag_validation['suggestions'])
    
    # General recommendations
    if not moderation_result.get('positive_terms'):
        recommendations.append('Consider adding positive terms like: halal, family, quality, authentic')
    
    return recommendations