"""
Kuwait Features Service
Handles Kuwait-specific features and cultural content
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import func, desc, and_
from models import (
    db, KuwaitFeature, KuwaitEvent, KuwaitHistoricalFact, 
    KuwaitTrendingTopic, KuwaitBusinessDirectory, CulturalGuideline,
    LocalInfluencer
)


class KuwaitFeaturesService:
    """Service for managing Kuwait-specific features"""
    
    @staticmethod
    def get_active_features(client_id: int) -> List[KuwaitFeature]:
        """Get all active Kuwait features for a client"""
        return KuwaitFeature.query.filter_by(
            client_id=client_id,
            is_active=True
        ).order_by(KuwaitFeature.feature_order).all()
    
    @staticmethod
    def get_upcoming_events(days_ahead: int = 30) -> List[KuwaitEvent]:
        """Get upcoming Kuwait events"""
        end_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        return KuwaitEvent.query.filter(
            and_(
                KuwaitEvent.event_date >= datetime.utcnow(),
                KuwaitEvent.event_date <= end_date,
                KuwaitEvent.is_active == True
            )
        ).order_by(KuwaitEvent.event_date).all()
    
    @staticmethod
    def get_trending_topics(limit: int = 10) -> List[KuwaitTrendingTopic]:
        """Get current trending topics in Kuwait"""
        # Topics are considered trending if updated within last 24 hours
        since = datetime.utcnow() - timedelta(hours=24)
        
        return KuwaitTrendingTopic.query.filter(
            KuwaitTrendingTopic.last_updated >= since
        ).order_by(desc(KuwaitTrendingTopic.trend_score)).limit(limit).all()
    
    @staticmethod
    def get_cultural_guidelines(category: Optional[str] = None) -> List[CulturalGuideline]:
        """Get cultural guidelines for content creation"""
        query = CulturalGuideline.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        
        return query.order_by(CulturalGuideline.importance_level.desc()).all()
    
    @staticmethod
    def get_local_influencers(platform: Optional[str] = None, 
                            min_followers: int = 0) -> List[LocalInfluencer]:
        """Get local influencers for collaboration"""
        query = LocalInfluencer.query.filter(
            and_(
                LocalInfluencer.is_active == True,
                LocalInfluencer.follower_count >= min_followers
            )
        )
        
        if platform:
            query = query.filter_by(primary_platform=platform)
        
        return query.order_by(desc(LocalInfluencer.engagement_rate)).all()
    
    @staticmethod
    def get_business_directory(category: Optional[str] = None, 
                             area: Optional[str] = None) -> List[KuwaitBusinessDirectory]:
        """Get Kuwait business directory entries"""
        query = KuwaitBusinessDirectory.query.filter_by(is_verified=True)
        
        if category:
            query = query.filter_by(category=category)
        
        if area:
            query = query.filter_by(area=area)
        
        return query.order_by(KuwaitBusinessDirectory.business_name).all()
    
    @staticmethod
    def get_historical_facts(category: Optional[str] = None) -> List[KuwaitHistoricalFact]:
        """Get Kuwait historical facts for content"""
        query = KuwaitHistoricalFact.query
        
        if category:
            query = query.filter_by(category=category)
        
        return query.order_by(func.random()).limit(5).all()
    
    @staticmethod
    def create_feature(client_id: int, feature_data: Dict) -> KuwaitFeature:
        """Create a new Kuwait feature for a client"""
        feature = KuwaitFeature(
            client_id=client_id,
            feature_name=feature_data.get('feature_name'),
            feature_type=feature_data.get('feature_type'),
            configuration=feature_data.get('configuration', {}),
            is_active=feature_data.get('is_active', True),
            feature_order=feature_data.get('feature_order', 0)
        )
        
        db.session.add(feature)
        db.session.commit()
        
        return feature
    
    @staticmethod
    def update_feature(feature_id: int, updates: Dict) -> KuwaitFeature:
        """Update a Kuwait feature"""
        feature = KuwaitFeature.query.get(feature_id)
        if not feature:
            raise ValueError(f"Feature {feature_id} not found")
        
        for key, value in updates.items():
            if hasattr(feature, key):
                setattr(feature, key, value)
        
        feature.updated_at = datetime.utcnow()
        db.session.commit()
        
        return feature
    
    @staticmethod
    def get_feature_analytics(client_id: int) -> Dict:
        """Get analytics for Kuwait features usage"""
        features = KuwaitFeature.query.filter_by(client_id=client_id).all()
        
        analytics = {
            'total_features': len(features),
            'active_features': sum(1 for f in features if f.is_active),
            'feature_types': {},
            'last_updated': None
        }
        
        for feature in features:
            feature_type = feature.feature_type
            if feature_type not in analytics['feature_types']:
                analytics['feature_types'][feature_type] = 0
            analytics['feature_types'][feature_type] += 1
            
            if feature.updated_at:
                if not analytics['last_updated'] or feature.updated_at > analytics['last_updated']:
                    analytics['last_updated'] = feature.updated_at
        
        return analytics