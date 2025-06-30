"""
Customer Engagement Service
Handles customer engagement features and analytics
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import func, desc
from models import (
    db, CustomerEngagement, CommentTemplate, UnifiedInboxMessage,
    MessageThread, ResponseMetrics, CustomerProfile, EngagementAutomation
)


class CustomerEngagementService:
    """Service for managing customer engagement features"""
    
    @staticmethod
    def get_engagement_summary(client_id: int, days: int = 30) -> Dict:
        """Get engagement summary for a client"""
        since_date = datetime.utcnow() - timedelta(days=days)
        
        # Get total engagements
        total_engagements = db.session.query(func.count(CustomerEngagement.id))\
            .filter(CustomerEngagement.client_id == client_id)\
            .filter(CustomerEngagement.created_at >= since_date)\
            .scalar()
        
        # Get engagement by type
        engagement_by_type = db.session.query(
            CustomerEngagement.engagement_type,
            func.count(CustomerEngagement.id)
        ).filter(
            CustomerEngagement.client_id == client_id,
            CustomerEngagement.created_at >= since_date
        ).group_by(CustomerEngagement.engagement_type).all()
        
        # Get average response time
        avg_response_time = db.session.query(
            func.avg(CustomerEngagement.response_time_minutes)
        ).filter(
            CustomerEngagement.client_id == client_id,
            CustomerEngagement.created_at >= since_date,
            CustomerEngagement.response_time_minutes.isnot(None)
        ).scalar() or 0
        
        # Get sentiment distribution
        sentiment_dist = db.session.query(
            CustomerEngagement.sentiment,
            func.count(CustomerEngagement.id)
        ).filter(
            CustomerEngagement.client_id == client_id,
            CustomerEngagement.created_at >= since_date,
            CustomerEngagement.sentiment.isnot(None)
        ).group_by(CustomerEngagement.sentiment).all()
        
        return {
            'total_engagements': total_engagements,
            'engagement_by_type': dict(engagement_by_type),
            'average_response_time': round(avg_response_time, 2),
            'sentiment_distribution': dict(sentiment_dist),
            'period_days': days
        }
    
    @staticmethod
    def get_message_threads(client_id: int, status: Optional[str] = None, 
                          limit: int = 50) -> List[MessageThread]:
        """Get message threads for a client"""
        query = MessageThread.query.filter_by(client_id=client_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(desc(MessageThread.last_message_at))\
                   .limit(limit).all()
    
    @staticmethod
    def get_comment_templates(client_id: int, category: Optional[str] = None) -> List[CommentTemplate]:
        """Get comment templates for a client"""
        query = CommentTemplate.query.filter_by(
            client_id=client_id,
            is_active=True
        )
        
        if category:
            query = query.filter_by(category=category)
        
        return query.order_by(desc(CommentTemplate.usage_count)).all()
    
    @staticmethod
    def create_engagement(client_id: int, engagement_data: Dict) -> CustomerEngagement:
        """Create a new customer engagement record"""
        engagement = CustomerEngagement(
            client_id=client_id,
            platform=engagement_data.get('platform'),
            engagement_type=engagement_data.get('engagement_type'),
            customer_id=engagement_data.get('customer_id'),
            customer_name=engagement_data.get('customer_name'),
            content=engagement_data.get('content'),
            response=engagement_data.get('response'),
            sentiment=engagement_data.get('sentiment'),
            is_automated=engagement_data.get('is_automated', False),
            post_id=engagement_data.get('post_id')
        )
        
        db.session.add(engagement)
        db.session.commit()
        
        return engagement
    
    @staticmethod
    def get_automation_rules(client_id: int, is_active: bool = True) -> List[EngagementAutomation]:
        """Get automation rules for a client"""
        return EngagementAutomation.query.filter_by(
            client_id=client_id,
            is_active=is_active
        ).order_by(desc(EngagementAutomation.priority)).all()
    
    @staticmethod
    def get_response_metrics(client_id: int, platform: Optional[str] = None) -> ResponseMetrics:
        """Get response metrics for a client"""
        query = ResponseMetrics.query.filter_by(client_id=client_id)
        
        if platform:
            query = query.filter_by(platform=platform)
        
        return query.first()
    
    @staticmethod
    def update_response_metrics(client_id: int, platform: str, response_time: float):
        """Update response metrics after an engagement"""
        metrics = ResponseMetrics.query.filter_by(
            client_id=client_id,
            platform=platform
        ).first()
        
        if not metrics:
            metrics = ResponseMetrics(
                client_id=client_id,
                platform=platform,
                avg_response_time=response_time,
                total_responses=1
            )
            db.session.add(metrics)
        else:
            # Update rolling average
            total = metrics.total_responses
            new_avg = ((metrics.avg_response_time * total) + response_time) / (total + 1)
            metrics.avg_response_time = new_avg
            metrics.total_responses = total + 1
            metrics.last_updated = datetime.utcnow()
        
        db.session.commit()
        
        return metrics