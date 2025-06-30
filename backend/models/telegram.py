"""
Telegram Account Model for Kuwait Social AI
"""

from datetime import datetime
from . import db


class TelegramAccount(db.Model):
    """Telegram account linked to users for notifications and bot interactions"""
    __tablename__ = 'telegram_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Telegram specific fields
    telegram_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    telegram_username = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    
    # Bot interaction fields
    is_bot_active = db.Column(db.Boolean, default=True)
    language_preference = db.Column(db.String(10), default='en')  # en, ar
    
    # Notification preferences
    notify_posts = db.Column(db.Boolean, default=True)
    notify_analytics = db.Column(db.Boolean, default=True)
    notify_alerts = db.Column(db.Boolean, default=True)
    
    # Verification and security
    verification_code = db.Column(db.String(20))
    verification_expires = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_interaction = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', back_populates='telegram_accounts')
    
    def __repr__(self):
        return f'<TelegramAccount {self.telegram_username or self.telegram_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'telegram_id': self.telegram_id,
            'telegram_username': self.telegram_username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_bot_active': self.is_bot_active,
            'language_preference': self.language_preference,
            'notify_posts': self.notify_posts,
            'notify_analytics': self.notify_analytics,
            'notify_alerts': self.notify_alerts,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None
        }
    
    def verify(self):
        """Mark the telegram account as verified"""
        self.is_verified = True
        self.verification_code = None
        self.verification_expires = None
        db.session.commit()