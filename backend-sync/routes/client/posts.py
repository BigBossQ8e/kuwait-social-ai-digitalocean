"""
Posts management routes for client portal
Handles CRUD operations for social media posts
"""

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime
from sqlalchemy import and_
from models import db, Client, Post, PostAnalytics
from services.content_generator import ContentGenerator
from services.image_processor import ImageProcessor
from services.social_publisher import SocialPublisher
from utils.decorators import client_required, validate_ownership
from utils.validators import (
    validate_request, validate_posting_time,
    validate_content_for_kuwait, validate_hashtags
)
from schemas import PostCreateSchema, PostUpdateSchema, PaginationSchema
import os
import io

posts_bp = Blueprint('posts', __name__)

# Initialize services
content_generator = ContentGenerator()
image_processor = ImageProcessor()
social_publisher = SocialPublisher()


@posts_bp.route('', methods=['GET'])
@jwt_required()
@client_required
@validate_request(PaginationSchema)
def get_posts(validated_data):
    """Get paginated list of client's posts"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    # Extract pagination parameters
    page = validated_data.get('page', 1)
    per_page = validated_data.get('per_page', 20)
    sort_by = validated_data.get('sort_by', 'created_at')
    sort_order = validated_data.get('sort_order', 'desc')
    
    # Build query
    query = Post.query.filter_by(client_id=client_id)
    
    # Apply filters if provided
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    platform = request.args.get('platform')
    if platform:
        query = query.filter_by(platform=platform)
    
    # Apply sorting
    if sort_order == 'desc':
        query = query.order_by(getattr(Post, sort_by).desc())
    else:
        query = query.order_by(getattr(Post, sort_by))
    
    # Paginate
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'posts': [post.to_dict() for post in paginated.items],
        'pagination': {
            'page': paginated.page,
            'per_page': paginated.per_page,
            'total': paginated.total,
            'pages': paginated.pages,
            'has_prev': paginated.has_prev,
            'has_next': paginated.has_next
        }
    }), 200


@posts_bp.route('', methods=['POST'])
@jwt_required()
@client_required
@validate_request(PostCreateSchema)
def create_post(validated_data):
    """Create a new post"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    # Get client
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    
    # Check monthly limit
    if client.monthly_posts_used >= client.monthly_posts_limit:
        return jsonify({
            'error': 'Monthly post limit reached',
            'limit': client.monthly_posts_limit,
            'used': client.monthly_posts_used
        }), 403
    
    # Validate content for Kuwait market
    content_validation = validate_content_for_kuwait(validated_data['caption_en'])
    if not content_validation['is_valid']:
        return jsonify({
            'error': 'Content validation failed',
            'issues': content_validation['issues']
        }), 400
    
    # Validate hashtags
    if validated_data.get('hashtags'):
        hashtag_validation = validate_hashtags(validated_data['hashtags'])
        if not hashtag_validation['is_valid']:
            return jsonify({
                'error': 'Hashtag validation failed',
                'issues': hashtag_validation['issues']
            }), 400
    
    # Validate posting time
    if validated_data.get('scheduled_time'):
        time_validation = validate_posting_time(validated_data['scheduled_time'])
        if not time_validation['is_valid']:
            return jsonify({
                'error': 'Invalid posting time',
                'issues': time_validation['issues'],
                'suggestions': time_validation['suggestions']
            }), 400
    
    # Process image if provided
    image_url = None
    if validated_data.get('image_data'):
        try:
            # Process image with AI enhancement
            processed_image = image_processor.enhance_image(
                validated_data['image_data'],
                platform=validated_data['platform']
            )
            # Save processed image
            image_url = image_processor.save_image(processed_image, client_id)
        except Exception as e:
            return jsonify({'error': f'Image processing failed: {str(e)}'}), 500
    
    # Create post
    post = Post(
        client_id=client_id,
        caption_en=validated_data['caption_en'],
        caption_ar=validated_data.get('caption_ar'),
        hashtags=validated_data.get('hashtags', []),
        platform=validated_data['platform'],
        scheduled_time=validated_data.get('scheduled_time'),
        status='scheduled' if validated_data.get('scheduled_time') else 'draft',
        image_url=image_url,
        ai_generated=validated_data.get('ai_generated', False)
    )
    
    # Add warnings from validation
    if content_validation.get('warnings'):
        post.metadata = {
            'content_warnings': content_validation['warnings'],
            'suggestions': content_validation.get('suggestions', [])
        }
    
    db.session.add(post)
    
    # Update client's monthly usage
    client.monthly_posts_used += 1
    
    db.session.commit()
    
    return jsonify({
        'post': post.to_dict(),
        'warnings': content_validation.get('warnings', [])
    }), 201


@posts_bp.route('/<int:post_id>', methods=['GET'])
@jwt_required()
@client_required
@validate_ownership('post')
def get_post(post_id):
    """Get a specific post"""
    post = Post.query.get_or_404(post_id)
    
    # Include analytics if available
    post_data = post.to_dict()
    if post.analytics:
        post_data['analytics'] = post.analytics.to_dict()
    
    return jsonify(post_data), 200


