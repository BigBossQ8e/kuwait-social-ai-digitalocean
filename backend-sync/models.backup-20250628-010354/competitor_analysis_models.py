"""
Enhanced Competitor Analysis Models for Kuwait Social AI
"""

from datetime import datetime
from sqlalchemy import func
from . import db


class CompetitorContent(db.Model):
    """Track competitor content for analysis"""
    __tablename__ = 'competitor_content'
    
    id = db.Column(db.Integer, primary_key=True)
    competitor_id = db.Column(db.Integer, db.ForeignKey('competitors.id'), nullable=False)
    platform = db.Column(db.String(20), nullable=False)
    post_id = db.Column(db.String(100), unique=True)  # Platform-specific post ID
    
    # Content details
    content_type = db.Column(db.String(50))  # photo, video, carousel, story, reel
    caption = db.Column(db.Text)
    hashtags = db.Column(db.JSON)
    mentions = db.Column(db.JSON)
    
    # Media analysis
    media_urls = db.Column(db.JSON)
    dominant_colors = db.Column(db.JSON)  # For visual branding analysis
    contains_text = db.Column(db.Boolean, default=False)
    contains_people = db.Column(db.Boolean, default=False)
    contains_product = db.Column(db.Boolean, default=False)
    
    # Performance metrics
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    saves = db.Column(db.Integer, default=0)
    reach = db.Column(db.Integer, default=0)
    impressions = db.Column(db.Integer, default=0)
    
    # Calculated metrics
    engagement_rate = db.Column(db.Float, default=0.0)
    virality_score = db.Column(db.Float, default=0.0)
    
    # Timing
    posted_at = db.Column(db.DateTime, nullable=False)
    posted_day = db.Column(db.String(10))  # Monday, Tuesday, etc.
    posted_hour = db.Column(db.Integer)  # 0-23
    
    # AI Analysis
    content_category = db.Column(db.String(50))  # product_launch, promotion, educational, etc.
    detected_products = db.Column(db.JSON)
    brand_sentiment = db.Column(db.String(20))  # positive, negative, neutral
    
    # Metadata
    is_ad = db.Column(db.Boolean, default=False)
    is_collaboration = db.Column(db.Boolean, default=False)
    collaboration_brands = db.Column(db.JSON)
    
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    competitor = db.relationship('Competitor', backref='content')
    sentiment_analysis = db.relationship('CompetitorSentiment', backref='content', lazy='dynamic')
    
    def __repr__(self):
        return f'<CompetitorContent {self.competitor.name} - {self.content_type}>'


class CompetitorSentiment(db.Model):
    """Sentiment analysis for competitor content comments"""
    __tablename__ = 'competitor_sentiment'
    
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('competitor_content.id'), nullable=False)
    
    # Comment details
    comment_text = db.Column(db.Text)
    comment_author = db.Column(db.String(100))
    comment_likes = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Sentiment analysis
    sentiment = db.Column(db.String(20))  # positive, negative, neutral
    sentiment_score = db.Column(db.Float)  # -1 to 1
    emotions = db.Column(db.JSON)  # joy, anger, sadness, etc.
    
    # Topic analysis
    topics = db.Column(db.JSON)  # product_quality, customer_service, pricing, etc.
    is_question = db.Column(db.Boolean, default=False)
    is_complaint = db.Column(db.Boolean, default=False)
    is_praise = db.Column(db.Boolean, default=False)
    
    # Language
    language = db.Column(db.String(10))
    is_arabic = db.Column(db.Boolean, default=False)
    
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CompetitorSentiment {self.sentiment}>'


