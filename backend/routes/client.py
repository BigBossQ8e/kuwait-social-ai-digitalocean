"""
Client portal routes for Kuwait Social AI
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
from sqlalchemy import and_, func
from extensions import db
from models import (
    db, Client, Post, PostAnalytics, Analytics, 
    SocialAccount, Feature, CompetitorAnalysis
)
from services.content_generator import ContentGenerator
from services.image_processor import ImageProcessor
from services.social_publisher import SocialPublisher
from services.analytics_service import AnalyticsService
from utils.decorators import client_required
from utils.validators import (
    validate_request, sanitize_input, validate_posting_time,
    validate_content_for_kuwait, validate_hashtags, ContentModerator
)
from schemas import (
    PostCreateSchema, PostUpdateSchema, ContentGenerationSchema,
    AnalyticsQuerySchema, CompetitorAddSchema, PaginationSchema,
    PostResponseSchema
)
import json

client_bp = Blueprint('client', __name__)

# Initialize services
content_generator = ContentGenerator()
image_processor = ImageProcessor()
social_publisher = SocialPublisher()
analytics_service = AnalyticsService()

@client_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@client_required
def get_dashboard():
    """Get client dashboard data"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    # Get client
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    # Get this week's analytics
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday())
    
    weekly_analytics = db.session.query(
        func.sum(Analytics.total_posts).label('total_posts'),
        func.sum(Analytics.total_reach).label('total_reach'),
        func.sum(Analytics.total_engagement).label('total_engagement'),
        func.avg(Analytics.followers_growth).label('avg_growth')
    ).filter(
        and_(
            Analytics.client_id == client_id,
            Analytics.date >= week_start
        )
    ).first()
    
    # Get recent posts
    recent_posts = Post.query.filter_by(
        client_id=client_id
    ).order_by(Post.created_at.desc()).limit(5).all()
    
    # Get scheduled posts
    scheduled_posts = Post.query.filter(
        and_(
            Post.client_id == client_id,
            Post.status == 'scheduled',
            Post.scheduled_time > datetime.utcnow()
        )
    ).order_by(Post.scheduled_time.asc()).limit(5).all()
    
    # Get connected accounts
    social_accounts = SocialAccount.query.filter_by(
        client_id=client_id,
        is_active=True
    ).all()
    
    return jsonify({
        'subscription': {
            'plan': client.subscription_plan,
            'status': client.subscription_status,
            'posts_remaining': client.monthly_posts_limit - client.monthly_posts_used
        },
        'weekly_analytics': {
            'total_posts': weekly_analytics.total_posts or 0,
            'total_reach': weekly_analytics.total_reach or 0,
            'total_engagement': weekly_analytics.total_engagement or 0,
            'growth_rate': float(weekly_analytics.avg_growth or 0)
        },
        'recent_posts': [
            {
                'id': post.id,
                'caption': post.caption_en[:100] + '...' if post.caption_en else '',
                'status': post.status,
                'created_at': post.created_at.isoformat(),
                'engagement': post.analytics.engagement_rate if post.analytics else 0
            }
            for post in recent_posts
        ],
        'scheduled_posts': [
            {
                'id': post.id,
                'caption': post.caption_en[:100] + '...' if post.caption_en else '',
                'scheduled_time': post.scheduled_time.isoformat(),
                'platforms': [acc.platform for acc in social_accounts if acc.id == post.social_account_id]
            }
            for post in scheduled_posts
        ],
        'connected_accounts': [
            {
                'id': acc.id,
                'platform': acc.platform,
                'account_name': acc.account_name,
                'connected_at': acc.connected_at.isoformat()
            }
            for acc in social_accounts
        ],
        'features_enabled': [
            feature.name for feature in client.features if feature.platform_enabled
        ]
    }), 200

