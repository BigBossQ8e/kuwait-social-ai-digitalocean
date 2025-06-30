"""
Query optimization utilities to prevent N+1 queries
"""

from sqlalchemy.orm import joinedload, selectinload, contains_eager
from typing import List, Optional, Any
from . import db


class QueryOptimizer:
    """Helper class for optimized database queries"""
    
    @staticmethod
    def get_posts_with_analytics(client_id: int, limit: int = 50):
        """Get posts with analytics pre-loaded to avoid N+1 queries"""
        from . import ScheduledPost, PostAnalytics
        
        return ScheduledPost.query.filter_by(
            client_id=client_id
        ).options(
            joinedload(ScheduledPost.analytics)
        ).order_by(
            ScheduledPost.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_client_with_all_relations(client_id: int):
        """Get client with all relationships pre-loaded"""
        from . import Client
        
        return Client.query.filter_by(
            id=client_id
        ).options(
            joinedload(Client.user),
            joinedload(Client.admin),
            selectinload(Client.social_accounts),
            selectinload(Client.scheduled_posts).joinedload('analytics'),
            selectinload(Client.campaigns),
            selectinload(Client.content_templates),
            selectinload(Client.competitors).selectinload('analyses')
        ).first()
    
    @staticmethod
    def get_campaign_with_posts(campaign_id: int):
        """Get campaign with all posts and their analytics"""
        from . import Campaign
        
        return Campaign.query.filter_by(
            id=campaign_id
        ).options(
            joinedload(Campaign.client),
            selectinload(Campaign.posts).options(
                joinedload('analytics'),
                joinedload('social_accounts')
            )
        ).first()
    
    @staticmethod
    def get_competitors_with_latest_analysis(client_id: int):
        """Get competitors with their latest analysis pre-loaded"""
        from . import Competitor, CompetitorAnalysis
        from sqlalchemy import and_
        
        # Subquery to get latest analysis date for each competitor
        latest_analysis = db.session.query(
            CompetitorAnalysis.competitor_id,
            db.func.max(CompetitorAnalysis.analysis_date).label('latest_date')
        ).group_by(
            CompetitorAnalysis.competitor_id
        ).subquery()
        
        return db.session.query(Competitor).filter(
            Competitor.client_id == client_id,
            Competitor.is_active == True
        ).outerjoin(
            CompetitorAnalysis,
            and_(
                CompetitorAnalysis.competitor_id == Competitor.id,
                CompetitorAnalysis.analysis_date == latest_analysis.c.latest_date
            )
        ).options(
            contains_eager(Competitor.analyses)
        ).all()
    
    @staticmethod
    def get_inbox_messages_with_profiles(client_id: int, unread_only: bool = False):
        """Get inbox messages with customer profiles pre-loaded"""
        from . import UnifiedInboxMessage, CustomerProfile
        
        query = UnifiedInboxMessage.query.filter_by(
            client_id=client_id
        )
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        return query.outerjoin(
            CustomerProfile,
            db.or_(
                CustomerProfile.instagram_username == UnifiedInboxMessage.sender_username,
                CustomerProfile.snapchat_username == UnifiedInboxMessage.sender_username
            )
        ).options(
            contains_eager('customer_profile'),
            joinedload('suggested_template')
        ).order_by(
            UnifiedInboxMessage.received_at.desc()
        ).all()
    
    @staticmethod
    def get_hashtag_performance_aggregated(client_id: int, days: int = 30):
        """Get aggregated hashtag performance to avoid multiple queries"""
        from . import HashtagPerformance
        from datetime import datetime, timedelta
        
        since_date = datetime.utcnow() - timedelta(days=days)
        
        return db.session.query(
            HashtagPerformance.hashtag,
            db.func.count(HashtagPerformance.id).label('usage_count'),
            db.func.avg(HashtagPerformance.engagement_rate).label('avg_engagement_rate'),
            db.func.sum(HashtagPerformance.reach).label('total_reach'),
            db.func.sum(HashtagPerformance.engagement).label('total_engagement')
        ).filter(
            HashtagPerformance.client_id == client_id,
            HashtagPerformance.measured_at >= since_date
        ).group_by(
            HashtagPerformance.hashtag
        ).order_by(
            db.desc('avg_engagement_rate')
        ).all()
    
    @staticmethod
    def bulk_create_posts(posts_data: List[dict]) -> List[Any]:
        """Bulk create posts to avoid multiple insert queries"""
        from . import ScheduledPost
        
        posts = []
        for data in posts_data:
            post = ScheduledPost(**data)
            posts.append(post)
        
        db.session.bulk_save_objects(posts, return_defaults=True)
        db.session.commit()
        
        return posts
    
    @staticmethod
    def update_analytics_batch(analytics_data: List[dict]):
        """Batch update analytics to avoid multiple update queries"""
        from . import PostAnalytics
        
        db.session.bulk_update_mappings(PostAnalytics, analytics_data)
        db.session.commit()


class EagerLoadMixin:
    """Mixin to add eager loading methods to models"""
    
    @classmethod
    def with_relations(cls, *relations):
        """Load model with specified relations"""
        query = cls.query
        for relation in relations:
            if '.' in relation:
                # Handle nested relations
                parts = relation.split('.')
                option = joinedload(getattr(cls, parts[0]))
                for part in parts[1:]:
                    option = option.joinedload(part)
                query = query.options(option)
            else:
                query = query.options(joinedload(getattr(cls, relation)))
        return query
    
    @classmethod
    def with_select_relations(cls, *relations):
        """Load model with specified relations using selectinload"""
        query = cls.query
        for relation in relations:
            query = query.options(selectinload(getattr(cls, relation)))
        return query


# Query optimization decorators
def optimize_query(eager_load=None, select_load=None):
    """Decorator to automatically optimize queries"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get the query result
            result = func(*args, **kwargs)
            
            # Apply eager loading if specified
            if hasattr(result, 'options'):
                if eager_load:
                    for relation in eager_load:
                        result = result.options(joinedload(relation))
                if select_load:
                    for relation in select_load:
                        result = result.options(selectinload(relation))
            
            return result
        return wrapper
    return decorator


# Example usage in routes
"""
# Bad (N+1 queries):
posts = ScheduledPost.query.filter_by(client_id=client_id).all()
for post in posts:
    analytics = post.analytics  # This triggers a new query for each post!
    
# Good (1 query with join):
posts = QueryOptimizer.get_posts_with_analytics(client_id)
for post in posts:
    analytics = post.analytics  # Already loaded, no additional query

# Or using the mixin:
posts = ScheduledPost.with_relations('analytics').filter_by(client_id=client_id).all()
"""