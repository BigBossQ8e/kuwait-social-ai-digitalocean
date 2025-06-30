"""
Marshmallow Schemas for Kuwait Social AI
Data validation and serialization
"""

from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from marshmallow.decorators import post_load, pre_load
import re
from datetime import datetime, timedelta

# Custom validators
def validate_kuwait_phone(phone):
    """Validate Kuwait phone number format"""
    # Kuwait phone: +965 followed by 8 digits (mobile) or 7 digits (landline)
    pattern = r'^\+965[0-9]{7,8}$'
    if not re.match(pattern, phone):
        raise ValidationError('Invalid Kuwait phone number. Format: +965XXXXXXXX')

def validate_password_strength(password):
    """Validate password meets security requirements"""
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter')
    if not re.search(r'[0-9]', password):
        raise ValidationError('Password must contain at least one number')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character')

def validate_arabic_text(text):
    """Validate text contains Arabic characters"""
    if text and not re.search(r'[\u0600-\u06FF]', text):
        raise ValidationError('Text must contain Arabic characters')

def validate_instagram_handle(handle):
    """Validate Instagram handle format"""
    pattern = r'^[a-zA-Z0-9_.]{1,30}$'
    if not re.match(pattern, handle):
        raise ValidationError('Invalid Instagram handle format')

def validate_future_datetime(dt):
    """Validate datetime is in the future"""
    if dt <= datetime.utcnow():
        raise ValidationError('Scheduled time must be in the future')

# Base Schemas
class BaseSchema(Schema):
    """Base schema with common configurations"""
    class Meta:
        # Include unknown fields in deserialized output
        unknown = 'exclude'
        # Convert datetime to ISO format
        datetimeformat = 'iso'

# User Schemas
class UserRegistrationSchema(BaseSchema):
    """Schema for user registration"""
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(
        required=True,
        validate=[validate.Length(min=8, max=128), validate_password_strength],
        load_only=True
    )
    company_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=200),
        error_messages={'required': 'Company name is required'}
    )
    contact_name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=200)
    )
    phone = fields.Str(
        required=True,
        validate=validate_kuwait_phone
    )
    address = fields.Str(
        missing='',
        validate=validate.Length(max=500)
    )
    
    @validates('email')
    def validate_email_domain(self, value):
        """Additional email validation"""
        # Block disposable email domains
        disposable_domains = ['tempmail.com', 'throwaway.email', '10minutemail.com']
        domain = value.split('@')[1].lower()
        if domain in disposable_domains:
            raise ValidationError('Please use a permanent email address')

class UserLoginSchema(BaseSchema):
    """Schema for user login"""
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    remember_me = fields.Bool(missing=False)

class PasswordChangeSchema(BaseSchema):
    """Schema for password change"""
    current_password = fields.Str(required=True, load_only=True)
    new_password = fields.Str(
        required=True,
        validate=[validate.Length(min=8, max=128), validate_password_strength],
        load_only=True
    )
    
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        """Ensure new password is different from current"""
        if data.get('current_password') == data.get('new_password'):
            raise ValidationError('New password must be different from current password')

# Content Schemas
class ContentGenerationSchema(BaseSchema):
    """Schema for AI content generation"""
    prompt = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=1000),
        error_messages={'required': 'Content prompt is required'}
    )
    platform = fields.Str(
        missing='both',
        validate=validate.OneOf(['instagram', 'snapchat', 'both'])
    )
    tone = fields.Str(
        missing='professional',
        validate=validate.OneOf(['professional', 'casual', 'exciting', 'formal', 'friendly'])
    )
    include_arabic = fields.Bool(missing=True)
    content_type = fields.Str(
        missing='post',
        validate=validate.OneOf(['post', 'story', 'reel'])
    )
    include_hashtags = fields.Bool(missing=True)
    
    @validates('prompt')
    def validate_prompt_content(self, value):
        """Validate prompt doesn't contain inappropriate content"""
        inappropriate_words = ['spam', 'scam', 'illegal']
        if any(word in value.lower() for word in inappropriate_words):
            raise ValidationError('Content contains inappropriate terms')

