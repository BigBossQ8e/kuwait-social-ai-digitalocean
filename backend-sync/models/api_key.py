"""
API Key management models for secure external API access
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
import hashlib
import secrets
import os
from . import db


class APIKey(db.Model):
    """Model for managing external API keys"""
    
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # Human-readable name for the key
    key_hash = Column(String(64), nullable=False, unique=True)  # SHA-256 hash of the key
    prefix = Column(String(10), nullable=False)  # First 8 chars for identification
    
    # Permissions and settings
    is_active = Column(Boolean, default=True, nullable=False)
    permissions = Column(Text)  # JSON string of permissions
    rate_limit = Column(Integer, default=1000)  # Requests per hour
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime)
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Optional client association
    client_id = Column(Integer, db.ForeignKey('clients.id'), nullable=True)
    
    # Security
    ip_whitelist = Column(Text)  # JSON array of allowed IPs
    expires_at = Column(DateTime)  # Optional expiration
    
    # Relationships
    client = db.relationship('Client', back_populates='api_keys')
    usage_logs = db.relationship('APIKeyUsage', back_populates='api_key', lazy='dynamic')
    
    def __init__(self, name, permissions=None, rate_limit=1000, client_id=None, 
                 ip_whitelist=None, expires_in_days=None):
        self.name = name
        self.permissions = permissions
        self.rate_limit = rate_limit
        self.client_id = client_id
        self.ip_whitelist = ip_whitelist
        
        if expires_in_days:
            self.expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Generate the API key
        self._generate_key()
    
    def _generate_key(self):
        """Generate a new API key"""
        # Generate a secure random key
        raw_key = f"ksa_{secrets.token_urlsafe(32)}"
        
        # Store prefix for identification
        self.prefix = raw_key[:8]
        
        # Hash the key for storage
        self.key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        # Return the raw key (only time it's available in plain text)
        self._raw_key = raw_key
        return raw_key
    
    def verify_key(self, provided_key):
        """Verify a provided key against this API key"""
        if not self.is_active:
            return False
        
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        
        # Hash the provided key and compare
        provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
        return provided_hash == self.key_hash
    
    def record_usage(self, ip_address=None):
        """Record usage of this API key"""
        self.last_used_at = datetime.utcnow()
        self.usage_count += 1
        db.session.commit()
    
    def is_rate_limited(self):
        """Check if this key has exceeded its rate limit"""
        if not self.rate_limit:
            return False
        
        # Check usage in the last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_usage = APIKeyUsage.query.filter(
            APIKeyUsage.api_key_id == self.id,
            APIKeyUsage.used_at >= one_hour_ago
        ).count()
        
        return recent_usage >= self.rate_limit
    
    def has_permission(self, permission):
        """Check if this key has a specific permission"""
        if not self.permissions:
            return False
        
        import json
        try:
            perms = json.loads(self.permissions)
            return permission in perms or 'all' in perms
        except (json.JSONDecodeError, TypeError):
            return False
    
    def to_dict(self, include_key=False):
        """Convert to dictionary (excluding sensitive data by default)"""
        data = {
            'id': self.id,
            'name': self.name,
            'prefix': self.prefix,
            'is_active': self.is_active,
            'rate_limit': self.rate_limit,
            'created_at': self.created_at.isoformat(),
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'usage_count': self.usage_count,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
        
        if include_key and hasattr(self, '_raw_key'):
            data['key'] = self._raw_key
        
        return data


class APIKeyUsage(db.Model):
    """Track API key usage for rate limiting and analytics"""
    
    __tablename__ = 'api_key_usage'
    
    id = Column(Integer, primary_key=True)
    api_key_id = Column(Integer, db.ForeignKey('api_keys.id'), nullable=False)
    
    # Request details
    endpoint = Column(String(200))
    method = Column(String(10))
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(Text)
    
    # Response details
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    
    # Timestamp
    used_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    api_key = db.relationship('APIKey', back_populates='usage_logs')


class APIKeyService:
    """Service for managing API keys"""
    
    @staticmethod
    def create_key(name, permissions=None, rate_limit=1000, client_id=None, 
                   ip_whitelist=None, expires_in_days=None):
        """Create a new API key"""
        api_key = APIKey(
            name=name,
            permissions=permissions,
            rate_limit=rate_limit,
            client_id=client_id,
            ip_whitelist=ip_whitelist,
            expires_in_days=expires_in_days
        )
        
        db.session.add(api_key)
        db.session.commit()
        
        return api_key
    
    @staticmethod
    def validate_key(provided_key, required_permission=None, ip_address=None):
        """Validate an API key and check permissions"""
        if not provided_key:
            return None, "API key required"
        
        # Find the key by prefix for faster lookup
        prefix = provided_key[:8] if len(provided_key) >= 8 else provided_key
        
        api_key = APIKey.query.filter_by(prefix=prefix, is_active=True).first()
        
        if not api_key:
            return None, "Invalid API key"
        
        if not api_key.verify_key(provided_key):
            return None, "Invalid API key"
        
        if api_key.expires_at and datetime.utcnow() > api_key.expires_at:
            return None, "API key expired"
        
        if api_key.is_rate_limited():
            return None, "Rate limit exceeded"
        
        if required_permission and not api_key.has_permission(required_permission):
            return None, f"Permission '{required_permission}' required"
        
        # Check IP whitelist
        if api_key.ip_whitelist and ip_address:
            import json
            try:
                allowed_ips = json.loads(api_key.ip_whitelist)
                if ip_address not in allowed_ips:
                    return None, "IP address not whitelisted"
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Record usage
        api_key.record_usage(ip_address)
        
        # Log detailed usage
        APIKeyService.log_usage(
            api_key.id,
            endpoint=request.endpoint if 'request' in globals() else None,
            method=request.method if 'request' in globals() else None,
            ip_address=ip_address
        )
        
        return api_key, None
    
    @staticmethod
    def log_usage(api_key_id, endpoint=None, method=None, ip_address=None,
                  status_code=None, response_time_ms=None, user_agent=None):
        """Log detailed API key usage"""
        usage = APIKeyUsage(
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            ip_address=ip_address,
            status_code=status_code,
            response_time_ms=response_time_ms,
            user_agent=user_agent
        )
        
        db.session.add(usage)
        db.session.commit()
    
    @staticmethod
    def revoke_key(api_key_id):
        """Revoke an API key"""
        api_key = APIKey.query.get(api_key_id)
        if api_key:
            api_key.is_active = False
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_usage_stats(api_key_id, days=30):
        """Get usage statistics for an API key"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        usage_stats = db.session.query(
            func.date(APIKeyUsage.used_at).label('date'),
            func.count(APIKeyUsage.id).label('requests'),
            func.avg(APIKeyUsage.response_time_ms).label('avg_response_time')
        ).filter(
            APIKeyUsage.api_key_id == api_key_id,
            APIKeyUsage.used_at >= start_date
        ).group_by(
            func.date(APIKeyUsage.used_at)
        ).all()
        
        return [
            {
                'date': stat.date.isoformat(),
                'requests': stat.requests,
                'avg_response_time': float(stat.avg_response_time or 0)
            }
            for stat in usage_stats
        ]


# Environment-based API key validation (fallback)
def validate_environment_api_key(provided_key):
    """Validate API key against environment variables (for simple setups)"""
    valid_keys = []
    
    # Load from environment
    env_keys = [
        os.getenv('EXTERNAL_API_KEY'),
        os.getenv('WEBHOOK_API_KEY'),
        os.getenv('ADMIN_API_KEY')
    ]
    
    valid_keys.extend([key for key in env_keys if key])
    
    # Hash the provided key
    provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
    
    # Check against hashed versions too
    for key in valid_keys:
        if key == provided_key:
            return True
        if hashlib.sha256(key.encode()).hexdigest() == provided_hash:
            return True
    
    return False