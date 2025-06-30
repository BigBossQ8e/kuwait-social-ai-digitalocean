"""
Kuwait-Specific Feature Models for Kuwait Social AI
"""

from datetime import datetime, date
from sqlalchemy import func
from . import db


class KuwaitFeature(db.Model):
    """Kuwait-specific features and functionality"""
    __tablename__ = 'kuwait_features'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Feature configuration
    feature_type = db.Column(db.String(50), nullable=False)  # prayer_times, local_events, cultural_content, etc.
    is_enabled = db.Column(db.Boolean, default=True)
    
    # Prayer time settings
    show_prayer_times = db.Column(db.Boolean, default=False)
    prayer_time_format = db.Column(db.String(20), default='12h')  # 12h or 24h
    include_prayer_reminders = db.Column(db.Boolean, default=False)
    
    # Local content preferences
    preferred_language = db.Column(db.String(10), default='both')  # ar, en, both
    include_local_holidays = db.Column(db.Boolean, default=True)
    include_cultural_events = db.Column(db.Boolean, default=True)
    
    # Regional targeting
    target_regions = db.Column(db.JSON)  # List of Kuwait regions
    local_dialect_preference = db.Column(db.Boolean, default=False)
    
    # Cultural sensitivity
    cultural_filter_level = db.Column(db.String(20), default='moderate')  # strict, moderate, relaxed
    include_national_content = db.Column(db.Boolean, default=True)
    
    # Business hours
    business_hours_kuwait = db.Column(db.JSON)  # Kuwait-specific business hours
    weekend_days = db.Column(db.JSON, default=['Friday', 'Saturday'])
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', back_populates='kuwait_features')
    
    def __repr__(self):
        return f'<KuwaitFeature {self.feature_type} for Client {self.client_id}>'


class KuwaitEvent(db.Model):
    """Local Kuwait events calendar"""
    __tablename__ = 'kuwait_events'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Event details
    name_en = db.Column(db.String(200), nullable=False)
    name_ar = db.Column(db.String(200))
    description_en = db.Column(db.Text)
    description_ar = db.Column(db.Text)
    
    # Event type
    category = db.Column(db.String(50))  # national, religious, cultural, sports, shopping
    is_public_holiday = db.Column(db.Boolean, default=False)
    is_shopping_event = db.Column(db.Boolean, default=False)
    
    # Dates
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_rule = db.Column(db.String(100))  # yearly, monthly, lunar
    
    # Content suggestions
    content_themes = db.Column(db.JSON)  # List of relevant content themes
    suggested_hashtags = db.Column(db.JSON)
    color_scheme = db.Column(db.JSON)  # Suggested colors for the event
    
    # Historical data
    typical_engagement_boost = db.Column(db.Float)  # Percentage increase in engagement
    best_posting_times = db.Column(db.JSON)
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<KuwaitEvent {self.name_en}>'


class KuwaitHistoricalFact(db.Model):
    """'On This Day in Kuwait' historical facts"""
    __tablename__ = 'kuwait_historical_facts'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Date (month and day only for yearly recurrence)
    month = db.Column(db.Integer, nullable=False)
    day = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer)  # Optional, for specific year events
    
    # Fact details
    title_en = db.Column(db.String(200), nullable=False)
    title_ar = db.Column(db.String(200))
    description_en = db.Column(db.Text, nullable=False)
    description_ar = db.Column(db.Text)
    
    # Categories
    category = db.Column(db.String(50))  # independence, cultural, economic, sports, achievement
    significance_level = db.Column(db.Integer)  # 1-5, how important
    
    # Media
    image_url = db.Column(db.String(500))
    video_url = db.Column(db.String(500))
    source_url = db.Column(db.String(500))
    
    # Content generation
    talking_points = db.Column(db.JSON)  # Key points for content
    suggested_captions = db.Column(db.JSON)
    relevant_hashtags = db.Column(db.JSON)
    
    # Usage tracking
    times_used = db.Column(db.Integer, default=0)
    avg_engagement_rate = db.Column(db.Float, default=0.0)
    
    is_verified = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<KuwaitHistoricalFact {self.month}/{self.day} - {self.title_en}>'


