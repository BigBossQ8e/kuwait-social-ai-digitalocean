"""
Custom validation utilities for Kuwait Social AI
Additional validation functions and decorators
"""

import re
from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError
from datetime import datetime, time
import pytz
from typing import Dict, List, Any, Callable
import bleach
from bleach.css_sanitizer import CSSSanitizer

# Kuwait timezone
KUWAIT_TZ = pytz.timezone('Asia/Kuwait')

# Prayer times (simplified - would be dynamic in production)
PRAYER_TIMES = {
    'fajr': (time(4, 30), time(5, 30)),
    'dhuhr': (time(11, 45), time(12, 30)),
    'asr': (time(15, 0), time(15, 45)),
    'maghrib': (time(17, 30), time(18, 15)),
    'isha': (time(19, 0), time(19, 45))
}

# Validation decorator
def validate_request(schema_class):
    """Decorator to validate request data using Marshmallow schema"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            schema = schema_class()
            
            # Get data based on request method
            if request.method == 'GET':
                data = request.args.to_dict()
            else:
                data = request.get_json() or {}
            
            # Handle file uploads
            if request.files:
                for key, file in request.files.items():
                    data[key] = file
            
            try:
                # Validate and deserialize
                validated_data = schema.load(data)
                
                # Add validated data to kwargs
                kwargs['validated_data'] = validated_data
                
                return f(*args, **kwargs)
            
            except ValidationError as err:
                return jsonify({
                    'error': 'Validation failed',
                    'errors': err.messages
                }), 400
                
        return decorated_function
    return decorator

# Validation functions
def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str, username: str = None, email: str = None) -> str:
    """
    Validate password strength using basic checks
    For enhanced validation with zxcvbn, use validate_password_enhanced
    """
    # Import enhanced validator
    from .password_strength import validate_password_enhanced
    
    # Use enhanced validation if available
    try:
        return validate_password_enhanced(password, username=username, email=email)
    except ImportError:
        # Fallback to basic validation if zxcvbn not available
        return _validate_password_basic(password)

def _validate_password_basic(password: str) -> str:
    """Basic password validation fallback"""
    if len(password) < 8:
        return 'Password must be at least 8 characters long'
    
    if not re.search(r'[A-Z]', password):
        return 'Password must contain at least one uppercase letter'
    
    if not re.search(r'[a-z]', password):
        return 'Password must contain at least one lowercase letter'
    
    if not re.search(r'[0-9]', password):
        return 'Password must contain at least one number'
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return 'Password must contain at least one special character'
    
    # Check for common weak passwords
    weak_passwords = ['password', '12345678', 'qwerty', 'abc12345', 'password123']
    if password.lower() in weak_passwords:
        return 'This password is too common. Please choose a stronger password'
    
    return None

def validate_kuwait_business_name(name: str) -> bool:
    """Validate business name for Kuwait context"""
    # Allow English, Arabic, numbers, and common business suffixes
    pattern = r'^[\w\s\u0600-\u06FF\.\-&]+$'
    
    if not re.match(pattern, name):
        return False
    
    # Check for minimum length
    if len(name) < 2:
        return False
    
    # Check for offensive terms (simplified)
    offensive_terms = ['spam', 'scam', 'fake']
    if any(term in name.lower() for term in offensive_terms):
        return False
    
    return True

def validate_content_for_kuwait(content: str) -> Dict[str, Any]:
    """Validate content for Kuwait cultural compliance"""
    issues = []
    warnings = []
    
    # Check for potentially sensitive content
    sensitive_terms = {
        'alcohol': 'Content mentions alcohol which may not be appropriate',
        'pork': 'Content mentions pork which is not halal',
        'gambling': 'Content mentions gambling which is prohibited',
        'dating': 'Content about dating should be culturally sensitive'
    }
    
    content_lower = content.lower()
    for term, warning in sensitive_terms.items():
        if term in content_lower:
            warnings.append(warning)
    
    # Check for respectful language
    if re.search(r'\b(damn|hell)\b', content_lower):
        warnings.append('Consider using more respectful language')
    
    # Check for proper Islamic phrases
    islamic_phrases = {
        'inshallah': 'إن شاء الله',
        'mashallah': 'ما شاء الله',
        'alhamdulillah': 'الحمد لله'
    }
    
    suggestions = []
    for english, arabic in islamic_phrases.items():
        if english in content_lower and arabic not in content:
            suggestions.append(f'Consider using the Arabic form: {arabic}')
    
    return {
        'is_valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'suggestions': suggestions
    }

def validate_posting_time(scheduled_time: datetime) -> Dict[str, Any]:
    """Validate posting time considering Kuwait prayer times and business hours"""
    # Convert to Kuwait timezone
    kuwait_time = scheduled_time.astimezone(KUWAIT_TZ)
    
    issues = []
    warnings = []
    suggestions = []
    
    # Check if during prayer time
    current_time = kuwait_time.time()
    for prayer_name, (start, end) in PRAYER_TIMES.items():
        if start <= current_time <= end:
            issues.append(f'Scheduled during {prayer_name} prayer time')
            
            # Suggest alternative time
            if end < time(23, 0):
                suggested_time = kuwait_time.replace(
                    hour=end.hour + 1,
                    minute=0
                )
                suggestions.append(f'Consider scheduling after {prayer_name} at {suggested_time.strftime("%I:%M %p")}')
    
    # Check if Friday prayer time (Jummah)
    if kuwait_time.weekday() == 4 and time(11, 30) <= current_time <= time(13, 0):
        issues.append('Scheduled during Friday prayer (Jummah) time')
    
    # Check if during sleeping hours
    if time(0, 0) <= current_time <= time(6, 0):
        warnings.append('Scheduled during typical sleeping hours (12 AM - 6 AM)')
    
    # Suggest optimal posting times
    optimal_times = [
        time(9, 0),   # Morning
        time(13, 0),  # After Dhuhr
        time(17, 0),  # Before Maghrib
        time(20, 0),  # Evening
    ]
    
    if not any(abs((kuwait_time.hour * 60 + kuwait_time.minute) - (t.hour * 60 + t.minute)) < 30 for t in optimal_times):
        suggestions.append('Consider posting at optimal times: 9 AM, 1 PM, 5 PM, or 8 PM Kuwait time')
    
    return {
        'is_valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'suggestions': suggestions,
        'kuwait_time': kuwait_time.strftime('%Y-%m-%d %I:%M %p %Z')
    }

def validate_image_content(image_path: str) -> Dict[str, Any]:
    """Validate image content for appropriateness (placeholder for actual implementation)"""
    # In production, this would use image recognition API
    # to check for inappropriate content
    return {
        'is_valid': True,
        'warnings': [],
        'suggestions': ['Ensure image is culturally appropriate for Kuwait audience']
    }

def validate_hashtags(hashtags: List[str]) -> Dict[str, Any]:
    """Validate hashtags for Kuwait market"""
    issues = []
    warnings = []
    suggestions = []
    
    # Check hashtag count
    if len(hashtags) > 30:
        issues.append('Too many hashtags (maximum 30 for Instagram)')
    
    # Check for required Kuwait hashtags
    kuwait_hashtags = ['#Kuwait', '#الكويت', '#Q8']
    if not any(tag in hashtags for tag in kuwait_hashtags):
        suggestions.append('Consider adding Kuwait-specific hashtags: #Kuwait #الكويت #Q8')
    
    # Validate each hashtag
    for hashtag in hashtags:
        # Check format
        if not hashtag.startswith('#'):
            issues.append(f'Hashtag must start with #: {hashtag}')
        
        # Check length
        if len(hashtag) > 100:
            warnings.append(f'Hashtag too long: {hashtag}')
        
        # Check for spaces
        if ' ' in hashtag:
            issues.append(f'Hashtag cannot contain spaces: {hashtag}')
    
    # Check for trending Kuwait hashtags (would be dynamic in production)
    trending = ['#KuwaitNationalDay', '#RamadanKuwait', '#KuwaitBusiness']
    relevant_trending = [tag for tag in trending if any(keyword in hashtags[0] for keyword in ['national', 'ramadan', 'business'])]
    if relevant_trending:
        suggestions.append(f'Consider using trending hashtags: {", ".join(relevant_trending)}')
    
    return {
        'is_valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'suggestions': suggestions
    }

def validate_business_hours(datetime_obj: datetime) -> bool:
    """Check if datetime is during Kuwait business hours"""
    kuwait_time = datetime_obj.astimezone(KUWAIT_TZ)
    
    # Kuwait business days: Sunday to Thursday
    if kuwait_time.weekday() >= 5:  # Friday or Saturday
        return False
    
    # Business hours: 8 AM to 5 PM (with break consideration)
    if not (8 <= kuwait_time.hour < 17):
        return False
    
    return True

def sanitize_input(text: str, allow_html: bool = False) -> str:
    """
    Sanitize user input to prevent XSS attacks using bleach library
    
    Args:
        text: Input text to sanitize
        allow_html: If True, allows safe HTML tags; if False, strips all HTML
    
    Returns:
        Sanitized text safe for display
    """
    if not text:
        return ''
    
    if allow_html:
        # Allow only safe HTML tags and attributes
        allowed_tags = [
            'p', 'br', 'span', 'div', 'strong', 'em', 'u', 'i', 'b',
            'a', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
        ]
        
        allowed_attributes = {
            'a': ['href', 'title', 'target'],
            'span': ['class'],
            'div': ['class'],
            'code': ['class']
        }
        
        # CSS sanitizer for style attributes
        css_sanitizer = CSSSanitizer(allowed_css_properties=[
            'color', 'background-color', 'font-size', 'font-weight',
            'text-align', 'margin', 'padding'
        ])
        
        # Clean the HTML
        cleaned = bleach.clean(
            text,
            tags=allowed_tags,
            attributes=allowed_attributes,
            css_sanitizer=css_sanitizer,
            strip=True
        )
        
        # Also sanitize any URLs in href attributes
        cleaned = bleach.linkify(cleaned, callbacks=[
            bleach.callbacks.nofollow,
            bleach.callbacks.target_blank
        ])
        
        return cleaned
    else:
        # Strip all HTML and return plain text
        # This is safer for most user inputs like names, titles, etc.
        cleaned = bleach.clean(text, tags=[], strip=True)
        return cleaned.strip()


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and other attacks
    
    Args:
        filename: Original filename
    
    Returns:
        Safe filename
    """
    if not filename:
        return 'unnamed'
    
    # Remove any path components
    filename = filename.replace('..', '')
    filename = filename.replace('/', '')
    filename = filename.replace('\\', '')
    
    # Keep only alphanumeric, dash, underscore, and dot
    filename = re.sub(r'[^\w\-_\.]', '', filename)
    
    # Limit length
    name_parts = filename.rsplit('.', 1)
    if len(name_parts) == 2:
        name, ext = name_parts
        # Limit name to 100 chars and extension to 10 chars
        filename = f"{name[:100]}.{ext[:10]}"
    else:
        filename = filename[:100]
    
    return filename or 'unnamed'