class PostCreateSchema(BaseSchema):
    """Schema for creating a post"""
    content_type = fields.Str(
        required=True,
        validate=validate.OneOf(['text', 'image', 'video'])
    )
    caption_en = fields.Str(
        validate=validate.Length(max=2200),  # Instagram limit
        allow_none=True
    )
    caption_ar = fields.Str(
        validate=[validate.Length(max=2200), validate_arabic_text],
        allow_none=True
    )
    hashtags = fields.List(
        fields.Str(validate=validate.Regexp(r'^#[\w\u0600-\u06FF]+$')),
        validate=validate.Length(max=30)  # Instagram hashtag limit
    )
    scheduled_time = fields.DateTime(
        allow_none=True,
        validate=validate_future_datetime
    )
    social_account_id = fields.Int(allow_none=True)
    media_urls = fields.List(
        fields.Url(),
        validate=validate.Length(max=10)  # Instagram carousel limit
    )
    location = fields.Str(
        validate=validate.Length(max=100),
        allow_none=True
    )
    
    @validates_schema
    def validate_content(self, data, **kwargs):
        """Validate post has either caption or media"""
        if not data.get('caption_en') and not data.get('caption_ar') and not data.get('media_urls'):
            raise ValidationError('Post must have either caption or media')
        
        # Validate scheduled time is not during prayer times (simplified check)
        if data.get('scheduled_time'):
            hour = data['scheduled_time'].hour
            # Approximate prayer times in Kuwait (would be dynamic in production)
            prayer_hours = [5, 12, 15, 18, 19]  # Fajr, Dhuhr, Asr, Maghrib, Isha
            if hour in prayer_hours:
                raise ValidationError('Please avoid scheduling during prayer times')

class PostUpdateSchema(BaseSchema):
    """Schema for updating a post"""
    caption_en = fields.Str(validate=validate.Length(max=2200))
    caption_ar = fields.Str(validate=[validate.Length(max=2200), validate_arabic_text])
    hashtags = fields.List(
        fields.Str(validate=validate.Regexp(r'^#[\w\u0600-\u06FF]+$')),
        validate=validate.Length(max=30)
    )
    scheduled_time = fields.DateTime(validate=validate_future_datetime)
    
    @pre_load
    def remove_empty_values(self, data, **kwargs):
        """Remove None values to allow partial updates"""
        return {k: v for k, v in data.items() if v is not None}

# Social Account Schemas
class SocialAccountConnectSchema(BaseSchema):
    """Schema for connecting social media account"""
    platform = fields.Str(
        required=True,
        validate=validate.OneOf(['instagram', 'snapchat', 'tiktok', 'twitter'])
    )
    access_token = fields.Str(required=True, load_only=True)
    refresh_token = fields.Str(load_only=True, allow_none=True)
    account_id = fields.Str(required=True)
    account_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    
    @validates('account_name')
    def validate_account_name(self, value):
        """Validate social media handle format"""
        if value.startswith('@'):
            value = value[1:]
        
        # Basic validation for social media handles
        if not re.match(r'^[a-zA-Z0-9_.]+$', value):
            raise ValidationError('Invalid account name format')

# Analytics Schemas
class AnalyticsQuerySchema(BaseSchema):
    """Schema for analytics queries"""
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    platform = fields.Str(
        validate=validate.OneOf(['all', 'instagram', 'snapchat']),
        missing='all'
    )
    metric_type = fields.Str(
        validate=validate.OneOf(['engagement', 'reach', 'growth', 'all']),
        missing='all'
    )
    
    @validates_schema
    def validate_date_range(self, data, **kwargs):
        """Validate date range"""
        if data['end_date'] < data['start_date']:
            raise ValidationError('End date must be after start date')
        
        # Maximum 90 days range
        delta = data['end_date'] - data['start_date']
        if delta.days > 90:
            raise ValidationError('Date range cannot exceed 90 days')

# Competitor Schemas
class CompetitorAddSchema(BaseSchema):
    """Schema for adding competitor"""
    competitor_handle = fields.Str(
        required=True,
        validate=[validate.Length(min=1, max=200), validate_instagram_handle]
    )
    platform = fields.Str(
        required=True,
        validate=validate.OneOf(['instagram', 'snapchat'])
    )
    
    @pre_load
    def clean_handle(self, data, **kwargs):
        """Remove @ symbol if present"""
        if 'competitor_handle' in data and data['competitor_handle'].startswith('@'):
            data['competitor_handle'] = data['competitor_handle'][1:]
        return data

# Payment Schemas
class PaymentSchema(BaseSchema):
    """Schema for payment processing"""
    plan = fields.Str(
        required=True,
        validate=validate.OneOf(['basic', 'professional', 'enterprise'])
    )
    payment_method = fields.Str(
        required=True,
        validate=validate.OneOf(['credit_card', 'debit_card', 'knet'])
    )
    billing_period = fields.Str(
        missing='monthly',
        validate=validate.OneOf(['monthly', 'yearly'])
    )
    coupon_code = fields.Str(
        validate=validate.Regexp(r'^[A-Z0-9]{4,20}$'),
        allow_none=True
    )
    
    @validates('coupon_code')
    def validate_coupon(self, value):
        """Validate coupon code format and expiry"""
        if value:
            # In production, check against database
            valid_coupons = ['KUWAIT2024', 'RAMADAN50', 'WELCOME20']
            if value not in valid_coupons:
                raise ValidationError('Invalid or expired coupon code')