@posts_bp.route('/<int:post_id>', methods=['PUT'])
@jwt_required()
@client_required
@validate_ownership('post')
@validate_request(PostUpdateSchema)
def update_post(post_id, validated_data):
    """Update a post"""
    post = Post.query.get_or_404(post_id)
    
    # Can only update if not published
    if post.status == 'published':
        return jsonify({'error': 'Cannot update published posts'}), 400
    
    # Update fields
    if 'caption_en' in validated_data:
        post.caption_en = validated_data['caption_en']
    if 'caption_ar' in validated_data:
        post.caption_ar = validated_data['caption_ar']
    if 'hashtags' in validated_data:
        post.hashtags = validated_data['hashtags']
    if 'scheduled_time' in validated_data:
        post.scheduled_time = validated_data['scheduled_time']
        post.status = 'scheduled' if validated_data['scheduled_time'] else 'draft'
    
    # Update image if provided
    if validated_data.get('image_data'):
        try:
            processed_image = image_processor.enhance_image(
                validated_data['image_data'],
                platform=post.platform
            )
            post.image_url = image_processor.save_image(
                processed_image, 
                post.client_id
            )
        except Exception as e:
            return jsonify({'error': f'Image update failed: {str(e)}'}), 500
    
    post.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(post.to_dict()), 200


@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
@client_required
@validate_ownership('post')
def delete_post(post_id):
    """Delete a post"""
    post = Post.query.get_or_404(post_id)
    
    # Can only delete if not published
    if post.status == 'published':
        return jsonify({'error': 'Cannot delete published posts'}), 400
    
    # Delete associated image if exists
    if post.image_url:
        try:
            image_processor.delete_image(post.image_url)
        except:
            pass  # Continue even if image deletion fails
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'message': 'Post deleted successfully'}), 200


@posts_bp.route('/<int:post_id>/publish', methods=['POST'])
@jwt_required()
@client_required
@validate_ownership('post')
def publish_post(post_id):
    """Publish a post to social media"""
    post = Post.query.get_or_404(post_id)
    
    # Check if post can be published
    if post.status == 'published':
        return jsonify({'error': 'Post already published'}), 400
    
    if not post.image_url and post.platform in ['instagram', 'snapchat']:
        return jsonify({'error': 'Image required for this platform'}), 400
    
    # Get connected social accounts
    social_accounts = SocialAccount.query.filter_by(
        client_id=post.client_id,
        platform=post.platform,
        is_active=True
    ).all()
    
    if not social_accounts:
        return jsonify({
            'error': f'No connected {post.platform} account found'
        }), 400
    
    # Publish to social media
    try:
        results = social_publisher.publish_post(post, social_accounts)
        
        # Update post status
        post.status = 'published'
        post.published_at = datetime.utcnow()
        
        # Store publishing results
        post.publishing_data = results
        
        db.session.commit()
        
        return jsonify({
            'message': 'Post published successfully',
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Publishing failed: {str(e)}'
        }), 500


@posts_bp.route('/<int:post_id>/download', methods=['GET'])
@jwt_required()
@client_required
@validate_ownership('post')
def download_post(post_id):
    """Download post image with caption overlay"""
    post = Post.query.get_or_404(post_id)
    
    if not post.image_url:
        return jsonify({'error': 'No image available for this post'}), 404
    
    try:
        # Generate image with caption overlay
        image_with_caption = image_processor.add_caption_overlay(
            post.image_url,
            post.caption_en,
            post.caption_ar,
            post.platform
        )
        
        # Convert to bytes for download
        img_io = io.BytesIO()
        image_with_caption.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'post_{post_id}_{post.platform}.png'
        )
        
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500


@posts_bp.route('/bulk/schedule', methods=['POST'])
@jwt_required()
@client_required
def bulk_schedule_posts():
    """Schedule multiple posts at once"""
    data = request.get_json()
    post_ids = data.get('post_ids', [])
    schedule_times = data.get('schedule_times', [])
    
    if len(post_ids) != len(schedule_times):
        return jsonify({'error': 'Mismatch between posts and schedule times'}), 400
    
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    updated_posts = []
    errors = []
    
    for post_id, schedule_time in zip(post_ids, schedule_times):
        try:
            post = Post.query.filter_by(
                id=post_id,
                client_id=client_id
            ).first()
            
            if not post:
                errors.append(f"Post {post_id} not found")
                continue
            
            if post.status == 'published':
                errors.append(f"Post {post_id} already published")
                continue
            
            # Validate schedule time
            schedule_dt = datetime.fromisoformat(schedule_time)
            time_validation = validate_posting_time(schedule_dt)
            
            if not time_validation['is_valid']:
                errors.append(f"Post {post_id}: {time_validation['issues'][0]}")
                continue
            
            post.scheduled_time = schedule_dt
            post.status = 'scheduled'
            updated_posts.append(post_id)
            
        except Exception as e:
            errors.append(f"Post {post_id}: {str(e)}")
    
    db.session.commit()
    
    return jsonify({
        'updated': updated_posts,
        'errors': errors,
        'total_updated': len(updated_posts)
    }), 200