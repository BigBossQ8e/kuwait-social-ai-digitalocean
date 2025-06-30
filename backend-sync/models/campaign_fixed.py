from datetime import datetime
from .core import db

class Campaign(db.Model):
    """Marketing campaign for organizing posts and tracking performance"""
    __tablename__ = 'campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False, index=True)
    
    # Campaign details
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    campaign_type = db.Column(db.String(50))  # product_launch, seasonal, awareness, etc.
    
    # Campaign goals
    objective = db.Column(db.String(100))  # engagement, conversions, brand_awareness, etc.
    target_audience = db.Column(db.JSON)  # Demographics and interests
    budget = db.Column(db.Float)
    
    # Duration
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, paused, completed
    
    # Performance metrics
    performance_metrics = db.Column(db.JSON, default={})
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Note: Relationships to posts and scheduled_posts are handled via foreign keys
    # without explicit SQLAlchemy relationships to avoid circular dependencies
    
    def __repr__(self):
        return f'<Campaign {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'name': self.name,
            'description': self.description,
            'campaign_type': self.campaign_type,
            'objective': self.objective,
            'target_audience': self.target_audience,
            'budget': self.budget,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'performance_metrics': self.performance_metrics,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
