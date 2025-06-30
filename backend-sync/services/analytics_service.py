from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from models import db, Post, PostAnalytics, CustomerEngagement, HashtagPerformance


class AnalyticsService:
    """Service for handling analytics operations"""
    
    @staticmethod
    def get_engagement_metrics(client_id: int, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Get engagement metrics for a client"""
        query = db.session.query(
            func.sum(PostAnalytics.likes).label('total_likes'),
            func.sum(PostAnalytics.comments).label('total_comments'),
            func.sum(PostAnalytics.shares).label('total_shares'),
            func.sum(PostAnalytics.views).label('total_views'),
            func.avg(PostAnalytics.engagement_rate).label('avg_engagement_rate')
        ).join(Post).filter(Post.client_id == client_id)
        
        if start_date:
            query = query.filter(Post.created_at >= start_date)
        if end_date:
            query = query.filter(Post.created_at <= end_date)
            
        result = query.first()
        
        return {
            'total_likes': int(result.total_likes or 0),
            'total_comments': int(result.total_comments or 0),
            'total_shares': int(result.total_shares or 0),
            'total_views': int(result.total_views or 0),
            'avg_engagement_rate': float(result.avg_engagement_rate or 0)
        }
    
    @staticmethod
    def get_post_performance(client_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing posts for a client"""
        posts = db.session.query(Post, PostAnalytics)\
            .join(PostAnalytics)\
            .filter(Post.client_id == client_id)\
            .order_by(PostAnalytics.engagement_rate.desc())\
            .limit(limit)\
            .all()
            
        return [{
            'id': post.id,
            'content': post.content,
            'platform': post.platform,
            'created_at': post.created_at.isoformat(),
            'likes': analytics.likes,
            'comments': analytics.comments,
            'shares': analytics.shares,
            'views': analytics.views,
            'engagement_rate': analytics.engagement_rate
        } for post, analytics in posts]
    
    @staticmethod
    def get_audience_insights(client_id: int) -> Dict[str, Any]:
        """Get audience insights for a client"""
        # This would typically query audience demographics data
        # For now, returning placeholder data
        return {
            'demographics': {
                'age_groups': {
                    '18-24': 25,
                    '25-34': 35,
                    '35-44': 20,
                    '45-54': 15,
                    '55+': 5
                },
                'gender': {
                    'male': 45,
                    'female': 55
                },
                'locations': {
                    'Kuwait City': 40,
                    'Hawally': 25,
                    'Farwaniya': 20,
                    'Other': 15
                }
            },
            'active_times': {
                'weekdays': {
                    '9-12': 25,
                    '12-15': 20,
                    '15-18': 30,
                    '18-21': 25
                },
                'weekends': {
                    '9-12': 20,
                    '12-15': 25,
                    '15-18': 35,
                    '18-21': 20
                }
            }
        }
    
    @staticmethod
    def get_hashtag_performance(client_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get hashtag performance data"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # This would query hashtag performance data
        # For now, returning placeholder data
        return [
            {
                'hashtag': '#kuwait',
                'usage_count': 150,
                'avg_engagement': 4.5,
                'reach': 25000
            },
            {
                'hashtag': '#kuwaitbusiness',
                'usage_count': 80,
                'avg_engagement': 3.8,
                'reach': 15000
            },
            {
                'hashtag': '#q8',
                'usage_count': 120,
                'avg_engagement': 4.2,
                'reach': 20000
            }
        ]
    
    @staticmethod
    def get_growth_metrics(client_id: int, period: str = 'month') -> Dict[str, Any]:
        """Get growth metrics over a period"""
        # Define period lengths
        periods = {
            'week': 7,
            'month': 30,
            'quarter': 90,
            'year': 365
        }
        
        days = periods.get(period, 30)
        current_start = datetime.utcnow() - timedelta(days=days)
        previous_start = current_start - timedelta(days=days)
        
        # Get current period metrics
        current_metrics = AnalyticsService.get_engagement_metrics(
            client_id, current_start, datetime.utcnow()
        )
        
        # Get previous period metrics
        previous_metrics = AnalyticsService.get_engagement_metrics(
            client_id, previous_start, current_start
        )
        
        # Calculate growth
        growth = {}
        for key in current_metrics:
            if key != 'avg_engagement_rate':
                current_val = current_metrics[key]
                previous_val = previous_metrics[key]
                if previous_val > 0:
                    growth[f'{key}_growth'] = ((current_val - previous_val) / previous_val) * 100
                else:
                    growth[f'{key}_growth'] = 100 if current_val > 0 else 0
        
        return {
            'current_period': current_metrics,
            'previous_period': previous_metrics,
            'growth': growth
        }