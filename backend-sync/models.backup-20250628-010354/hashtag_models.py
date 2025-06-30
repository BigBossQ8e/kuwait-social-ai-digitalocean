"""
Hashtag Strategy Models for Kuwait Social AI
"""

from datetime import datetime
from sqlalchemy import func
from . import db


class HashtagGroup(db.Model):
    """Groups of hashtags for different content types"""
    __tablename__ = 'hashtag_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    hashtags = db.Column(db.JSON, nullable=False)  # List of hashtags
    category = db.Column(db.String(50))  # product_launch, weekly_offer, cultural, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Performance metrics
    total_uses = db.Column(db.Integer, default=0)
    avg_engagement_rate = db.Column(db.Float, default=0.0)
    
    # Relationships
    client = db.relationship('Client', backref='hashtag_groups')
    performance_records = db.relationship('HashtagPerformance', backref='group', lazy='dynamic')
    
    def __repr__(self):
        return f'<HashtagGroup {self.name}>'


class HashtagPerformance(db.Model):
    """Track performance metrics for individual hashtags"""
    __tablename__ = 'hashtag_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    hashtag = db.Column(db.String(100), nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('scheduled_posts.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('hashtag_groups.id'))
    
    # Performance metrics
    impressions = db.Column(db.Integer, default=0)
    reach = db.Column(db.Integer, default=0)
    engagement = db.Column(db.Integer, default=0)  # likes + comments + shares
    clicks = db.Column(db.Integer, default=0)
    saves = db.Column(db.Integer, default=0)
    
    # Calculated metrics
    engagement_rate = db.Column(db.Float, default=0.0)
    click_through_rate = db.Column(db.Float, default=0.0)
    
    # Metadata
    platform = db.Column(db.String(20))  # instagram, snapchat
    posted_at = db.Column(db.DateTime)
    measured_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client')
    post = db.relationship('ScheduledPost')
    
    def calculate_engagement_rate(self):
        """Calculate engagement rate"""
        if self.reach > 0:
            self.engagement_rate = (self.engagement / self.reach) * 100
        return self.engagement_rate


class CompetitorHashtag(db.Model):
    """Track hashtags used by competitors"""
    __tablename__ = 'competitor_hashtags'
    
    id = db.Column(db.Integer, primary_key=True)
    competitor_id = db.Column(db.Integer, db.ForeignKey('competitors.id'), nullable=False)
    hashtag = db.Column(db.String(100), nullable=False)
    
    # Usage metrics
    usage_count = db.Column(db.Integer, default=1)
    avg_engagement = db.Column(db.Float, default=0.0)
    best_performing_post = db.Column(db.JSON)  # Store post details
    
    # Trends
    is_trending = db.Column(db.Boolean, default=False)
    trend_score = db.Column(db.Float, default=0.0)  # 0-100 score
    
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    competitor = db.relationship('Competitor', backref='tracked_hashtags')
    
    def __repr__(self):
        return f'<CompetitorHashtag {self.hashtag} - {self.competitor.name}>'


class HashtagRecommendation(db.Model):
    """AI-generated hashtag recommendations"""
    __tablename__ = 'hashtag_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Recommendation details
    hashtag = db.Column(db.String(100), nullable=False)
    reason = db.Column(db.Text)  # Why this hashtag is recommended
    score = db.Column(db.Float)  # Recommendation score (0-100)
    category = db.Column(db.String(50))  # trending, competitor, industry, seasonal
    
    # Expected performance
    expected_reach = db.Column(db.Integer)
    expected_engagement_rate = db.Column(db.Float)
    
    # Metadata
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # For time-sensitive recommendations
    is_used = db.Column(db.Boolean, default=False)
    used_at = db.Column(db.DateTime)
    
    # Relationships
    client = db.relationship('Client')
    
    @property
    def is_expired(self):
        """Check if recommendation has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False


class HashtagTrend(db.Model):
    """Track hashtag trends in Kuwait"""
    __tablename__ = 'hashtag_trends'
    
    id = db.Column(db.Integer, primary_key=True)
    hashtag = db.Column(db.String(100), nullable=False, index=True)
    
    # Trend metrics
    popularity_score = db.Column(db.Float, default=0.0)  # 0-100
    growth_rate = db.Column(db.Float, default=0.0)  # Percentage growth
    peak_time = db.Column(db.Time)  # Best time to use this hashtag
    
    # Category
    category = db.Column(db.String(50))  # kuwait, ramadan, national_day, etc.
    is_seasonal = db.Column(db.Boolean, default=False)
    season_start = db.Column(db.Date)
    season_end = db.Column(db.Date)
    
    # Usage stats
    total_posts = db.Column(db.Integer, default=0)
    avg_engagement = db.Column(db.Float, default=0.0)
    top_accounts = db.Column(db.JSON)  # List of top accounts using this hashtag
    
    # Metadata
    first_trending = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<HashtagTrend {self.hashtag} - Score: {self.popularity_score}>'