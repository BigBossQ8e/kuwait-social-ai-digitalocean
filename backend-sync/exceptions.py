"""
Custom exceptions for Kuwait Social AI
"""

class KuwaitSocialAIException(Exception):
    """Base exception for all Kuwait Social AI exceptions"""
    status_code = 500
    error_code = 'INTERNAL_ERROR'
    
    def __init__(self, message=None, status_code=None, error_code=None, details=None):
        super().__init__(message)
        self.message = message or 'An error occurred'
        self.status_code = status_code or self.status_code
        self.error_code = error_code or self.error_code
        self.details = details or {}
    
    def to_dict(self):
        """Convert exception to dictionary for JSON response"""
        return {
            'error': self.message,
            'error_code': self.error_code,
            'details': self.details
        }

# Content Generation Exceptions
class ContentGenerationException(KuwaitSocialAIException):
    """Base exception for content generation errors"""
    status_code = 500
    error_code = 'CONTENT_GENERATION_ERROR'

class TranslationException(ContentGenerationException):
    """Exception for translation failures"""
    status_code = 503
    error_code = 'TRANSLATION_FAILED'
    
    def __init__(self, source_lang='en', target_lang='ar', original_text=None, attempted_services=None):
        message = f'Failed to translate from {source_lang} to {target_lang}'
        details = {
            'source_language': source_lang,
            'target_language': target_lang,
            'attempted_services': attempted_services or [],
            'original_text_length': len(original_text) if original_text else 0
        }
        super().__init__(message=message, details=details)

class AIServiceException(ContentGenerationException):
    """Exception for AI service failures"""
    status_code = 503
    error_code = 'AI_SERVICE_ERROR'
    
    def __init__(self, service='OpenAI', reason=None):
        message = f'{service} service is currently unavailable'
        details = {
            'service': service,
            'reason': reason
        }
        super().__init__(message=message, details=details)

class ContentModerationException(ContentGenerationException):
    """Exception for content that fails moderation"""
    status_code = 422
    error_code = 'CONTENT_MODERATION_FAILED'
    
    def __init__(self, violations=None, suggestions=None):
        message = 'Content violates community guidelines'
        details = {
            'violations': violations or [],
            'suggestions': suggestions or []
        }
        super().__init__(message=message, details=details)

# Image Processing Exceptions
class ImageProcessingException(KuwaitSocialAIException):
    """Base exception for image processing errors"""
    status_code = 422
    error_code = 'IMAGE_PROCESSING_ERROR'

class InvalidImageException(ImageProcessingException):
    """Exception for invalid image files"""
    status_code = 400
    error_code = 'INVALID_IMAGE'
    
    def __init__(self, reason=None, supported_formats=None):
        message = 'Invalid image file'
        details = {
            'reason': reason,
            'supported_formats': supported_formats or ['jpg', 'jpeg', 'png', 'gif']
        }
        super().__init__(message=message, details=details)

class ImageSizeException(ImageProcessingException):
    """Exception for image size issues"""
    status_code = 413
    error_code = 'IMAGE_SIZE_ERROR'
    
    def __init__(self, current_size=None, max_size=None):
        message = 'Image size exceeds maximum allowed'
        details = {
            'current_size_mb': current_size,
            'max_size_mb': max_size
        }
        super().__init__(message=message, details=details)

# Social Media Exceptions
class SocialMediaException(KuwaitSocialAIException):
    """Base exception for social media API errors"""
    status_code = 503
    error_code = 'SOCIAL_MEDIA_ERROR'

class InstagramAPIException(SocialMediaException):
    """Exception for Instagram API failures"""
    error_code = 'INSTAGRAM_API_ERROR'
    
    def __init__(self, reason=None, api_error_code=None):
        message = 'Instagram API error'
        details = {
            'platform': 'instagram',
            'reason': reason,
            'api_error_code': api_error_code
        }
        super().__init__(message=message, details=details)

class SnapchatAPIException(SocialMediaException):
    """Exception for Snapchat API failures"""
    error_code = 'SNAPCHAT_API_ERROR'
    
    def __init__(self, reason=None, api_error_code=None):
        message = 'Snapchat API error'
        details = {
            'platform': 'snapchat',
            'reason': reason,
            'api_error_code': api_error_code
        }
        super().__init__(message=message, details=details)

class SocialAccountNotConnectedException(SocialMediaException):
    """Exception when social account is not connected"""
    status_code = 400
    error_code = 'SOCIAL_ACCOUNT_NOT_CONNECTED'
    
    def __init__(self, platform=None):
        message = f'No {platform} account connected' if platform else 'No social account connected'
        details = {
            'platform': platform,
            'action_required': 'connect_account'
        }
        super().__init__(message=message, details=details)

# Authentication Exceptions
class AuthenticationException(KuwaitSocialAIException):
    """Base exception for authentication errors"""
    status_code = 401
    error_code = 'AUTHENTICATION_ERROR'

class InvalidCredentialsException(AuthenticationException):
    """Exception for invalid login credentials"""
    error_code = 'INVALID_CREDENTIALS'
    
    def __init__(self):
        super().__init__(message='Invalid email or password')

class AccountSuspendedException(AuthenticationException):
    """Exception for suspended accounts"""
    status_code = 403
    error_code = 'ACCOUNT_SUSPENDED'
    
    def __init__(self, reason=None, suspended_until=None):
        message = 'Account has been suspended'
        details = {
            'reason': reason,
            'suspended_until': suspended_until.isoformat() if suspended_until else None
        }
        super().__init__(message=message, details=details)