@client_bp.route('/posts', methods=['POST'])
@jwt_required()
@client_required
@validate_request(PostCreateSchema)
def create_post(validated_data):
    """Create new post"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    moderator = ContentModerator()
    
    # Check post limit
    client = Client.query.get(client_id)
    if client.monthly_posts_used >= client.monthly_posts_limit:
        return jsonify({'error': 'Monthly post limit reached'}), 403
    
    try:
        # Create post
        post = Post(
            client_id=client_id,
            content_type=data['content_type'],
            status='draft'
        )
        
        # Process based on content type
        if data['content_type'] == 'text':
            # Generate content if AI requested
            if data.get('use_ai') and data.get('prompt'):
                generated = content_generator.generate_content(
                    prompt=data['prompt'],
                    include_arabic=data.get('include_arabic', True),
                    platform=data.get('platform', 'instagram')
                )
                post.caption_en = generated['caption_en']
                post.caption_ar = generated.get('caption_ar')
                post.hashtags = generated['hashtags']
                post.ai_generated = True
                post.ai_prompt = data['prompt']
            else:
                post.caption_en = data.get('caption_en')
                post.caption_ar = data.get('caption_ar')
                post.hashtags = data.get('hashtags', [])
        
        elif data['content_type'] == 'image':
            # Handle image upload and enhancement
            if 'image' in request.files:
                image_file = request.files['image']
                
                # Process image
                processed = image_processor.process_image(
                    image_file,
                    enhance=data.get('enhance', True),
                    resize_for=data.get('platform', 'instagram')
                )
                
                post.media_urls = [processed['url']]
                
                # Generate caption from image if requested
                if data.get('generate_caption'):
                    caption_data = content_generator.generate_caption_from_image(
                        processed['url'],
                        include_arabic=True
                    )
                    post.caption_en = caption_data['caption_en']
                    post.caption_ar = caption_data['caption_ar']
                    post.hashtags = caption_data['hashtags']
        
        # Set schedule if provided
        if data.get('scheduled_time'):
            post.scheduled_time = datetime.fromisoformat(data['scheduled_time'])
            post.status = 'scheduled'
        
        # Link social account
        if data.get('social_account_id'):
            post.social_account_id = data['social_account_id']
        
        db.session.add(post)
        
        # Update usage
        client.monthly_posts_used += 1
        
        db.session.commit()
        
        return jsonify({
            'message': 'Post created successfully',
            'post': {
                'id': post.id,
                'uuid': post.uuid,
                'status': post.status,
                'caption_en': post.caption_en,
                'caption_ar': post.caption_ar,
                'hashtags': post.hashtags,
                'media_urls': post.media_urls,
                'scheduled_time': post.scheduled_time.isoformat() if post.scheduled_time else None
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create post', 'details': str(e)}), 500

@client_bp.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
@client_required
def get_post(post_id):
    """Get post details"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    post = Post.query.filter_by(id=post_id, client_id=client_id).first()
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    return jsonify({
        'id': post.id,
        'uuid': post.uuid,
        'content_type': post.content_type,
        'caption_en': post.caption_en,
        'caption_ar': post.caption_ar,
        'hashtags': post.hashtags,
        'media_urls': post.media_urls,
        'status': post.status,
        'scheduled_time': post.scheduled_time.isoformat() if post.scheduled_time else None,
        'published_time': post.published_time.isoformat() if post.published_time else None,
        'platform_url': post.platform_url,
        'ai_generated': post.ai_generated,
        'created_at': post.created_at.isoformat(),
        'analytics': {
            'impressions': post.analytics.impressions if post.analytics else 0,
            'reach': post.analytics.reach if post.analytics else 0,
            'likes': post.analytics.likes if post.analytics else 0,
            'comments': post.analytics.comments if post.analytics else 0,
            'engagement_rate': post.analytics.engagement_rate if post.analytics else 0
        } if post.analytics else None
    }), 200

@client_bp.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
@client_required
def update_post(post_id):
    """Update post"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    data = request.get_json()
    
    post = Post.query.filter_by(id=post_id, client_id=client_id).first()
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    if post.status == 'published':
        return jsonify({'error': 'Cannot edit published posts'}), 400
    
    # Update fields
    if 'caption_en' in data:
        post.caption_en = data['caption_en']
    if 'caption_ar' in data:
        post.caption_ar = data['caption_ar']
    if 'hashtags' in data:
        post.hashtags = data['hashtags']
    if 'scheduled_time' in data:
        post.scheduled_time = datetime.fromisoformat(data['scheduled_time'])
        post.status = 'scheduled'
    
    post.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Post updated successfully'}), 200

@client_bp.route('/posts/<int:post_id>/publish', methods=['POST'])
@jwt_required()
@client_required
def publish_post(post_id):
    """Publish post immediately"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    post = Post.query.filter_by(id=post_id, client_id=client_id).first()
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    if not post.social_account_id:
        return jsonify({'error': 'No social account linked to post'}), 400
    
    try:
        # Publish to platform
        result = social_publisher.publish_post(post)
        
        if result['success']:
            post.status = 'published'
            post.published_time = datetime.utcnow()
            post.platform_post_id = result['platform_id']
            post.platform_url = result['platform_url']
            db.session.commit()
            
            return jsonify({
                'message': 'Post published successfully',
                'platform_url': result['platform_url']
            }), 200
        else:
            return jsonify({'error': 'Publishing failed', 'details': result['error']}), 500
            
    except Exception as e:
        return jsonify({'error': 'Publishing failed', 'details': str(e)}), 500

