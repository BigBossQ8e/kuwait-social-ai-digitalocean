"""
Client Error Model
Stores frontend errors for monitoring and analysis
"""

from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from . import db


class ClientError(db.Model):
    """Model for storing client-side errors"""
    __tablename__ = 'client_errors'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Error details
    type = db.Column(db.String(50), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), default='error', index=True)
    
    # Source information
    source = db.Column(db.String(500))  # File/URL where error occurred
    line_number = db.Column(db.Integer)
    column_number = db.Column(db.Integer)
    stack_trace = db.Column(db.Text)
    
    # Session and user info
    session_id = db.Column(db.String(100), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    user_role = db.Column(db.String(20))
    
    # Client information
    user_agent = db.Column(db.String(500))
    client_ip = db.Column(db.String(45))  # Support IPv6
    
    # Additional context
    context = db.Column(JSON, default={})
    error_metadata = db.Column(JSON, default={})
    
    # Timestamps
    timestamp = db.Column(db.DateTime, nullable=False)  # When error occurred on client
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # When received by server
    
    # Relationships
    user = db.relationship('User', backref='client_errors', lazy=True)
    
    # Indexes for common queries
    __table_args__ = (
        db.Index('idx_client_errors_type_severity', 'type', 'severity'),
        db.Index('idx_client_errors_timestamp', 'timestamp'),
        db.Index('idx_client_errors_session_user', 'session_id', 'user_id'),
    )
    
    def __repr__(self):
        return f'<ClientError {self.id}: {self.type} - {self.message[:50]}>'
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'type': self.type,
            'message': self.message,
            'severity': self.severity,
            'source': self.source,
            'line': self.line_number,
            'column': self.column_number,
            'sessionId': self.session_id,
            'userId': self.user_id,
            'userAgent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_error_summary(cls, hours=24):
        """Get error summary for the last N hours"""
        from datetime import timedelta
        from sqlalchemy import func
        
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        return db.session.query(
            cls.type,
            cls.severity,
            func.count(cls.id).label('count')
        ).filter(
            cls.created_at >= start_time
        ).group_by(
            cls.type,
            cls.severity
        ).all()
    
    @classmethod
    def get_frequent_errors(cls, limit=10, hours=24):
        """Get most frequent error messages"""
        from datetime import timedelta
        from sqlalchemy import func
        
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        return db.session.query(
            cls.message,
            cls.type,
            func.count(cls.id).label('occurrences')
        ).filter(
            cls.created_at >= start_time
        ).group_by(
            cls.message,
            cls.type
        ).order_by(
            func.count(cls.id).desc()
        ).limit(limit).all()
    
    @classmethod
    def get_affected_users(cls, hours=24):
        """Get count of users affected by errors"""
        from datetime import timedelta
        from sqlalchemy import func
        
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        return db.session.query(
            func.count(func.distinct(cls.user_id))
        ).filter(
            cls.created_at >= start_time,
            cls.user_id.isnot(None)
        ).scalar()
    
    @classmethod
    def cleanup_old_errors(cls, days=30):
        """Remove old error logs"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted = cls.query.filter(
            cls.created_at < cutoff_date
        ).delete()
        
        db.session.commit()
        return deleted