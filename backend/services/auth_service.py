"""
Enhanced Authentication Service with JWT Refresh Tokens
Handles authentication, authorization, and token management
"""
import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple, Any
import jwt
import secrets
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import or_

from models import db, User, Admin, Owner, Client, AdminActivity
from extensions import redis_client as _redis_client

# Get redis client, handling case where it might not be initialized yet
def get_redis_client():
    """Get Redis client, handling None case"""
    return _redis_client

logger = logging.getLogger(__name__)


class AuthService:
    """Enhanced authentication service with JWT refresh tokens"""
    
    def __init__(self):
        self.access_token_expires = timedelta(minutes=15)  # Short-lived access tokens
        self.refresh_token_expires = timedelta(days=7)    # Long-lived refresh tokens
        self.refresh_token_reuse_window = timedelta(minutes=2)  # Grace period for token rotation
    
    def authenticate_user(self, email: str, password: str, ip_address: str = None) -> Tuple[Optional[User], Optional[str]]:
        """Authenticate user and return user object and error message if any"""
        # Find user by email
        user = User.query.filter_by(email=email.lower()).first()
        
        if not user:
            self._log_failed_login(email, ip_address, "User not found")
            return None, "Invalid email or password"
        
        # Check if user is active
        if not user.is_active:
            self._log_failed_login(email, ip_address, "Account inactive")
            return None, "Account is inactive. Please contact support."
        
        # Check password
        if not check_password_hash(user.password_hash, password):
            self._log_failed_login(email, ip_address, "Invalid password")
            self._increment_failed_attempts(user)
            return None, "Invalid email or password"
        
        # Check if account is locked
        if self._is_account_locked(user):
            return None, "Account is locked due to too many failed attempts. Please try again later."
        
        # Success - reset failed attempts
        if hasattr(user, 'failed_login_attempts'):
            user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        self._log_successful_login(user, ip_address)
        
        return user, None
    
    def generate_tokens(self, user: User) -> Dict[str, str]:
        """Generate both access and refresh tokens"""
        # Create token ID for tracking
        token_id = secrets.token_urlsafe(16)
        
        # Common payload
        base_payload = {
            'user_id': user.id,
            'email': user.email,
            'role': user.role,
            'token_id': token_id
        }
        
        # Access token payload
        access_payload = {
            **base_payload,
            'type': 'access',
            'exp': datetime.now(timezone.utc) + self.access_token_expires,
            'iat': datetime.now(timezone.utc)
        }
        
        # Refresh token payload
        refresh_payload = {
            **base_payload,
            'type': 'refresh',
            'exp': datetime.now(timezone.utc) + self.refresh_token_expires,
            'iat': datetime.now(timezone.utc)
        }
        
        # Add role-specific data
        if user.role == 'admin' and user.admin_profile:
            access_payload['admin_id'] = user.admin_profile.id
            access_payload['admin_role'] = user.admin_profile.role
            access_payload['permissions'] = self._get_admin_permissions(user.admin_profile)
        elif user.role == 'client' and user.client_profile:
            access_payload['client_id'] = user.client_profile.id
            access_payload['company'] = user.client_profile.company_name
        
        # Generate tokens using Flask-JWT-Extended
        from flask_jwt_extended import create_access_token, create_refresh_token
        
        # Create access token with additional claims
        access_token = create_access_token(
            identity=user.id,
            additional_claims=access_payload,
            expires_delta=self.access_token_expires
        )
        
        # Create refresh token
        refresh_token = create_refresh_token(
            identity=user.id,
            additional_claims=refresh_payload,
            expires_delta=self.refresh_token_expires
        )
        
        # Store refresh token in Redis
        self._store_refresh_token(user.id, token_id, refresh_token)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': int(self.access_token_expires.total_seconds())
        }
    
    def refresh_access_token(self, refresh_token: str, ip_address: str = None) -> Tuple[Optional[Dict[str, str]], Optional[str]]:
        """Refresh access token using refresh token"""
        try:
            # Decode refresh token
            payload = jwt.decode(
                refresh_token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Verify token type
            if payload.get('type') != 'refresh':
                return None, "Invalid token type"
            
            # Check if token is revoked
            if self._is_token_revoked(payload['user_id'], payload['token_id']):
                return None, "Token has been revoked"
            
            # Get user
            user = User.query.get(payload['user_id'])
            if not user or not user.is_active:
                return None, "User not found or inactive"
            
            # Check if refresh token is still valid in Redis
            stored_token = self._get_refresh_token(user.id, payload['token_id'])
            if not stored_token:
                return None, "Refresh token not found"
            
            # Implement refresh token rotation
            # Generate new tokens
            new_tokens = self.generate_tokens(user)
            
            # Revoke old refresh token (with grace period)
            self._revoke_refresh_token_with_grace(user.id, payload['token_id'])
            
            # Log token refresh
            self._log_token_refresh(user, ip_address)
            
            return new_tokens, None
            
        except jwt.ExpiredSignatureError:
            return None, "Refresh token has expired"
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid refresh token: {e}")
            return None, "Invalid refresh token"
    
    def verify_token(self, token: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Verify and decode access token"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Verify token type
            if payload.get('type') != 'access':
                return None, "Invalid token type"
            
            # Check if user still exists and is active
            user = User.query.get(payload['user_id'])
            if not user or not user.is_active:
                return None, "User not found or inactive"
            
            # Check if token is revoked
            if self._is_token_revoked(payload['user_id'], payload['token_id']):
                return None, "Token has been revoked"
            
            return payload, None
            
        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"
    
    def revoke_token(self, user_id: int, token_id: str = None):
        """Revoke a specific token or all tokens for a user"""
        if token_id:
            # Revoke specific token
            self._revoke_refresh_token(user_id, token_id)
        else:
            # Revoke all tokens for user
            self._revoke_all_user_tokens(user_id)
    
    def logout(self, user_id: int, token_id: str):
        """Logout user by revoking their tokens"""
        self.revoke_token(user_id, token_id)
        
        # Log logout
        user = User.query.get(user_id)
        if user:
            self._log_logout(user)
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """Change user password"""
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        # Verify old password
        if not check_password_hash(user.password_hash, old_password):
            return False, "Current password is incorrect"
        
        # Validate new password
        if len(new_password) < 8:
            return False, "Password must be at least 8 characters long"
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        user.password_changed_at = datetime.utcnow()
        db.session.commit()
        
        # Revoke all existing tokens (force re-login)
        self._revoke_all_user_tokens(user_id)
        
        return True, None
    
    def create_impersonation_token(self, admin_id: int, target_user_id: int, duration_minutes: int = 60) -> Tuple[Optional[str], Optional[str]]:
        """Create a temporary impersonation token for admins"""
        admin = Admin.query.get(admin_id)
        if not admin or admin.role not in ['owner', 'admin']:
            return None, "Insufficient permissions"
        
        target_user = User.query.get(target_user_id)
        if not target_user:
            return None, "Target user not found"
        
        # Create impersonation token
        payload = {
            'user_id': target_user_id,
            'email': target_user.email,
            'role': target_user.role,
            'type': 'access',
            'impersonation': True,
            'impersonated_by': admin_id,
            'exp': datetime.now(timezone.utc) + timedelta(minutes=duration_minutes),
            'iat': datetime.now(timezone.utc)
        }
        
        # Add role-specific data
        if target_user.role == 'client' and target_user.client_profile:
            payload['client_id'] = target_user.client_profile.id
            payload['company'] = target_user.client_profile.company_name
        
        token = jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        # Log impersonation
        self._log_impersonation(admin, target_user)
        
        return token, None
    
    # Private helper methods
    
    def _get_admin_permissions(self, admin: Admin) -> list:
        """Get permissions based on admin role"""
        if admin.role == 'owner':
            return ['all']  # Full access
        elif admin.role == 'admin':
            return ['clients', 'content', 'analytics', 'settings']
        elif admin.role == 'support':
            return ['clients:read', 'content:read', 'support']
        return []
    
    def _store_refresh_token(self, user_id: int, token_id: str, token: str):
        """Store refresh token in Redis"""
        redis_client = get_redis_client()
        if not redis_client:
            return
        
        key = f"refresh_token:{user_id}:{token_id}"
        redis_client.setex(
            key,
            int(self.refresh_token_expires.total_seconds()),
            token
        )
        
        # Also store in a set for easy revocation of all tokens
        redis_client.sadd(f"user_tokens:{user_id}", token_id)
    
    def _get_refresh_token(self, user_id: int, token_id: str) -> Optional[str]:
        """Get refresh token from Redis"""
        redis_client = get_redis_client()
        if not redis_client:
            return None
        
        key = f"refresh_token:{user_id}:{token_id}"
        return redis_client.get(key)
    
    def _revoke_refresh_token(self, user_id: int, token_id: str):
        """Revoke a refresh token immediately"""
        redis_client = get_redis_client()
        if not redis_client:
            return
        
        key = f"refresh_token:{user_id}:{token_id}"
        redis_client.delete(key)
        redis_client.srem(f"user_tokens:{user_id}", token_id)
        
        # Add to revoked tokens list
        redis_client.setex(
            f"revoked_token:{user_id}:{token_id}",
            int(self.refresh_token_expires.total_seconds()),
            "1"
        )
    
    def _revoke_refresh_token_with_grace(self, user_id: int, token_id: str):
        """Revoke refresh token with grace period for rotation"""
        redis_client = get_redis_client()
        if not redis_client:
            return
        
        # Mark token as rotating (grace period)
        redis_client.setex(
            f"rotating_token:{user_id}:{token_id}",
            int(self.refresh_token_reuse_window.total_seconds()),
            "1"
        )
        
        # Schedule revocation after grace period
        # In production, use a task queue like Celery
        # For now, token will be invalid after grace period
    
    def _revoke_all_user_tokens(self, user_id: int):
        """Revoke all tokens for a user"""
        redis_client = get_redis_client()
        if not redis_client:
            return
        
        # Get all token IDs for user
        token_ids = redis_client.smembers(f"user_tokens:{user_id}")
        
        # Revoke each token
        for token_id in token_ids:
            self._revoke_refresh_token(user_id, token_id.decode())
    
    def _is_token_revoked(self, user_id: int, token_id: str) -> bool:
        """Check if token is revoked"""
        redis_client = get_redis_client()
        if not redis_client:
            return False
        
        return redis_client.exists(f"revoked_token:{user_id}:{token_id}")
    
    def _is_account_locked(self, user: User) -> bool:
        """Check if account is locked due to failed attempts"""
        # Skip if user doesn't have these attributes
        if not hasattr(user, 'failed_login_attempts') or not hasattr(user, 'last_failed_login'):
            return False
            
        if getattr(user, 'failed_login_attempts', 0) >= 5:
            # Lock for 30 minutes after 5 failed attempts
            last_failed = getattr(user, 'last_failed_login', None)
            if last_failed:
                lock_until = last_failed + timedelta(minutes=30)
                return datetime.utcnow() < lock_until
        return False
    
    def _increment_failed_attempts(self, user: User):
        """Increment failed login attempts"""
        # Skip if user doesn't have these attributes
        if hasattr(user, 'failed_login_attempts'):
            user.failed_login_attempts = (getattr(user, 'failed_login_attempts', 0) or 0) + 1
        if hasattr(user, 'last_failed_login'):
            user.last_failed_login = datetime.utcnow()
        try:
            db.session.commit()
        except:
            pass  # Ignore if attributes don't exist
    
    # Logging methods
    
    def _log_successful_login(self, user: User, ip_address: str = None):
        """Log successful login"""
        if user.role == 'admin' and user.admin_profile:
            activity = AdminActivity(
                admin_id=user.admin_profile.id,
                action='login',
                resource_type='auth',
                ip_address=ip_address
            )
            db.session.add(activity)
            db.session.commit()
    
    def _log_failed_login(self, email: str, ip_address: str = None, reason: str = None):
        """Log failed login attempt"""
        logger.warning(f"Failed login attempt for {email} from {ip_address}: {reason}")
    
    def _log_logout(self, user: User):
        """Log user logout"""
        if user.role == 'admin' and user.admin_profile:
            activity = AdminActivity(
                admin_id=user.admin_profile.id,
                action='logout',
                resource_type='auth'
            )
            db.session.add(activity)
            db.session.commit()
    
    def _log_token_refresh(self, user: User, ip_address: str = None):
        """Log token refresh"""
        logger.info(f"Token refreshed for user {user.email} from {ip_address}")
    
    def _log_impersonation(self, admin: Admin, target_user: User):
        """Log admin impersonation"""
        activity = AdminActivity(
            admin_id=admin.id,
            action='impersonate',
            resource_type='user',
            resource_id=target_user.id,
            changes={
                'target_email': target_user.email,
                'target_role': target_user.role
            }
        )
        db.session.add(activity)
        db.session.commit()


# Singleton instance
auth_service = AuthService()