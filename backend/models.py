"""
Database Models for Kuwait Social AI
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSON, UUID
import uuid

from extensions import db  # Moved to models/__init__.py

# Association tables
client_features = db.Table('client_features',
    db.Column('client_id', db.Integer, db.ForeignKey('clients.id'), primary_key=True),
    db.Column('feature_id', db.Integer, db.ForeignKey('features.id'), primary_key=True),
    db.Column('enabled', db.Boolean, default=True),
    db.Column('enabled_at', db.DateTime, default=datetime.utcnow)
)

class User(db.Model):
    """Base user model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), nullable=False)  # owner, admin, client
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    owner_profile = db.relationship('Owner', back_populates='user', uselist=False)
    admin_profile = db.relationship('Admin', back_populates='user', uselist=False)
    client_profile = db.relationship('Client', back_populates='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Owner(db.Model):
    """Platform owner model"""
    __tablename__ = 'owners'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    company_name = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    
    # Relationships
    user = db.relationship('User', back_populates='owner_profile')
    platform_settings = db.relationship('PlatformSettings', back_populates='owner')

class Admin(db.Model):
    """Admin user model"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    full_name = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    permissions = db.Column(JSON, default={})
    
    # Relationships
    user = db.relationship('User', back_populates='admin_profile')
    support_tickets = db.relationship('SupportTicket', back_populates='assigned_admin')

class Client(db.Model):
    """Client user model"""
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    company_name = db.Column(db.String(200), nullable=False)
    contact_name = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    
    # Subscription info
    subscription_plan = db.Column(db.String(50), default='trial')  # trial, basic, pro, enterprise
    subscription_status = db.Column(db.String(20), default='active')  # active, suspended, cancelled
    subscription_start = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_end = db.Column(db.DateTime)
    
    # Usage limits
    monthly_posts_limit = db.Column(db.Integer, default=100)
    monthly_posts_used = db.Column(db.Integer, default=0)
    
    # Telegram integration
    telegram_id = db.Column(db.String(50), unique=True)
    telegram_linked_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', back_populates='client_profile')
    social_accounts = db.relationship('SocialAccount', back_populates='client', cascade='all, delete-orphan')
    posts = db.relationship('Post', back_populates='client', cascade='all, delete-orphan')
    analytics = db.relationship('Analytics', back_populates='client')
    features = db.relationship('Feature', secondary=client_features, back_populates='clients')
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'contact_name': self.contact_name,
            'subscription_plan': self.subscription_plan,
            'subscription_status': self.subscription_status,
            'monthly_posts_remaining': self.monthly_posts_limit - self.monthly_posts_used,
            'telegram_linked': bool(self.telegram_id)
        }

class Feature(db.Model):
    """Platform features that can be toggled"""
    __tablename__ = 'features'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(200))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # ai, analytics, publishing, etc.
    is_premium = db.Column(db.Boolean, default=False)
    platform_enabled = db.Column(db.Boolean, default=True)
    
    # Relationships
    clients = db.relationship('Client', secondary=client_features, back_populates='features')

class SocialAccount(db.Model):
    """Connected social media accounts"""
    __tablename__ = 'social_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # instagram, snapchat
    account_id = db.Column(db.String(100))
    account_name = db.Column(db.String(200))
    access_token = db.Column(db.Text)  # Encrypted in production
    refresh_token = db.Column(db.Text)  # Encrypted in production
    token_expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    connected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', back_populates='social_accounts')
    posts = db.relationship('Post', back_populates='social_account')

class Post(db.Model):
    """Social media posts"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    social_account_id = db.Column(db.Integer, db.ForeignKey('social_accounts.id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=True)
    
    # Content
    content_type = db.Column(db.String(20))  # text, image, video
    caption_en = db.Column(db.Text)
    caption_ar = db.Column(db.Text)
    hashtags = db.Column(JSON, default=list)
    media_urls = db.Column(JSON, default=list)
    
    # Status
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, published, failed
    scheduled_time = db.Column(db.DateTime)
    published_time = db.Column(db.DateTime)
    
    # Platform specific
    platform_post_id = db.Column(db.String(100))
    platform_url = db.Column(db.String(500))
    
    # AI generation info
    ai_generated = db.Column(db.Boolean, default=False)
    ai_prompt = db.Column(db.Text)
    ai_model = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Campaign relationship
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=True)
    campaign = db.relationship("Campaign", back_populates="posts")
    
    # Relationships
    client = db.relationship('Client', back_populates='posts')
    social_account = db.relationship('SocialAccount', back_populates='posts')
    analytics = db.relationship('PostAnalytics', back_populates='post', uselist=False)