# Telegram Integration Schemas
class TelegramLinkSchema(BaseSchema):
    """Schema for linking Telegram account"""
    code = fields.Str(
        required=True,
        validate=validate.Length(equal=64)  # Base64 encoded linking code
    )

class TelegramContentSchema(BaseSchema):
    """Schema for content received via Telegram"""
    message_type = fields.Str(
        required=True,
        validate=validate.OneOf(['text', 'voice', 'image', 'document', 'video'])
    )
    content = fields.Str(required=True)
    language = fields.Str(
        validate=validate.OneOf(['en', 'ar', 'auto']),
        missing='auto'
    )
    platform = fields.Str(
        validate=validate.OneOf(['instagram', 'snapchat', 'both']),
        missing='both'
    )

# Admin Schemas
class ClientManagementSchema(BaseSchema):
    """Schema for admin client management"""
    action = fields.Str(
        required=True,
        validate=validate.OneOf(['suspend', 'activate', 'delete', 'upgrade', 'downgrade'])
    )
    reason = fields.Str(
        validate=validate.Length(max=500),
        required_if_action=['suspend', 'delete']
    )
    new_plan = fields.Str(
        validate=validate.OneOf(['trial', 'basic', 'professional', 'enterprise']),
        required_if_action=['upgrade', 'downgrade']
    )
    gift_days = fields.Int(
        validate=validate.Range(min=1, max=365),
        allow_none=True
    )
    
    def required_if_action(self, actions):
        """Custom validator for conditional requirements"""
        def validator(value):
            if self.context.get('action') in actions and not value:
                raise ValidationError(f'This field is required when action is {self.context.get("action")}')
        return validator

class FeatureToggleSchema(BaseSchema):
    """Schema for toggling features"""
    feature_name = fields.Str(
        required=True,
        validate=validate.OneOf([
            'ai_content_generation',
            'competitor_analysis',
            'video_creation',
            'image_enhancement',
            'auto_scheduling',
            'telegram_integration',
            'advanced_analytics',
            'hygiene_ai'
        ])
    )
    enabled = fields.Bool(required=True)
    client_ids = fields.List(
        fields.Int(),
        allow_none=True,
        validate=validate.Length(min=1)
    )

# Support Ticket Schemas
class SupportTicketCreateSchema(BaseSchema):
    """Schema for creating support ticket"""
    subject = fields.Str(
        required=True,
        validate=validate.Length(min=5, max=200)
    )
    description = fields.Str(
        required=True,
        validate=validate.Length(min=20, max=5000)
    )
    category = fields.Str(
        missing='other',
        validate=validate.OneOf(['technical', 'billing', 'feature_request', 'content', 'other'])
    )
    priority = fields.Str(
        missing='medium',
        validate=validate.OneOf(['low', 'medium', 'high', 'urgent'])
    )
    attachments = fields.List(
        fields.Str(validate=validate.URL()),
        validate=validate.Length(max=5)
    )

# Response Schemas (for serialization)
class UserResponseSchema(BaseSchema):
    """Schema for user response"""
    id = fields.Int()
    email = fields.Email()
    role = fields.Str()
    company_name = fields.Str()
    subscription_plan = fields.Str()
    subscription_status = fields.Str()
    created_at = fields.DateTime()
    last_login = fields.DateTime(allow_none=True)

class PostResponseSchema(BaseSchema):
    """Schema for post response"""
    id = fields.Int()
    uuid = fields.UUID()
    content_type = fields.Str()
    caption_en = fields.Str()
    caption_ar = fields.Str()
    hashtags = fields.List(fields.Str())
    media_urls = fields.List(fields.Url())
    status = fields.Str()
    scheduled_time = fields.DateTime(allow_none=True)
    published_time = fields.DateTime(allow_none=True)
    platform_url = fields.Url(allow_none=True)
    analytics = fields.Nested('PostAnalyticsSchema', allow_none=True)
    created_at = fields.DateTime()

class PostAnalyticsSchema(BaseSchema):
    """Schema for post analytics"""
    impressions = fields.Int()
    reach = fields.Int()
    likes = fields.Int()
    comments = fields.Int()
    shares = fields.Int()
    saves = fields.Int()
    engagement_rate = fields.Float()
    
# Pagination Schema
class PaginationSchema(BaseSchema):
    """Schema for pagination parameters"""
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=20, validate=validate.Range(min=1, max=100))
    sort_by = fields.Str(missing='created_at')
    sort_order = fields.Str(
        missing='desc',
        validate=validate.OneOf(['asc', 'desc'])
    )

