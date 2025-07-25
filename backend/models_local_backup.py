"""
Database Models for Kuwait Social AI
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSON, UUID
import uuid
from extensions import db

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