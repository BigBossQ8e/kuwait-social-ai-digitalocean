"""
Telegram Models for Kuwait Social AI
"""

from datetime import datetime
from . import db


class TelegramAccount(db.Model):
    """Telegram account linked to users for notifications and bot interactions"""
    __tablename__ = 'telegram_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)
    
    # Telegram specific fields
    telegram_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    telegram_username = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    chat_id = db.Column(db.String(100), unique=True, nullable=False)
    
    # Bot configuration - each client has their own bot
    bot_token = db.Column(db.String(200))  # Encrypted in production
    bot_username = db.Column(db.String(100))  # e.g., @ClientRestaurantBot
    bot_name = db.Column(db.String(100))  # e.g., "Restaurant Kuwait Bot"
    webhook_url = db.Column(db.String(500))  # Optional webhook URL
    
    # Bot interaction fields
    is_bot_active = db.Column(db.Boolean, default=True)
    language_preference = db.Column(db.String(10), default='en')  # en, ar
    
    # Notification preferences
    notify_posts = db.Column(db.Boolean, default=True)
    notify_analytics = db.Column(db.Boolean, default=True)
    notify_alerts = db.Column(db.Boolean, default=True)
    notify_approvals = db.Column(db.Boolean, default=True)
    
    # Verification and security
    verification_code = db.Column(db.String(20))
    verification_expires = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_interaction = db.Column(db.DateTime)
    linked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='telegram_accounts')
    client = db.relationship('Client', back_populates='telegram_account', uselist=False)
    approvals = db.relationship('PostApproval', back_populates='telegram_account')
    
    def __repr__(self):
        return f'<TelegramAccount {self.telegram_username or self.telegram_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'client_id': self.client_id,
            'telegram_id': self.telegram_id,
            'telegram_username': self.telegram_username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'chat_id': self.chat_id,
            'bot_username': self.bot_username,
            'bot_name': self.bot_name,
            'has_bot_token': bool(self.bot_token),  # Don't expose the actual token
            'webhook_url': self.webhook_url,
            'is_bot_active': self.is_bot_active,
            'language_preference': self.language_preference,
            'notify_posts': self.notify_posts,
            'notify_analytics': self.notify_analytics,
            'notify_alerts': self.notify_alerts,
            'notify_approvals': self.notify_approvals,
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


class PostApproval(db.Model):
    """Model for post approval tracking via Telegram"""
    __tablename__ = 'post_approvals'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    telegram_account_id = db.Column(db.Integer, db.ForeignKey('telegram_accounts.id'))
    
    # Approval status
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, edited
    approved_via = db.Column(db.String(50), default='telegram')  # telegram, web, auto
    
    # Timestamps
    approved_at = db.Column(db.DateTime)
    rejected_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional info
    rejection_reason = db.Column(db.Text)
    edit_notes = db.Column(db.Text)
    telegram_message_id = db.Column(db.String(100))  # For tracking the approval message
    manual_download_count = db.Column(db.Integer, default=0)
    
    # Relationships
    post = db.relationship('Post', back_populates='approval', uselist=False)
    telegram_account = db.relationship('TelegramAccount', back_populates='approvals')
    
    def __repr__(self):
        return f'<PostApproval {self.post_id} - {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'post_id': self.post_id,
            'telegram_account_id': self.telegram_account_id,
            'status': self.status,
            'approved_via': self.approved_via,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejected_at': self.rejected_at.isoformat() if self.rejected_at else None,
            'rejection_reason': self.rejection_reason,
            'edit_notes': self.edit_notes,
            'telegram_message_id': self.telegram_message_id,
            'manual_download_count': self.manual_download_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def approve(self, via='telegram'):
        """Approve the post"""
        self.status = 'approved'
        self.approved_via = via
        self.approved_at = datetime.utcnow()
        db.session.commit()
    
    def reject(self, reason=None):
        """Reject the post"""
        self.status = 'rejected'
        self.rejected_at = datetime.utcnow()
        self.rejection_reason = reason
        db.session.commit()


class TelegramCommand(db.Model):
    """Model for tracking Telegram bot commands"""
    __tablename__ = 'telegram_commands'
    
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(100), nullable=False)
    command = db.Column(db.String(50), nullable=False)
    parameters = db.Column(db.Text)
    response_status = db.Column(db.String(20))  # success, error, pending
    error_message = db.Column(db.Text)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TelegramCommand {self.command} from {self.chat_id}>'