@client_bp.route('/posts/<int:post_id>/download', methods=['GET'])
@jwt_required()
@client_required
def download_post(post_id):
    """Download post package for manual posting"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    post = Post.query.filter_by(id=post_id, client_id=client_id).first()
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    # Create download package
    package = {
        'post_id': post.id,
        'created_at': datetime.utcnow().isoformat(),
        'content': {
            'caption_en': post.caption_en,
            'caption_ar': post.caption_ar,
            'hashtags': post.hashtags,
            'media_urls': post.media_urls
        },
        'recommendations': {
            'optimal_times': ['09:00', '13:00', '20:00'],
            'platform_tips': {
                'instagram': {
                    'max_hashtags': 30,
                    'ideal_caption_length': 125,
                    'format': '1:1 for feed, 9:16 for stories'
                },
                'snapchat': {
                    'max_caption_length': 250,
                    'format': '9:16 vertical'
                }
            }
        },
        'kuwait_insights': {
            'prayer_times': analytics_service.get_prayer_times(),
            'trending_hashtags': analytics_service.get_trending_hashtags()
        }
    }
    
    return jsonify(package), 200

@client_bp.route('/analytics/overview', methods=['GET'])
@jwt_required()
@client_required
def get_analytics_overview():
    """Get analytics overview"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    # Time range
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=30)
    
    # Get analytics data
    analytics_data = Analytics.query.filter(
        and_(
            Analytics.client_id == client_id,
            Analytics.date >= start_date,
            Analytics.date <= end_date
        )
    ).order_by(Analytics.date.asc()).all()
    
    # Get top posts
    top_posts = db.session.query(Post, PostAnalytics).join(
        PostAnalytics
    ).filter(
        Post.client_id == client_id
    ).order_by(
        PostAnalytics.engagement_rate.desc()
    ).limit(5).all()
    
    # Format response
    return jsonify({
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'overview': {
            'total_posts': sum(a.total_posts for a in analytics_data),
            'total_reach': sum(a.total_reach for a in analytics_data),
            'total_engagement': sum(a.total_engagement for a in analytics_data),
            'avg_engagement_rate': analytics_service.calculate_engagement_rate(
                sum(a.total_engagement for a in analytics_data),
                sum(a.total_reach for a in analytics_data)
            )
        },
        'daily_metrics': [
            {
                'date': a.date.isoformat(),
                'posts': a.total_posts,
                'reach': a.total_reach,
                'engagement': a.total_engagement,
                'followers': a.followers_count
            }
            for a in analytics_data
        ],
        'top_posts': [
            {
                'id': post.id,
                'caption': post.caption_en[:100] + '...' if post.caption_en else '',
                'published_at': post.published_time.isoformat() if post.published_time else None,
                'reach': analytics.reach,
                'engagement_rate': analytics.engagement_rate,
                'platform_url': post.platform_url
            }
            for post, analytics in top_posts
        ],
        'platform_breakdown': analytics_service.get_platform_breakdown(client_id, start_date, end_date)
    }), 200

@client_bp.route('/competitors', methods=['GET'])
@jwt_required()
@client_required
def get_competitors():
    """Get competitor analysis"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    # Check if feature is enabled
    client = Client.query.get(client_id)
    if not any(f.name == 'competitor_analysis' for f in client.features if f.platform_enabled):
        return jsonify({'error': 'Competitor analysis feature not enabled'}), 403
    
    competitors = CompetitorAnalysis.query.filter_by(client_id=client_id).all()
    
    return jsonify({
        'competitors': [
            {
                'id': c.id,
                'handle': c.competitor_handle,
                'platform': c.platform,
                'followers': c.followers,
                'avg_engagement': c.avg_engagement,
                'posting_frequency': c.posting_frequency,
                'top_hashtags': c.top_hashtags,
                'last_analyzed': c.last_analyzed.isoformat()
            }
            for c in competitors
        ]
    }), 200

@client_bp.route('/features', methods=['GET'])
@jwt_required()
@client_required
def get_enabled_features():
    """Get list of enabled features for client"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    client = Client.query.get(client_id)
    
    enabled_features = [
        {
            'name': feature.name,
            'display_name': feature.display_name,
            'category': feature.category,
            'is_premium': feature.is_premium
        }
        for feature in client.features 
        if feature.platform_enabled
    ]
    
    return jsonify({'features': enabled_features}), 200