class KuwaitTrendingTopic(db.Model):
    """Trending topics specific to Kuwait"""
    __tablename__ = 'kuwait_trending_topics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Topic details
    topic = db.Column(db.String(100), nullable=False)
    topic_ar = db.Column(db.String(100))
    description = db.Column(db.Text)
    
    # Trending data
    platform = db.Column(db.String(20))  # instagram, snapchat, twitter, general
    trend_score = db.Column(db.Float)  # 0-100
    volume = db.Column(db.Integer)  # Number of posts/mentions
    growth_rate = db.Column(db.Float)  # Percentage growth
    
    # Category
    category = db.Column(db.String(50))  # news, entertainment, sports, politics, lifestyle
    sentiment = db.Column(db.String(20))  # positive, negative, neutral, mixed
    
    # Related content
    related_hashtags = db.Column(db.JSON)
    example_posts = db.Column(db.JSON)
    key_influencers = db.Column(db.JSON)
    
    # Time sensitivity
    started_trending = db.Column(db.DateTime)
    peak_time = db.Column(db.DateTime)
    expected_duration_hours = db.Column(db.Integer)
    
    # Content suggestions
    content_angles = db.Column(db.JSON)  # Different ways to approach the topic
    do_not_mention = db.Column(db.JSON)  # Sensitive aspects to avoid
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<KuwaitTrendingTopic {self.topic}>'


class KuwaitBusinessDirectory(db.Model):
    """Directory of Kuwait businesses for collaboration and benchmarking"""
    __tablename__ = 'kuwait_business_directory'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Business details
    name_en = db.Column(db.String(200), nullable=False)
    name_ar = db.Column(db.String(200))
    category = db.Column(db.String(100))  # restaurant, retail, service, etc.
    subcategory = db.Column(db.String(100))
    
    # Location
    area = db.Column(db.String(100))  # Salmiya, Kuwait City, Hawalli, etc.
    full_address = db.Column(db.Text)
    google_maps_url = db.Column(db.String(500))
    
    # Social media presence
    instagram_handle = db.Column(db.String(100))
    snapchat_handle = db.Column(db.String(100))
    follower_count = db.Column(db.Integer)
    engagement_rate = db.Column(db.Float)
    
    # Business info
    established_year = db.Column(db.Integer)
    is_local_brand = db.Column(db.Boolean, default=True)
    is_franchise = db.Column(db.Boolean, default=False)
    
    # Collaboration potential
    collaboration_score = db.Column(db.Float)  # 0-100
    past_collaborations = db.Column(db.JSON)
    collaboration_types = db.Column(db.JSON)  # cross_promotion, giveaway, event
    
    # Performance benchmarks
    avg_post_frequency = db.Column(db.Float)  # Posts per week
    peak_posting_times = db.Column(db.JSON)
    top_performing_content = db.Column(db.JSON)
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<KuwaitBusinessDirectory {self.name_en}>'


class CulturalGuideline(db.Model):
    """Cultural guidelines for content creation in Kuwait"""
    __tablename__ = 'cultural_guidelines'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Guideline details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))  # religious, social, business, language
    
    # Rules
    do_rules = db.Column(db.JSON)  # What to do
    dont_rules = db.Column(db.JSON)  # What not to do
    
    # Examples
    good_examples = db.Column(db.JSON)
    bad_examples = db.Column(db.JSON)
    
    # Context
    applies_to = db.Column(db.JSON)  # industries, content types
    exceptions = db.Column(db.JSON)
    seasonal_relevance = db.Column(db.JSON)  # More important during certain times
    
    # Severity
    importance_level = db.Column(db.Integer)  # 1-5
    violation_impact = db.Column(db.String(20))  # low, medium, high, severe
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CulturalGuideline {self.title}>'


class LocalInfluencer(db.Model):
    """Kuwait social media influencers database"""
    __tablename__ = 'local_influencers'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Influencer details
    name = db.Column(db.String(200), nullable=False)
    instagram_handle = db.Column(db.String(100), unique=True)
    snapchat_handle = db.Column(db.String(100))
    
    # Metrics
    instagram_followers = db.Column(db.Integer)
    snapchat_followers = db.Column(db.Integer)
    avg_engagement_rate = db.Column(db.Float)
    
    # Categories
    primary_category = db.Column(db.String(50))  # fashion, food, lifestyle, tech
    secondary_categories = db.Column(db.JSON)
    
    # Audience
    audience_gender_split = db.Column(db.JSON)  # {'male': 40, 'female': 60}
    audience_age_groups = db.Column(db.JSON)  # {'18-24': 30, '25-34': 50, ...}
    audience_interests = db.Column(db.JSON)
    
    # Collaboration
    collaboration_rate_range = db.Column(db.String(50))  # budget range
    preferred_collaboration_types = db.Column(db.JSON)
    past_brand_collaborations = db.Column(db.JSON)
    
    # Content style
    content_language = db.Column(db.String(20))  # en, ar, mixed
    content_tone = db.Column(db.String(50))  # professional, casual, humorous
    posting_frequency = db.Column(db.Float)  # Posts per week
    
    # Reputation
    reputation_score = db.Column(db.Float)  # 0-100
    controversy_flag = db.Column(db.Boolean, default=False)
    verified_status = db.Column(db.Boolean, default=False)
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LocalInfluencer {self.name}>'