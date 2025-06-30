"""
Missing Model Definitions for Kuwait Social AI
These models are referenced throughout the codebase but were not defined
"""

from datetime import datetime
from sqlalchemy import func
from . import db


class Competitor(db.Model):
    """Competitor company/account being tracked"""
    __tablename__ = 'competitors'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False, index=True)
    
    # Basic information
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    website = db.Column(db.String(255))
    industry = db.Column(db.String(50))
    
    # Social media handles
    instagram_handle = db.Column(db.String(50))
    twitter_handle = db.Column(db.String(50))
    snapchat_handle = db.Column(db.String(50))
    tiktok_handle = db.Column(db.String(50))
    
    # Tracking settings
    is_active = db.Column(db.Boolean, default=True)
    tracking_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_analyzed = db.Column(db.DateTime)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', backref='competitors')
    
    def __repr__(self):
        return f'<Competitor {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'name': self.name,
            'description': self.description,
            'website': self.website,
            'industry': self.industry,
            'social_handles': {
                'instagram': self.instagram_handle,
                'twitter': self.twitter_handle,
                'snapchat': self.snapchat_handle,
                'tiktok': self.tiktok_handle
            },
            'is_active': self.is_active,
            'tracking_since': self.tracking_since.isoformat() if self.tracking_since else None,
            'last_analyzed': self.last_analyzed.isoformat() if self.last_analyzed else None
        }


class Campaign(db.Model):
    """Marketing campaign for organizing posts and tracking performance"""
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False, index=True)
    
    # Campaign details
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    campaign_type = db.Column(db.String(50))  # product_launch, seasonal, awareness, etc.
    
    # Campaign goals
    objective = db.Column(db.String(100))  # engagement, conversions, brand_awareness, etc.
    target_audience = db.Column(db.JSON)  # Demographics and interests
    budget = db.Column(db.Float)
    
    # Duration
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, active, paused, completed
    
    # Performance targets
    target_impressions = db.Column(db.Integer)
    target_engagement_rate = db.Column(db.Float)
    target_conversions = db.Column(db.Integer)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', backref='campaigns')
    # Remove the problematic relationship for now
    # posts = db.relationship('Post', backref='campaign', lazy='dynamic')
    scheduled_posts = db.relationship('ScheduledPost', backref='campaign', lazy='dynamic')
    
    def __repr__(self):
        return f'<Campaign {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'name': self.name,
            'description': self.description,
            'campaign_type': self.campaign_type,
            'objective': self.objective,
            'target_audience': self.target_audience,
            'budget': self.budget,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'targets': {
                'impressions': self.target_impressions,
                'engagement_rate': self.target_engagement_rate,
                'conversions': self.target_conversions
            },
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ScheduledPost(db.Model):
    """Posts scheduled for future publishing"""
    __tablename__ = 'scheduled_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False, index=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=True)
    
    # Content
    content = db.Column(db.Text, nullable=False)
    content_arabic = db.Column(db.Text)  # Arabic version if applicable
    media_urls = db.Column(db.JSON)  # List of media file URLs
    
    # Platform-specific content
    platform_content = db.Column(db.JSON)  # Platform-specific variations
    
    # Scheduling
    scheduled_for = db.Column(db.DateTime, nullable=False, index=True)
    timezone = db.Column(db.String(50), default='Asia/Kuwait')
    
    # Target platforms
    platforms = db.Column(db.JSON)  # ['instagram', 'twitter', 'snapchat', 'tiktok']
    
    # Hashtags
    hashtags = db.Column(db.JSON)  # List of hashtags
    
    # Status
    status = db.Column(db.String(20), default='scheduled')  # scheduled, publishing, published, failed, cancelled
    publish_attempts = db.Column(db.Integer, default=0)
    last_error = db.Column(db.Text)
    
    # Published posts references
    published_posts = db.Column(db.JSON)  # {platform: post_id} mapping after publishing
    
    # AI suggestions
    ai_generated = db.Column(db.Boolean, default=False)
    ai_suggestions = db.Column(db.JSON)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Relationships
    client = db.relationship('Client', backref='scheduled_posts')
    
    def __repr__(self):
        return f'<ScheduledPost {self.id} for {self.scheduled_for}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'campaign_id': self.campaign_id,
            'content': self.content,
            'content_arabic': self.content_arabic,
            'media_urls': self.media_urls,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'timezone': self.timezone,
            'platforms': self.platforms,
            'hashtags': self.hashtags,
            'status': self.status,
            'ai_generated': self.ai_generated,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
    
    def can_publish(self):
        """Check if the post is ready to be published"""
        return (
            self.status == 'scheduled' and
            self.scheduled_for <= datetime.utcnow() and
            self.publish_attempts < 3
        )