class PostAnalytics(db.Model):
    """Analytics for individual posts"""
    __tablename__ = 'post_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), unique=True)
    
    # Engagement metrics
    impressions = db.Column(db.Integer, default=0)
    reach = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    saves = db.Column(db.Integer, default=0)
    
    # Calculated metrics
    engagement_rate = db.Column(db.Float, default=0.0)
    
    # Snapchat specific
    screenshots = db.Column(db.Integer, default=0)
    story_views = db.Column(db.Integer, default=0)
    
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    post = db.relationship('Post', back_populates='analytics')

class Analytics(db.Model):
    """Overall analytics for clients"""
    __tablename__ = 'analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Daily metrics
    total_posts = db.Column(db.Integer, default=0)
    total_impressions = db.Column(db.Integer, default=0)
    total_reach = db.Column(db.Integer, default=0)
    total_engagement = db.Column(db.Integer, default=0)
    
    # Growth metrics
    followers_count = db.Column(db.Integer, default=0)
    followers_growth = db.Column(db.Integer, default=0)
    
    # Platform breakdown
    instagram_metrics = db.Column(JSON, default={})
    snapchat_metrics = db.Column(JSON, default={})
    
    # Relationships
    client = db.relationship('Client', back_populates='analytics')

class ContentTemplate(db.Model):
    """AI content generation templates"""
    __tablename__ = 'content_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    prompt_template = db.Column(db.Text, nullable=False)
    variables = db.Column(JSON, default=list)
    is_active = db.Column(db.Boolean, default=True)
    
    # Kuwait specific
    includes_arabic = db.Column(db.Boolean, default=True)
    cultural_guidelines = db.Column(db.Text)

class CompetitorAnalysis(db.Model):
    """Competitor tracking"""
    __tablename__ = 'competitor_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    competitor_handle = db.Column(db.String(200), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    
    # Metrics
    followers = db.Column(db.Integer)
    avg_engagement = db.Column(db.Float)
    posting_frequency = db.Column(db.Float)  # posts per week
    top_hashtags = db.Column(JSON, default=list)
    
    last_analyzed = db.Column(db.DateTime, default=datetime.utcnow)

class PlatformSettings(db.Model):
    """Global platform settings managed by owner"""
    __tablename__ = 'platform_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'))
    
    # API Keys (encrypted in production)
    instagram_client_id = db.Column(db.String(200))
    instagram_client_secret = db.Column(db.Text)
    snapchat_client_id = db.Column(db.String(200))
    snapchat_client_secret = db.Column(db.Text)
    openai_api_key = db.Column(db.Text)
    google_cloud_key = db.Column(db.Text)
    myfatoorah_api_key = db.Column(db.Text)
    
    # Platform settings
    maintenance_mode = db.Column(db.Boolean, default=False)
    allow_registration = db.Column(db.Boolean, default=True)
    default_trial_days = db.Column(db.Integer, default=7)
    
    # Kuwait specific
    prayer_times_enabled = db.Column(db.Boolean, default=True)
    ramadan_mode = db.Column(db.Boolean, default=False)
    
    # Relationships
    owner = db.relationship('Owner', back_populates='platform_settings')

class SupportTicket(db.Model):
    """Support tickets"""
    __tablename__ = 'support_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    assigned_admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    
    subject = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))  # technical, billing, feature_request, other
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Relationships
    client = db.relationship('Client', foreign_keys=[client_id])
    assigned_admin = db.relationship('Admin', back_populates='support_tickets')