# Missing schemas for complete validation coverage

class ForgotPasswordSchema(BaseSchema):
    """Schema for forgot password request"""
    email = fields.Email(required=True, validate=validate.Length(max=255))
    
    @validates('email')
    def validate_email_format(self, value):
        """Additional email validation"""
        if not value or '@' not in value:
            raise ValidationError('Please provide a valid email address')
        # Ensure email is lowercase for consistency
        return value.lower()


class ResetPasswordSchema(BaseSchema):
    """Schema for password reset"""
    token = fields.Str(required=True, validate=validate.Length(min=20, max=200))
    password = fields.Str(required=True, validate=[
        validate.Length(min=8, max=128),
        validate_password_strength
    ])
    confirm_password = fields.Str(required=True)
    
    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        """Ensure passwords match"""
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError('Passwords do not match', field_names=['confirm_password'])
    
    @post_load
    def enhance_password_validation(self, data, **kwargs):
        """Use enhanced password validation if available"""
        try:
            from utils.password_strength import validate_password_enhanced
            error = validate_password_enhanced(data['password'])
            if error:
                raise ValidationError(error, field_names=['password'])
        except ImportError:
            pass  # Fall back to basic validation
        return data


class ContentValidationSchema(BaseSchema):
    """Schema for content validation request"""
    content = fields.Str(required=True, validate=validate.Length(min=1, max=5000))
    content_type = fields.Str(
        missing='post',
        validate=validate.OneOf(['post', 'story', 'reel', 'caption'])
    )
    platform = fields.Str(
        missing='instagram',
        validate=validate.OneOf(['instagram', 'snapchat', 'both'])
    )
    scheduled_time = fields.DateTime(missing=None)
    include_arabic = fields.Bool(missing=True)
    
    @validates('scheduled_time')
    def validate_scheduled_time(self, value):
        """Ensure scheduled time is in the future if provided"""
        if value and value <= datetime.utcnow():
            raise ValidationError('Scheduled time must be in the future')


class ContentEnhanceSchema(BaseSchema):
    """Schema for content enhancement request"""
    content = fields.Str(required=True, validate=validate.Length(min=1, max=5000))
    improvements = fields.List(
        fields.Str(validate=validate.OneOf([
            'engagement', 'hashtags', 'emoji', 'cultural', 'length',
            'grammar', 'tone', 'call_to_action', 'accessibility'
        ])),
        missing=['engagement', 'hashtags']
    )
    platform = fields.Str(
        missing='instagram',
        validate=validate.OneOf(['instagram', 'snapchat', 'both'])
    )
    target_audience = fields.Str(
        missing='general',
        validate=validate.OneOf(['general', 'youth', 'business', 'family', 'luxury'])
    )
    
    @validates('improvements')
    def validate_improvements(self, value):
        """Ensure at least one improvement is selected"""
        if not value:
            raise ValidationError('At least one improvement type must be selected')
        # Remove duplicates
        return list(set(value))


# Hashtag Strategy Schema
class HashtagStrategySchema(BaseSchema):
    """Schema for hashtag strategy"""
    strategy_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    description = fields.Str(allow_none=True)
    is_active = fields.Bool(missing=True)
    trending_hashtags = fields.List(fields.Dict(), dump_only=True)
    recommended_combinations = fields.List(fields.Dict(), dump_only=True)
    performance_metrics = fields.Dict(dump_only=True)


# Engagement Tool Schema  
class EngagementToolSchema(BaseSchema):
    """Schema for engagement tools configuration"""
    tool_type = fields.Str(
        required=True,
        validate=validate.OneOf(['auto_reply', 'comment_template', 'inbox_manager'])
    )
    is_enabled = fields.Bool(missing=True)
    configuration = fields.Dict(missing={})
    automation_rules = fields.List(fields.Dict(), allow_none=True)


# Export all schemas
__all__ = [
    'UserRegistrationSchema',
    'UserLoginSchema',
    'PasswordChangeSchema',
    'ContentGenerationSchema',
    'PostCreateSchema',
    'PostUpdateSchema',
    'SocialAccountConnectSchema',
    'AnalyticsQuerySchema',
    'CompetitorAddSchema',
    'PaymentSchema',
    'TelegramLinkSchema',
    'TelegramContentSchema',
    'ClientManagementSchema',
    'FeatureToggleSchema',
    'SupportTicketCreateSchema',
    'UserResponseSchema',
    'PostResponseSchema',
    'PostAnalyticsSchema',
    'PaginationSchema',
    'ForgotPasswordSchema',
    'ResetPasswordSchema',
    'ContentValidationSchema',
    'ContentEnhanceSchema',
    'HashtagStrategySchema',
    'EngagementToolSchema'
]