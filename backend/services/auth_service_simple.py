"""
Simple Authentication Service for Testing
Bypasses complex features for demo purposes
"""
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from models import db, User
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
import logging

logger = logging.getLogger(__name__)


class SimpleAuthService:
    """Simplified auth service for testing"""
    
    def __init__(self):
        self.access_token_expires = timedelta(hours=24)  # Longer for testing
        self.refresh_token_expires = timedelta(days=30)
    
    def authenticate_user(self, email: str, password: str, ip_address: str = None) -> Tuple[Optional[User], Optional[str]]:
        """Simple authentication"""
        try:
            # Find user
            user = User.query.filter_by(email=email).first()
            
            if not user:
                # For testing, create a user if it doesn't exist
                if email == "admin@example.com" and password == "password":
                    from werkzeug.security import generate_password_hash
                    user = User(
                        email=email,
                        password_hash=generate_password_hash(password),
                        is_active=True,
                        role='admin'
                    )
                    db.session.add(user)
                    db.session.commit()
                else:
                    return None, "Invalid credentials"
            
            # Check password
            if not user.check_password(password):
                return None, "Invalid credentials"
            
            # Check if active
            if not user.is_active:
                return None, "Account is inactive"
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            return user, None
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None, "Authentication failed"
    
    def generate_tokens(self, user: User) -> Dict[str, str]:
        """Generate simple tokens"""
        # Create payload
        payload = {
            'user_id': user.id,
            'email': user.email,
            'role': user.role,
            'is_admin': user.role == 'admin'
        }
        
        # Generate tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims=payload,
            expires_delta=self.access_token_expires
        )
        
        refresh_token = create_refresh_token(
            identity=user.id,
            additional_claims={'user_id': user.id},
            expires_delta=self.refresh_token_expires
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': int(self.access_token_expires.total_seconds())
        }
    
    def decode_token(self, token: str) -> Optional[Dict]:
        """Decode and validate token"""
        try:
            return decode_token(token)
        except:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Refresh access token"""
        try:
            # Decode refresh token
            payload = decode_token(refresh_token)
            user_id = payload.get('sub') or payload.get('user_id')
            
            # Get user
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return None
            
            # Generate new tokens
            return self.generate_tokens(user)
            
        except:
            return None
    
    def logout(self, user_id: int, token: str = None):
        """Simple logout - just return success"""
        return True
    
    def logout_all_devices(self, user_id: int):
        """Simple logout all - just return success"""
        return True
    
    def get_user_sessions(self, user_id: int) -> list:
        """Return empty sessions for now"""
        return []


# Create singleton instance
simple_auth_service = SimpleAuthService()