class AuditLog(db.Model):
    """Audit trail for important actions"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.Integer)
    details = db.Column(JSON, default={})
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id])
# Translation Models
class Translation(db.Model):
    __tablename__ = "translations"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), nullable=False)
    locale = db.Column(db.String(10), nullable=False)
    value = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    __table_args__ = (db.UniqueConstraint("key", "locale", name="_key_locale_uc"),)

# Add missing model classes

# Missing models for analytics
class CustomerEngagement(db.Model):
    __tablename__ = 'customer_engagements'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

class Competitor(db.Model):
    __tablename__ = 'competitors'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    name = db.Column(db.String(100))
    social_handle = db.Column(db.String(100))
    platform = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HashtagPerformance(db.Model):
    __tablename__ = 'hashtag_performance'
    id = db.Column(db.Integer, primary_key=True)
    hashtag = db.Column(db.String(100))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    impressions = db.Column(db.Integer, default=0)
    engagement_rate = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HashtagStrategy(db.Model):
    __tablename__ = 'hashtag_strategies'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    strategy_name = db.Column(db.String(100))
    hashtags = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class KuwaitFeature(db.Model):
    __tablename__ = 'kuwait_features'
    id = db.Column(db.Integer, primary_key=True)
    feature_name = db.Column(db.String(100))
    description = db.Column(db.Text)
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Customer Engagement Models

# Engagement Models from backup
from datetime import datetime
from sqlalchemy import func

class CommentTemplate(db.Model):
    """AI-powered comment response templates"""
    __tablename__ = 'comment_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Template details
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # greeting, thank_you, apology, product_info, etc.
    intent = db.Column(db.String(50))  # question, complaint, praise, inquiry
    
    # Response templates
    template_en = db.Column(db.Text, nullable=False)
    template_ar = db.Column(db.Text)
    
    # Personalization tokens
    tokens = db.Column(db.JSON)  # {customer_name}, {product}, {order_number}, etc.
    
    # Usage tracking
    usage_count = db.Column(db.Integer, default=0)
    last_used = db.Column(db.DateTime)
    effectiveness_score = db.Column(db.Float, default=0.0)
    
    # AI customization
    tone = db.Column(db.String(20))  # formal, friendly, professional, casual
    include_emoji = db.Column(db.Boolean, default=False)
    max_length = db.Column(db.Integer, default=280)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', back_populates='comment_templates')
    suggested_messages = db.relationship('UnifiedInboxMessage', back_populates='suggested_template')
    
    def __repr__(self):
        return f'<CommentTemplate {self.name}>'


# Engagement Models (from backup)

class UnifiedInboxMessage(db.Model):
    """Unified inbox for all social media messages"""
    __tablename__ = 'unified_inbox_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Message source
    platform = db.Column(db.String(20), nullable=False)  # instagram, snapchat
    message_type = db.Column(db.String(20))  # comment, dm, mention, story_reply
    platform_message_id = db.Column(db.String(100), unique=True)
    
    # Message details
    sender_username = db.Column(db.String(100))
    sender_name = db.Column(db.String(200))
    sender_profile_pic = db.Column(db.String(500))
    is_verified_sender = db.Column(db.Boolean, default=False)
    
    # Content
    message_text = db.Column(db.Text)
    media_urls = db.Column(db.JSON)
    parent_post_id = db.Column(db.String(100))  # For comments
    parent_post_caption = db.Column(db.Text)
    
    # Analysis
    sentiment = db.Column(db.String(20))  # positive, negative, neutral
    intent = db.Column(db.String(50))  # question, complaint, praise, inquiry, spam
    language = db.Column(db.String(10))  # en, ar
    urgency_score = db.Column(db.Integer, default=0)  # 0-10
    
    # Response tracking
    is_read = db.Column(db.Boolean, default=False)
    is_responded = db.Column(db.Boolean, default=False)
    responded_at = db.Column(db.DateTime)
    response_text = db.Column(db.Text)
    response_time_minutes = db.Column(db.Integer)
    
    # AI suggestions
    suggested_response = db.Column(db.Text)
    suggested_template_id = db.Column(db.Integer, db.ForeignKey('comment_templates.id'))
    confidence_score = db.Column(db.Float)
    
    # Customer info
    is_existing_customer = db.Column(db.Boolean, default=False)
    customer_value_score = db.Column(db.Float)  # Based on past interactions
    
    # Metadata
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', back_populates='inbox_messages')
    suggested_template = db.relationship('CommentTemplate', back_populates='suggested_messages')
    thread_messages = db.relationship('MessageThread', back_populates='original_message', lazy='dynamic')
    
    def __repr__(self):
        return f'<UnifiedInboxMessage {self.platform} - {self.message_type}>'


class MessageThread(db.Model):
    """Thread of messages for conversations"""
    __tablename__ = 'message_threads'
    
    id = db.Column(db.Integer, primary_key=True)
    original_message_id = db.Column(db.Integer, db.ForeignKey('unified_inbox_messages.id'), nullable=False)
    
    # Message details
    sender_type = db.Column(db.String(20))  # customer, business
    message_text = db.Column(db.Text)
    
    # Metadata
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship back to UnifiedInboxMessage
    original_message = db.relationship("UnifiedInboxMessage", back_populates="thread_messages")
    
    def __repr__(self):
        return f'<MessageThread {self.sender_type}>'


class ResponseMetrics(db.Model):
    """Track engagement response metrics"""
    __tablename__ = 'response_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Time period
    date = db.Column(db.Date, nullable=False)
    
    # Volume metrics
    total_messages_received = db.Column(db.Integer, default=0)
    total_comments = db.Column(db.Integer, default=0)
    total_dms = db.Column(db.Integer, default=0)
    total_mentions = db.Column(db.Integer, default=0)
    
    # Response metrics
    messages_responded = db.Column(db.Integer, default=0)
    avg_response_time_minutes = db.Column(db.Float, default=0.0)
    response_rate = db.Column(db.Float, default=0.0)
    
    # Sentiment metrics
    positive_messages = db.Column(db.Integer, default=0)
    negative_messages = db.Column(db.Integer, default=0)
    neutral_messages = db.Column(db.Integer, default=0)
    
    # AI assistance metrics
    ai_suggestions_used = db.Column(db.Integer, default=0)
    ai_accuracy_score = db.Column(db.Float, default=0.0)
    
    # Customer satisfaction
    resolved_issues = db.Column(db.Integer, default=0)
    escalated_issues = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', back_populates='response_metrics')
    
    def __repr__(self):
        return f'<ResponseMetrics {self.date} - Client {self.client_id}>'


class CustomerProfile(db.Model):
    """Enhanced customer profiles from social interactions"""
    __tablename__ = 'customer_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Social identities
    instagram_username = db.Column(db.String(100), index=True)
    snapchat_username = db.Column(db.String(100), index=True)
    
    # Profile info
    display_name = db.Column(db.String(200))
    profile_pic = db.Column(db.String(500))
    is_verified = db.Column(db.Boolean, default=False)
    
    # Interaction history
    first_interaction = db.Column(db.DateTime)
    last_interaction = db.Column(db.DateTime)
    total_interactions = db.Column(db.Integer, default=0)
    
    # Engagement metrics
    total_comments = db.Column(db.Integer, default=0)
    total_dms = db.Column(db.Integer, default=0)
    total_mentions = db.Column(db.Integer, default=0)
    total_purchases = db.Column(db.Integer, default=0)
    
    # Sentiment analysis
    avg_sentiment_score = db.Column(db.Float, default=0.0)
    loyalty_score = db.Column(db.Float, default=0.0)  # 0-100
    influence_score = db.Column(db.Float, default=0.0)  # Based on followers, engagement
    
    # Preferences
    preferred_language = db.Column(db.String(10))
    preferred_contact_time = db.Column(db.Time)
    interests = db.Column(db.JSON)  # Inferred from interactions
    
    # Customer value
    lifetime_value = db.Column(db.Float, default=0.0)
    churn_risk_score = db.Column(db.Float, default=0.0)  # 0-100
    
    # Tags and notes
    tags = db.Column(db.JSON)  # VIP, frequent_buyer, complainer, advocate
    internal_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', back_populates='customer_profiles')
    
    def __repr__(self):
        return f'<CustomerProfile {self.display_name or self.instagram_username}>'


class EngagementAutomation(db.Model):
    """Automation rules for customer engagement"""
    __tablename__ = 'engagement_automations'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Rule details
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Trigger conditions
    trigger_type = db.Column(db.String(50))  # keyword, sentiment, time, customer_tag
    trigger_conditions = db.Column(db.JSON)
    
    # Actions
    action_type = db.Column(db.String(50))  # auto_reply, tag_customer, notify_team, escalate
    action_config = db.Column(db.JSON)
    
    # Scheduling
    is_active = db.Column(db.Boolean, default=True)
    active_days = db.Column(db.JSON)  # ['monday', 'tuesday', ...]
    active_hours_start = db.Column(db.Time)

# Kuwait Features Models
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


class Campaign(db.Model):
    __tablename__ = "campaigns"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship("Post", back_populates="campaign")