def validate_and_sanitize_json(data: Dict[str, Any], schema: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Validate and sanitize JSON data
    
    Args:
        data: JSON data to validate and sanitize
        schema: Optional schema to validate against
    
    Returns:
        Sanitized JSON data
    """
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")
    
    sanitized = {}
    
    for key, value in data.items():
        # Sanitize the key
        safe_key = sanitize_input(str(key), allow_html=False)
        
        # Sanitize the value based on type
        if isinstance(value, str):
            sanitized[safe_key] = sanitize_input(value, allow_html=False)
        elif isinstance(value, dict):
            sanitized[safe_key] = validate_and_sanitize_json(value)
        elif isinstance(value, list):
            sanitized[safe_key] = [
                sanitize_input(str(item), allow_html=False) if isinstance(item, str) else item
                for item in value
            ]
        else:
            # For numbers, booleans, None, etc.
            sanitized[safe_key] = value
    
    return sanitized

def validate_file_upload(file) -> Dict[str, Any]:
    """Validate uploaded files using python-magic for proper MIME type detection"""
    from .file_validator import validate_upload
    
    # Determine file type based on extension (for initial categorization)
    filename = file.filename.lower() if file and file.filename else ''
    
    if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')):
        file_type = 'image'
    elif filename.endswith(('.mp4', '.mov', '.avi', '.webm')):
        file_type = 'video'
    elif filename.endswith(('.pdf', '.doc', '.docx', '.txt')):
        file_type = 'document'
    elif filename.endswith(('.mp3', '.wav', '.ogg')):
        file_type = 'audio'
    else:
        file_type = 'image'  # Default to image
    
    # Use the advanced file validator with python-magic
    return validate_upload(file, file_type)

class ContentModerator:
    """Content moderation for Kuwait market"""
    
    def __init__(self):
        self.inappropriate_terms = [
            # Add culturally inappropriate terms
            'alcohol', 'beer', 'wine', 'vodka',
            'pork', 'bacon',
            'gambling', 'casino', 'betting',
            'nude', 'naked'
        ]
        
        self.positive_terms = [
            'halal', 'family', 'traditional', 'quality',
            'authentic', 'fresh', 'healthy', 'blessed'
        ]
    
    def moderate(self, content: str) -> Dict[str, Any]:
        """Moderate content for appropriateness"""
        content_lower = content.lower()
        
        found_inappropriate = [term for term in self.inappropriate_terms if term in content_lower]
        found_positive = [term for term in self.positive_terms if term in content_lower]
        
        score = len(found_positive) - (len(found_inappropriate) * 2)
        
        return {
            'is_appropriate': len(found_inappropriate) == 0,
            'score': score,
            'inappropriate_terms': found_inappropriate,
            'positive_terms': found_positive,
            'recommendation': self._get_recommendation(score, found_inappropriate)
        }
    
    def _get_recommendation(self, score: int, inappropriate_terms: List[str]) -> str:
        """Get content recommendation based on moderation"""
        if inappropriate_terms:
            return f'Remove references to: {", ".join(inappropriate_terms)}'
        elif score >= 3:
            return 'Excellent content for Kuwait market!'
        elif score >= 1:
            return 'Good content. Consider adding more positive terms.'
        else:
            return 'Consider adding culturally relevant positive terms.'

# Validation middleware
def validate_api_key(required_permission=None):
    """Decorator to validate API key for external requests"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            api_key = request.headers.get('X-API-Key')
            
            if not api_key:
                return jsonify({'error': 'API key required'}), 401
            
            # Try database-based validation first
            try:
                from models.api_key import APIKeyService
                
                api_key_obj, error = APIKeyService.validate_key(
                    api_key,
                    required_permission=required_permission,
                    ip_address=request.remote_addr
                )
                
                if error:
                    return jsonify({'error': error}), 401
                
                # Add API key info to request context
                kwargs['api_key'] = api_key_obj
                
            except ImportError:
                # Fallback to environment-based validation
                from models.api_key import validate_environment_api_key
                
                if not validate_environment_api_key(api_key):
                    return jsonify({'error': 'Invalid API key'}), 401
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    # Allow decorator to be used with or without parameters
    if callable(required_permission):
        # Called without parentheses: @validate_api_key
        func = required_permission
        required_permission = None
        return decorator(func)
    else:
        # Called with parentheses: @validate_api_key('permission')
        return decorator

# Rate limiting validator
def validate_rate_limit(max_requests: int = 100, window: int = 3600):
    """Decorator to validate rate limits"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # In production, use Redis for rate limiting
            # This is a simplified example
            client_id = request.headers.get('X-Client-ID', request.remote_addr)
            
            # Check rate limit (simplified)
            # In production, track requests in Redis
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator