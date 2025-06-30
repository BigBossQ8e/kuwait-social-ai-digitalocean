"""
Dashboard routes for client portal
Handles dashboard data and overview information
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timedelta
from sqlalchemy import and_, func
from models import db, Client, Post, Analytics, SocialAccount
from utils.decorators import client_required

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('', methods=['GET'])
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
                'caption': post.caption_en[:100] + '...' if len(post.caption_en) > 100 else post.caption_en,
                'platform': post.platform,
                'status': post.status,
                'created_at': post.created_at.isoformat(),
                'scheduled_time': post.scheduled_time.isoformat() if post.scheduled_time else None,
                'image_url': post.image_url,
                'analytics': {
                    'reach': post.analytics.reach if post.analytics else 0,
                    'engagement': post.analytics.engagement if post.analytics else 0
                }
            } for post in recent_posts
        ],
        'scheduled_posts': [
            {
                'id': post.id,
                'caption': post.caption_en[:100] + '...',
                'platform': post.platform,
                'scheduled_time': post.scheduled_time.isoformat()
            } for post in scheduled_posts
        ],
        'social_accounts': [
            {
                'platform': account.platform,
                'username': account.username,
                'is_active': account.is_active
            } for account in social_accounts
        ]
    }), 200


@dashboard_bp.route('/summary', methods=['GET'])
@jwt_required()
@client_required
def get_dashboard_summary():
    """Get quick summary statistics for dashboard widgets"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    # Get various counts
    total_posts = Post.query.filter_by(client_id=client_id).count()
    published_posts = Post.query.filter_by(
        client_id=client_id,
        status='published'
    ).count()
    scheduled_posts = Post.query.filter_by(
        client_id=client_id,
        status='scheduled'
    ).count()
    
    # Get today's stats
    today_posts = Post.query.filter(
        and_(
            Post.client_id == client_id,
            func.date(Post.created_at) == datetime.utcnow().date()
        )
    ).count()
    
    return jsonify({
        'total_posts': total_posts,
        'published_posts': published_posts,
        'scheduled_posts': scheduled_posts,
        'today_posts': today_posts,
        'timestamp': datetime.utcnow().isoformat()
    }), 200