class TokenExpiredException(AuthenticationException):
    """Exception for expired tokens"""
    error_code = 'TOKEN_EXPIRED'
    
    def __init__(self):
        super().__init__(message='Authentication token has expired')

# Subscription Exceptions
class SubscriptionException(KuwaitSocialAIException):
    """Base exception for subscription issues"""
    status_code = 403
    error_code = 'SUBSCRIPTION_ERROR'

class SubscriptionExpiredException(SubscriptionException):
    """Exception for expired subscriptions"""
    error_code = 'SUBSCRIPTION_EXPIRED'
    
    def __init__(self, expired_date=None, renewal_url=None):
        message = 'Your subscription has expired'
        details = {
            'expired_date': expired_date.isoformat() if expired_date else None,
            'renewal_url': renewal_url or '/pricing'
        }
        super().__init__(message=message, details=details)

class QuotaExceededException(SubscriptionException):
    """Exception for quota exceeded"""
    error_code = 'QUOTA_EXCEEDED'
    
    def __init__(self, resource=None, used=None, limit=None, reset_date=None):
        message = f'{resource} quota exceeded' if resource else 'Quota exceeded'
        details = {
            'resource': resource,
            'used': used,
            'limit': limit,
            'reset_date': reset_date.isoformat() if reset_date else None
        }
        super().__init__(message=message, details=details)

class FeatureNotAvailableException(SubscriptionException):
    """Exception for unavailable features"""
    error_code = 'FEATURE_NOT_AVAILABLE'
    
    def __init__(self, feature=None, required_plan=None, current_plan=None):
        message = f'{feature} is not available in your plan' if feature else 'Feature not available'
        details = {
            'feature': feature,
            'required_plan': required_plan,
            'current_plan': current_plan,
            'upgrade_url': '/pricing'
        }
        super().__init__(message=message, details=details)

# Validation Exceptions
class ValidationException(KuwaitSocialAIException):
    """Base exception for validation errors"""
    status_code = 400
    error_code = 'VALIDATION_ERROR'

class KuwaitComplianceException(ValidationException):
    """Exception for Kuwait compliance violations"""
    status_code = 422
    error_code = 'KUWAIT_COMPLIANCE_ERROR'
    
    def __init__(self, violations=None, suggestions=None):
        message = 'Content does not comply with Kuwait guidelines'
        details = {
            'violations': violations or [],
            'suggestions': suggestions or [],
            'guidelines_url': '/guidelines/kuwait'
        }
        super().__init__(message=message, details=details)

class PrayerTimeConflictException(ValidationException):
    """Exception for scheduling during prayer times"""
    error_code = 'PRAYER_TIME_CONFLICT'
    
    def __init__(self, prayer_name=None, prayer_time=None, suggested_time=None):
        message = f'Cannot schedule during {prayer_name} prayer time' if prayer_name else 'Cannot schedule during prayer time'
        details = {
            'prayer_name': prayer_name,
            'prayer_time': prayer_time,
            'suggested_time': suggested_time
        }
        super().__init__(message=message, details=details)

# Rate Limiting Exceptions
class RateLimitException(KuwaitSocialAIException):
    """Exception for rate limit exceeded"""
    status_code = 429
    error_code = 'RATE_LIMIT_EXCEEDED'
    
    def __init__(self, limit=None, window=None, retry_after=None):
        message = 'Rate limit exceeded'
        details = {
            'limit': limit,
            'window': window,
            'retry_after': retry_after
        }
        super().__init__(message=message, details=details)

# External Service Exceptions
class ExternalServiceException(KuwaitSocialAIException):
    """Base exception for external service failures"""
    status_code = 503
    error_code = 'EXTERNAL_SERVICE_ERROR'
    
    def __init__(self, service=None, reason=None):
        message = f'{service} service unavailable' if service else 'External service unavailable'
        details = {
            'service': service,
            'reason': reason
        }
        super().__init__(message=message, details=details)

class PaymentGatewayException(ExternalServiceException):
    """Exception for payment gateway failures"""
    error_code = 'PAYMENT_GATEWAY_ERROR'
    
    def __init__(self, gateway='MyFatoorah', reason=None, transaction_id=None):
        message = f'{gateway} payment failed'
        details = {
            'gateway': gateway,
            'reason': reason,
            'transaction_id': transaction_id
        }
        super().__init__(message=message, details=details)

# Database Exceptions
class DatabaseException(KuwaitSocialAIException):
    """Base exception for database errors"""
    status_code = 503
    error_code = 'DATABASE_ERROR'
    
    def __init__(self, operation=None, reason=None):
        message = 'Database operation failed'
        details = {
            'operation': operation,
            'reason': reason
        }
        super().__init__(message=message, details=details)

class ResourceNotFoundException(KuwaitSocialAIException):
    """Exception for resource not found"""
    status_code = 404
    error_code = 'RESOURCE_NOT_FOUND'
    
    def __init__(self, resource=None, resource_id=None):
        message = f'{resource} not found' if resource else 'Resource not found'
        details = {
            'resource': resource,
            'resource_id': resource_id
        }
        super().__init__(message=message, details=details)

class DuplicateResourceException(KuwaitSocialAIException):
    """Exception for duplicate resource"""
    status_code = 409
    error_code = 'DUPLICATE_RESOURCE'
    
    def __init__(self, resource=None, field=None, value=None):
        message = f'{resource} already exists' if resource else 'Resource already exists'
        details = {
            'resource': resource,
            'field': field,
            'value': value
        }
        super().__init__(message=message, details=details)