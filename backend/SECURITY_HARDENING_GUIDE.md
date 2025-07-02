# 🔒 Kuwait Social AI - Security Hardening Guide

## Critical Security Vulnerabilities to Fix

### 1. Nginx Security Headers (CRITICAL)

**Current nginx.conf is missing essential security headers!**

```nginx
# /nginx/nginx.conf - Add these immediately

server {
    listen 80;
    server_name app.kuwaitsa.com;
    
    # Security Headers - MUST ADD
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
    
    # HSTS (if using HTTPS)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Content Security Policy - Customize for your needs
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://apis.google.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https://api.openai.com https://api.anthropic.com; frame-ancestors 'none';" always;
    
    # Hide Nginx version
    server_tokens off;
    
    # Prevent clickjacking
    add_header X-Frame-Options "DENY" always;
    
    # Enable CORS properly
    add_header Access-Control-Allow-Origin "$http_origin" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
    add_header Access-Control-Allow-Credentials "true" always;
}
```

### 2. Rate Limiting Per Client (CRITICAL)

```python
# backend/utils/rate_limiting.py

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from functools import wraps
import redis

# Initialize Redis for distributed rate limiting
redis_client = redis.from_url(os.getenv('REDIS_URL'))

def get_client_identifier():
    """Get unique identifier for rate limiting"""
    try:
        verify_jwt_in_request()
        client_id = get_jwt_identity()
        claims = get_jwt()
        
        # Different limits for different roles
        role = claims.get('role', 'client')
        return f"{role}:{client_id}"
    except:
        # For non-authenticated requests
        return get_remote_address()

# Configure limiter with Redis storage
limiter = Limiter(
    key_func=get_client_identifier,
    storage_uri=os.getenv('REDIS_URL'),
    default_limits=["200 per day", "50 per hour"]
)

# Custom decorators for different tiers
def premium_limit(f):
    """Higher limits for premium clients"""
    @wraps(f)
    @limiter.limit("1000 per day, 200 per hour")
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

def ai_endpoint_limit(f):
    """Specific limits for expensive AI operations"""
    @wraps(f)
    @limiter.limit("100 per day, 20 per hour")
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

# Track usage for billing
def track_api_usage(endpoint, tokens_used=0):
    """Track API usage for billing purposes"""
    client_id = get_jwt_identity()
    timestamp = datetime.utcnow()
    
    # Store in Redis with expiry
    key = f"usage:{client_id}:{timestamp.strftime('%Y-%m-%d')}"
    redis_client.hincrby(key, endpoint, 1)
    if tokens_used:
        redis_client.hincrby(key, f"{endpoint}:tokens", tokens_used)
    
    # Expire after 90 days
    redis_client.expire(key, 90 * 24 * 60 * 60)
```

### 3. Input Validation & Sanitization (HIGH)

