"""
Analytics routes for client portal
Handles analytics data and reporting
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime, timedelta
from sqlalchemy import and_, func
from models import db, Post, PostAnalytics, Analytics, SocialAccount
from services.analytics_service import AnalyticsService
from utils.decorators import client_required
from schemas import AnalyticsQuerySchema
from utils.validators import validate_request

analytics_bp = Blueprint('analytics', __name__)

# Initialize analytics service
analytics_service = AnalyticsService()


@analytics_bp.route('/overview', methods=['GET'])
@jwt_required()
@client_required
@validate_request(AnalyticsQuerySchema)
def get_analytics_overview(validated_data):
    """Get analytics overview for date range"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    # Extract date range
    start_date = validated_data['start_date']
    end_date = validated_data['end_date']
    platform = validated_data.get('platform')
    
    # Get analytics data
    query = db.session.query(
        Analytics.date,
        func.sum(Analytics.total_posts).label('posts'),
        func.sum(Analytics.total_reach).label('reach'),
        func.sum(Analytics.total_engagement).label('engagement'),
        func.avg(Analytics.engagement_rate).label('engagement_rate'),
        func.sum(Analytics.followers_growth).label('followers_growth')
    ).filter(
        and_(
            Analytics.client_id == client_id,
            Analytics.date >= start_date,
            Analytics.date <= end_date
        )
    )
    
    if platform:
        query = query.filter(Analytics.platform == platform)
    
    analytics_data = query.group_by(Analytics.date).all()
    
    # Calculate totals and averages
    totals = db.session.query(
        func.sum(Analytics.total_posts).label('total_posts'),
        func.sum(Analytics.total_reach).label('total_reach'),
        func.sum(Analytics.total_engagement).label('total_engagement'),
        func.avg(Analytics.engagement_rate).label('avg_engagement_rate')
    ).filter(
        and_(
            Analytics.client_id == client_id,
            Analytics.date >= start_date,
            Analytics.date <= end_date
        )
    ).first()
    
    # Get top performing posts
    top_posts = PostAnalytics.query.join(Post).filter(
        and_(
            Post.client_id == client_id,
            PostAnalytics.recorded_at >= start_date,
            PostAnalytics.recorded_at <= end_date
        )
    ).order_by(PostAnalytics.engagement.desc()).limit(10).all()
    
    return jsonify({
        'date_range': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'totals': {
            'posts': totals.total_posts or 0,
            'reach': totals.total_reach or 0,
            'engagement': totals.total_engagement or 0,
            'engagement_rate': float(totals.avg_engagement_rate or 0)
        },
        'daily_data': [
            {
                'date': data.date.isoformat(),
                'posts': data.posts or 0,
                'reach': data.reach or 0,
                'engagement': data.engagement or 0,
                'engagement_rate': float(data.engagement_rate or 0),
                'followers_growth': data.followers_growth or 0
            } for data in analytics_data
        ],
        'top_posts': [
            {
                'post_id': analytics.post_id,
                'caption': analytics.post.caption_en[:100] + '...',
                'platform': analytics.post.platform,
                'reach': analytics.reach,
                'engagement': analytics.engagement,
                'engagement_rate': analytics.engagement_rate,
                'published_at': analytics.post.published_at.isoformat() if analytics.post.published_at else None
            } for analytics in top_posts
        ]
    }), 200


@analytics_bp.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
@client_required
def get_post_analytics(post_id):
    """Get detailed analytics for a specific post"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    # Verify post belongs to client
    post = Post.query.filter_by(
        id=post_id,
        client_id=client_id
    ).first()
    
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    # Get all analytics records for this post
    analytics = PostAnalytics.query.filter_by(
        post_id=post_id
    ).order_by(PostAnalytics.recorded_at.desc()).all()
    
    if not analytics:
        return jsonify({'error': 'No analytics data available'}), 404
    
    # Get latest metrics
    latest = analytics[0]
    
    # Calculate growth over time
    growth_data = []
    for record in reversed(analytics):
        growth_data.append({
            'timestamp': record.recorded_at.isoformat(),
            'reach': record.reach,
            'likes': record.likes,
            'comments': record.comments,
            'shares': record.shares,
            'saves': record.saves
        })
    
    return jsonify({
        'post': {
            'id': post.id,
            'caption': post.caption_en,
            'platform': post.platform,
            'published_at': post.published_at.isoformat() if post.published_at else None
        },
        'current_metrics': {
            'reach': latest.reach,
            'impressions': latest.impressions,
            'likes': latest.likes,
            'comments': latest.comments,
            'shares': latest.shares,
            'saves': latest.saves,
            'engagement': latest.engagement,
            'engagement_rate': latest.engagement_rate
        },
        'growth_timeline': growth_data,
        'metadata': latest.metadata or {}
    }), 200


@analytics_bp.route('/engagement', methods=['GET'])
@jwt_required()
@client_required
def get_engagement_analytics():
    """Get engagement analytics by content type, time, etc."""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    # Get parameters
    days = request.args.get('days', 30, type=int)
    group_by = request.args.get('group_by', 'day')  # day, hour, day_of_week
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get engagement by time
    if group_by == 'hour':
        data = db.session.query(
            func.extract('hour', Post.published_at).label('hour'),
            func.avg(PostAnalytics.engagement_rate).label('avg_engagement')
        ).join(PostAnalytics).filter(
            and_(
                Post.client_id == client_id,
                Post.published_at >= start_date,
                Post.published_at <= end_date
            )
        ).group_by('hour').all()
        
        result = {
            'by_hour': [
                {'hour': int(d.hour), 'engagement_rate': float(d.avg_engagement or 0)}
                for d in data
            ]
        }
        
    elif group_by == 'day_of_week':
        data = db.session.query(
            func.extract('dow', Post.published_at).label('day'),
            func.avg(PostAnalytics.engagement_rate).label('avg_engagement')
        ).join(PostAnalytics).filter(
            and_(
                Post.client_id == client_id,
                Post.published_at >= start_date,
                Post.published_at <= end_date
            )
        ).group_by('day').all()
        
        days_map = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        result = {
            'by_day_of_week': [
                {'day': days_map[int(d.day)], 'engagement_rate': float(d.avg_engagement or 0)}
                for d in data
            ]
        }
        
    else:  # Default to daily
        data = db.session.query(
            func.date(Post.published_at).label('date'),
            func.avg(PostAnalytics.engagement_rate).label('avg_engagement')
        ).join(PostAnalytics).filter(
            and_(
                Post.client_id == client_id,
                Post.published_at >= start_date,
                Post.published_at <= end_date
            )
        ).group_by('date').all()
        
        result = {
            'by_day': [
                {'date': d.date.isoformat(), 'engagement_rate': float(d.avg_engagement or 0)}
                for d in data
            ]
        }
    
    # Add content type analysis
    content_data = db.session.query(
        Post.platform,
        func.count(Post.id).label('post_count'),
        func.avg(PostAnalytics.engagement_rate).label('avg_engagement')
    ).join(PostAnalytics).filter(
        and_(
            Post.client_id == client_id,
            Post.published_at >= start_date,
            Post.published_at <= end_date
        )
    ).group_by(Post.platform).all()
    
    result['by_platform'] = [
        {
            'platform': d.platform,
            'post_count': d.post_count,
            'avg_engagement_rate': float(d.avg_engagement or 0)
        }
        for d in content_data
    ]
    
    return jsonify(result), 200


@analytics_bp.route('/audience', methods=['GET'])
@jwt_required()
@client_required
def get_audience_analytics():
    """Get audience demographics and insights"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    # This would typically come from social media APIs
    # For now, return mock data structure
    return jsonify({
        'demographics': {
            'age_groups': [
                {'range': '18-24', 'percentage': 25},
                {'range': '25-34', 'percentage': 35},
                {'range': '35-44', 'percentage': 20},
                {'range': '45-54', 'percentage': 15},
                {'range': '55+', 'percentage': 5}
            ],
            'gender': {
                'male': 45,
                'female': 55
            },
            'locations': [
                {'city': 'Kuwait City', 'percentage': 40},
                {'city': 'Hawalli', 'percentage': 20},
                {'city': 'Farwaniya', 'percentage': 15},
                {'city': 'Ahmadi', 'percentage': 10},
                {'city': 'Jahra', 'percentage': 10},
                {'city': 'Other', 'percentage': 5}
            ]
        },
        'growth': {
            'followers_total': 5000,
            'followers_growth_30d': 250,
            'growth_rate': 5.0
        },
        'best_times': {
            'posting_times': [
                {'day': 'Sunday', 'time': '20:00', 'engagement': 8.5},
                {'day': 'Monday', 'time': '19:00', 'engagement': 7.2},
                {'day': 'Tuesday', 'time': '21:00', 'engagement': 7.8},
                {'day': 'Wednesday', 'time': '20:00', 'engagement': 8.1},
                {'day': 'Thursday', 'time': '19:00', 'engagement': 7.5}
            ]
        }
    }), 200


@analytics_bp.route('/export', methods=['POST'])
@jwt_required()
@client_required
def export_analytics():
    """Export analytics data in various formats"""
    claims = get_jwt()
    client_id = claims.get('client_id')
    
    data = request.get_json()
    format = data.get('format', 'csv')  # csv, pdf, excel
    date_range = data.get('date_range', {})
    
    # Generate export based on format
    # This is a placeholder - actual implementation would generate files
    
    return jsonify({
        'message': 'Export request received',
        'format': format,
        'status': 'processing',
        'download_url': f'/api/client/analytics/download/{client_id}_analytics.{format}'
    }), 202