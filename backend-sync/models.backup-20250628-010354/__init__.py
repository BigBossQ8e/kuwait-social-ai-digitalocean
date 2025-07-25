"""
Models package for Kuwait Social AI
This file imports all models and the database instance for easy access
"""

from flask_sqlalchemy import SQLAlchemy

# Create the database instance
db = SQLAlchemy()

# Import core models
from .core import (
    User, Owner, Admin, Client, AuditLog,
    client_features, Feature, SocialAccount, Post, PostAnalytics,
    Analytics, ContentTemplate, CompetitorAnalysisOld,
    PlatformSettings, SupportTicket
)

# Import models from submodules
from .api_key import APIKey
from .client_error import ClientError
from .missing_models import Competitor, Campaign, ScheduledPost
from .competitor_analysis_models import CompetitorContent
from .engagement_models import (
    CustomerEngagement, CommentTemplate, UnifiedInboxMessage, MessageThread, 
    ResponseMetrics, CustomerProfile, EngagementAutomation
)
from .hashtag_models import (
    HashtagGroup, HashtagPerformance, CompetitorHashtag, 
    HashtagRecommendation, HashtagTrend
)
from .kuwait_features_models import (
    KuwaitFeature, KuwaitEvent, KuwaitHistoricalFact, KuwaitTrendingTopic,
    KuwaitBusinessDirectory, CulturalGuideline, LocalInfluencer
)
from .normalized_models import (
    CompetitorAnalysis, CompetitorTopHashtag, CompetitorTopPost, 
    CompetitorAudienceDemographic, HashtagStrategy, TrendingHashtag, 
    HashtagCombination, HashtagCombinationItem
)
from .reporting_models import (
    ReportTemplate, GeneratedReport, ROITracking,
    AnalyticsDashboard, MetricAlert, BenchmarkData
)

# Export all models
__all__ = [
    # Database instance
    'db',
    
    # Core models
    'User', 'Owner', 'Admin', 'Client', 'AuditLog',
    'client_features', 'Feature', 'SocialAccount', 'Post', 'PostAnalytics',
    'Analytics', 'ContentTemplate', 'CompetitorAnalysisOld',
    'PlatformSettings', 'SupportTicket',
    
    # API and error models
    'APIKey', 'ClientError',
    
    # Core missing models
    'Competitor', 'Campaign', 'ScheduledPost',
    
    # Competitor analysis models
    'CompetitorContent',
    
    # Engagement models
    'CustomerEngagement', 'CommentTemplate', 'UnifiedInboxMessage', 'MessageThread',
    'ResponseMetrics', 'CustomerProfile', 'EngagementAutomation',
    
    # Hashtag models
    'HashtagGroup', 'HashtagPerformance', 'CompetitorHashtag',
    'HashtagRecommendation', 'HashtagTrend',
    
    # Kuwait features models
    'KuwaitFeature', 'KuwaitEvent', 'KuwaitHistoricalFact', 'KuwaitTrendingTopic',
    'KuwaitBusinessDirectory', 'CulturalGuideline', 'LocalInfluencer',
    
    # Normalized models
    'CompetitorAnalysis', 'CompetitorTopHashtag', 'CompetitorTopPost',
    'CompetitorAudienceDemographic', 'HashtagStrategy', 'TrendingHashtag', 
    'HashtagCombination', 'HashtagCombinationItem',
    
    # Reporting models
    'ReportTemplate', 'GeneratedReport', 'ROITracking',
    'AnalyticsDashboard', 'MetricAlert', 'BenchmarkData'
]