```python
# backend/utils/validators.py

from marshmallow import Schema, fields, validate, ValidationError
from bleach import clean
import re

class ContentGenerationSchema(Schema):
    """Validate AI content generation requests"""
    prompt = fields.Str(
        required=True,
        validate=[
            validate.Length(min=10, max=1000),
            lambda x: not bool(re.search(r'<script|javascript:|on\w+=', x, re.I))
        ],
        error_messages={
            "required": "Prompt is required",
            "invalid": "Invalid characters in prompt"
        }
    )
    platform = fields.Str(
        required=True,
        validate=validate.OneOf(['instagram', 'tiktok', 'twitter', 'facebook'])
    )
    tone = fields.Str(
        validate=validate.OneOf(['professional', 'casual', 'enthusiastic', 'formal'])
    )
    business_type = fields.Str(
        validate=validate.OneOf(['restaurant', 'cafe', 'bakery', 'catering'])
    )
    include_arabic = fields.Bool()
    include_hashtags = fields.Bool()

def sanitize_user_content(content: str) -> str:
    """Sanitize user-generated content"""
    # Allow only safe HTML tags
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'br']
    allowed_attributes = {}
    
    # Clean HTML
    cleaned = clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    
    # Additional sanitization for Kuwait context
    # Remove any potential blasphemous content
    sensitive_patterns = [
        r'(?i)prophet\s*muhammad',  # Should be PBUH
        r'(?i)allah',  # Should be used respectfully
    ]
    
    for pattern in sensitive_patterns:
        if re.search(pattern, cleaned):
            # Flag for review instead of auto-removing
            raise ValidationError("Content requires cultural review")
    
    return cleaned

# SQL Injection Prevention
def validate_search_query(query: str) -> str:
    """Validate search queries to prevent SQL injection"""
    # Remove SQL keywords and special characters
    dangerous_patterns = [
        r"('|\")",  # Quotes
        r"(--|#|\/\*|\*\/)",  # SQL comments
        r"(union|select|insert|update|delete|drop|create)",  # SQL keywords
        r"(script|javascript|vbscript)",  # Script tags
        r"(<|>|&|%)",  # Special chars
    ]
    
    clean_query = query
    for pattern in dangerous_patterns:
        clean_query = re.sub(pattern, '', clean_query, flags=re.IGNORECASE)
    
    # Limit length
    return clean_query[:100]
```

### 4. JWT Security Enhancements (HIGH)

```python
# backend/utils/jwt_security.py

from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
import secrets

class SecureJWTManager:
    """Enhanced JWT security with refresh tokens and blacklisting"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.access_expires = timedelta(minutes=15)  # Short-lived
        self.refresh_expires = timedelta(days=30)
        
    def create_tokens(self, identity, role, additional_claims=None):
        """Create both access and refresh tokens"""
        claims = {
            'role': role,
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(16)  # Unique token ID
        }
        
        if additional_claims:
            claims.update(additional_claims)
        
        access_token = create_access_token(
            identity=identity,
            fresh=True,
            expires_delta=self.access_expires,
            additional_claims=claims
        )
        
        refresh_token = create_refresh_token(
            identity=identity,
            expires_delta=self.refresh_expires,
            additional_claims={'role': role}
        )
        
        # Store refresh token in Redis
        self.redis.setex(
            f"refresh:{identity}:{claims['jti']}",
            int(self.refresh_expires.total_seconds()),
            refresh_token
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': int(self.access_expires.total_seconds())
        }
    
    def revoke_token(self, jti):
        """Blacklist a token"""
        self.redis.setex(f"blacklist:{jti}", 86400 * 30, "true")
    
    def is_token_revoked(self, jwt_header, jwt_payload):
        """Check if token is blacklisted"""
        jti = jwt_payload.get('jti')
        return self.redis.get(f"blacklist:{jti}") is not None
```

### 5. API Security Middleware (HIGH)

```python
# backend/middleware/security.py

from flask import request, abort, g
from functools import wraps
import hmac
import hashlib
import time

class SecurityMiddleware:
    """Comprehensive security middleware"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Security checks before processing request"""
        # 1. Check request size
        if request.content_length and request.content_length > 10 * 1024 * 1024:  # 10MB
            abort(413, "Request too large")
        
        # 2. Validate content type for POST/PUT
        if request.method in ['POST', 'PUT']:
            if not request.is_json:
                abort(400, "Content-Type must be application/json")
        
        # 3. Check for suspicious patterns
        self._check_suspicious_patterns()
        
        # 4. Add request ID for tracking
        g.request_id = secrets.token_urlsafe(16)
        
    def after_request(self, response):
        """Add security headers to response"""
        response.headers['X-Request-ID'] = g.get('request_id', 'unknown')
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    
    def _check_suspicious_patterns(self):
        """Check for common attack patterns"""
        # Check URL
        suspicious_patterns = [
            '../',  # Path traversal
            '<script',  # XSS
            'SELECT.*FROM',  # SQL injection
            'eval(',  # Code injection
            'cmd=',  # Command injection
        ]
        
        url = request.url.lower()
        for pattern in suspicious_patterns:
            if pattern.lower() in url:
                abort(400, "Suspicious request pattern detected")

def require_api_signature(f):
    """Require HMAC signature for sensitive operations"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get signature from header
        signature = request.headers.get('X-API-Signature')
        if not signature:
            abort(401, "Missing API signature")
        
        # Recreate signature
        timestamp = request.headers.get('X-Timestamp')
        if not timestamp or abs(time.time() - float(timestamp)) > 300:  # 5 min window
            abort(401, "Invalid or expired timestamp")
        
        # Create expected signature
        message = f"{request.method}:{request.path}:{timestamp}:{request.get_data(as_text=True)}"
        expected = hmac.new(
            current_app.config['API_SECRET'].encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected):
            abort(401, "Invalid API signature")
        
        return f(*args, **kwargs)
    return decorated_function
```