class CompetitorAd(db.Model):
    """Track competitor advertising campaigns"""
    __tablename__ = 'competitor_ads'
    
    id = db.Column(db.Integer, primary_key=True)
    competitor_id = db.Column(db.Integer, db.ForeignKey('competitors.id'), nullable=False)
    platform = db.Column(db.String(20), nullable=False)
    
    # Ad details
    ad_id = db.Column(db.String(100))
    ad_type = db.Column(db.String(50))  # image, video, carousel, collection
    ad_objective = db.Column(db.String(50))  # awareness, traffic, conversions, etc.
    
    # Creative
    headline = db.Column(db.String(200))
    primary_text = db.Column(db.Text)
    call_to_action = db.Column(db.String(50))
    landing_page_url = db.Column(db.String(500))
    
    # Targeting (inferred)
    target_audience = db.Column(db.JSON)  # demographics, interests
    target_locations = db.Column(db.JSON)
    
    # Performance (if available)
    estimated_reach = db.Column(db.Integer)
    estimated_impressions = db.Column(db.Integer)
    
    # Duration
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Analysis
    creative_elements = db.Column(db.JSON)  # colors, text, offers
    offer_type = db.Column(db.String(50))  # discount, free_shipping, bundle, etc.
    urgency_indicators = db.Column(db.JSON)  # limited_time, last_chance, etc.
    
    # Relationships
    competitor = db.relationship('Competitor', backref='ads')
    
    def __repr__(self):
        return f'<CompetitorAd {self.competitor.name} - {self.ad_type}>'


class CompetitorStrategy(db.Model):
    """AI-inferred competitor strategies"""
    __tablename__ = 'competitor_strategies'
    
    id = db.Column(db.Integer, primary_key=True)
    competitor_id = db.Column(db.Integer, db.ForeignKey('competitors.id'), nullable=False)
    
    # Strategy identification
    strategy_type = db.Column(db.String(50))  # content, pricing, product, marketing
    strategy_name = db.Column(db.String(100))
    confidence_score = db.Column(db.Float)  # 0-100
    
    # Details
    description = db.Column(db.Text)
    key_indicators = db.Column(db.JSON)  # What led to this inference
    examples = db.Column(db.JSON)  # Example posts/content
    
    # Timing
    identified_at = db.Column(db.DateTime, default=datetime.utcnow)
    active_since = db.Column(db.DateTime)
    active_until = db.Column(db.DateTime)
    
    # Impact
    effectiveness_score = db.Column(db.Float)  # 0-100
    threat_level = db.Column(db.String(20))  # low, medium, high
    
    # Recommendations
    counter_strategies = db.Column(db.JSON)
    opportunities = db.Column(db.JSON)
    
    # Relationships
    competitor = db.relationship('Competitor', backref='strategies')
    
    def __repr__(self):
        return f'<CompetitorStrategy {self.strategy_name}>'


class ContentComparison(db.Model):
    """Compare client content with competitor content"""
    __tablename__ = 'content_comparisons'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    competitor_id = db.Column(db.Integer, db.ForeignKey('competitors.id'), nullable=False)
    
    # Comparison period
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    
    # Content metrics
    client_post_count = db.Column(db.Integer, default=0)
    competitor_post_count = db.Column(db.Integer, default=0)
    
    client_avg_engagement = db.Column(db.Float, default=0.0)
    competitor_avg_engagement = db.Column(db.Float, default=0.0)
    
    # Content type distribution
    client_content_types = db.Column(db.JSON)
    competitor_content_types = db.Column(db.JSON)
    
    # Posting patterns
    client_posting_times = db.Column(db.JSON)
    competitor_posting_times = db.Column(db.JSON)
    
    # Topic analysis
    client_topics = db.Column(db.JSON)
    competitor_topics = db.Column(db.JSON)
    shared_topics = db.Column(db.JSON)
    unique_client_topics = db.Column(db.JSON)
    unique_competitor_topics = db.Column(db.JSON)
    
    # Performance gaps
    engagement_gap = db.Column(db.Float)  # Positive means client is better
    reach_gap = db.Column(db.Float)
    growth_gap = db.Column(db.Float)
    
    # Insights
    key_insights = db.Column(db.JSON)
    recommendations = db.Column(db.JSON)
    
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client')
    competitor = db.relationship('Competitor')
    
    def __repr__(self):
        return f'<ContentComparison {self.client.business_name} vs {self.competitor.name}>'