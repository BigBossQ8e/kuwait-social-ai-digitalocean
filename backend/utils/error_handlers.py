"""
Error handling utilities for Kuwait Social AI
"""

import logging
from datetime import datetime
from functools import wraps
from flask import jsonify, request
from exceptions import KuwaitSocialAIException

logger = logging.getLogger(__name__)

def handle_errors(f):
    """Decorator to handle errors in route functions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KuwaitSocialAIException as e:
            # Custom exceptions are already properly formatted
            raise e
        except Exception as e:
            # Log unexpected errors
            logger.error(
                f"Unexpected error in {f.__name__}: {str(e)}",
                extra={
                    'function': f.__name__,
                    'method': request.method,
                    'path': request.path,
                    'user_agent': request.headers.get('User-Agent'),
                    'ip': request.remote_addr
                }
            )
            # Return generic error to avoid exposing internals
            return jsonify({
                'error': 'An unexpected error occurred',
                'error_code': 'INTERNAL_ERROR',
                'details': {
                    'message': 'Please try again later or contact support if the issue persists',
                    'request_id': request.headers.get('X-Request-ID', 'unknown')
                }
            }), 500
    
    return decorated_function

def create_error_response(error_code, message, status_code=400, details=None):
    """Create standardized error response"""
    response = {
        'error': message,
        'error_code': error_code,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if details:
        response['details'] = details
    
    return jsonify(response), status_code

def log_error(error, context=None):
    """Log error with context"""
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'request_method': request.method,
        'request_path': request.path,
        'request_args': dict(request.args),
        'user_agent': request.headers.get('User-Agent'),
        'ip_address': request.remote_addr
    }
    
    if context:
        error_info['context'] = context
    
    # Log based on error type
    if isinstance(error, KuwaitSocialAIException):
        if error.status_code >= 500:
            logger.error("Application error", extra=error_info)
        else:
            logger.warning("Client error", extra=error_info)
    else:
        logger.error("Unexpected error", extra=error_info, exc_info=True)

def validate_error_response(response_data):
    """Ensure error response follows standard format"""
    required_fields = ['error', 'error_code']
    
    for field in required_fields:
        if field not in response_data:
            logger.warning(f"Error response missing required field: {field}")
            response_data[field] = 'UNKNOWN_ERROR'
    
    return response_data

class ErrorContext:
    """Context manager for error handling with cleanup"""
    
    def __init__(self, operation_name, cleanup_func=None):
        self.operation_name = operation_name
        self.cleanup_func = cleanup_func
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            log_error(exc_val, {'operation': self.operation_name})
            
            # Run cleanup if provided
            if self.cleanup_func:
                try:
                    self.cleanup_func()
                except Exception as cleanup_error:
                    logger.error(f"Error during cleanup: {str(cleanup_error)}")
        
        # Don't suppress the exception
        return False

# Error message templates for common scenarios
ERROR_MESSAGES = {
    'translation_unavailable': {
        'en': 'Arabic translation is temporarily unavailable. Your content has been saved in English only.',
        'ar': 'الترجمة العربية غير متوفرة مؤقتاً. تم حفظ المحتوى باللغة الإنجليزية فقط.'
    },
    'ai_service_down': {
        'en': 'AI content generation is temporarily unavailable. Please try again in a few minutes.',
        'ar': 'خدمة إنشاء المحتوى بالذكاء الاصطناعي غير متوفرة مؤقتاً. يرجى المحاولة مرة أخرى بعد دقائق.'
    },
    'social_media_error': {
        'en': 'Unable to connect to {platform}. Please check your account connection.',
        'ar': 'تعذر الاتصال بـ {platform}. يرجى التحقق من اتصال حسابك.'
    }
}

def get_user_friendly_message(error_code, language='en', **kwargs):
    """Get user-friendly error message in requested language"""
    if error_code in ERROR_MESSAGES:
        message_template = ERROR_MESSAGES[error_code].get(language, ERROR_MESSAGES[error_code]['en'])
        return message_template.format(**kwargs)
    
    # Default message
    return "An error occurred. Please try again." if language == 'en' else "حدث خطأ. يرجى المحاولة مرة أخرى."