### 6. Database Security (MEDIUM)

```python
# backend/utils/db_security.py

from sqlalchemy import event
from sqlalchemy.pool import Pool
import logging

@event.listens_for(Pool, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set security pragmas for SQLite"""
    if 'sqlite' in db.engine.url.drivername:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

# Audit logging for sensitive operations
class AuditLog(db.Model):
    """Track all sensitive operations"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100), nullable=False)
    resource = db.Column(db.String(100))
    resource_id = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    details = db.Column(db.JSON)

def log_security_event(action, resource=None, resource_id=None, details=None):
    """Log security-relevant events"""
    try:
        log = AuditLog(
            user_id=get_jwt_identity() if verify_jwt_in_request() else None,
            action=action,
            resource=resource,
            resource_id=resource_id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string[:200],
            details=details
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        logging.error(f"Failed to log security event: {e}")
```

### 7. Environment Security (.env)

```bash
# .env.example - NEVER commit actual .env file

# Security Keys - Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=CHANGE_THIS_TO_RANDOM_STRING_MIN_32_CHARS
JWT_SECRET_KEY=DIFFERENT_RANDOM_STRING_MIN_32_CHARS
API_SIGNATURE_SECRET=ANOTHER_RANDOM_STRING_FOR_HMAC

# Database - Use strong passwords
DATABASE_URL=postgresql://user:STRONG_PASSWORD@localhost/kuwait_social_ai
REDIS_URL=redis://:REDIS_PASSWORD@localhost:6379

# API Keys - Restrict by IP in provider dashboard
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Security Settings
FLASK_ENV=production
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=None

# Rate Limiting
RATELIMIT_STORAGE_URL=redis://:REDIS_PASSWORD@localhost:6379
RATELIMIT_HEADERS_ENABLED=True
```

---

## 🚨 Immediate Action Items

### Day 1: Critical Fixes
1. [ ] Add all security headers to nginx.conf
2. [ ] Implement per-client rate limiting
3. [ ] Update JWT to use refresh tokens
4. [ ] Add request validation schemas

### Week 1: High Priority
1. [ ] Implement API signature for sensitive endpoints
2. [ ] Add audit logging for all admin actions
3. [ ] Set up security monitoring alerts
4. [ ] Create security test suite

### Week 2: Medium Priority
1. [ ] Implement CSRF protection
2. [ ] Add request/response encryption for sensitive data
3. [ ] Set up automated security scanning
4. [ ] Create incident response plan

---

## 🛡️ Security Checklist

- [ ] All user input is validated and sanitized
- [ ] SQL queries use parameterized statements
- [ ] Passwords are hashed with bcrypt (cost factor 12+)
- [ ] API keys are stored encrypted in database
- [ ] HTTPS is enforced in production
- [ ] Security headers are present on all responses
- [ ] Rate limiting is implemented per client
- [ ] Logs don't contain sensitive information
- [ ] Regular security audits are scheduled
- [ ] Incident response plan is documented

This security hardening will protect Kuwait Social AI from common attacks and ensure client data safety! 🔒