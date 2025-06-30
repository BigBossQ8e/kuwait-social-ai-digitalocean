from datetime import datetime
from extensions import db

class Translation(db.Model):
    __tablename__ = 'translations'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), nullable=False)
    locale = db.Column(db.String(10), nullable=False)
    value = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])
    history = db.relationship('TranslationHistory', back_populates='translation', cascade='all, delete-orphan')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('key', 'locale', name='_key_locale_uc'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'locale': self.locale,
            'value': self.value,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }


class TranslationHistory(db.Model):
    __tablename__ = 'translation_history'
    
    id = db.Column(db.Integer, primary_key=True)
    translation_id = db.Column(db.Integer, db.ForeignKey('translations.id', ondelete='CASCADE'), nullable=False)
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    translation = db.relationship('Translation', back_populates='history')
    changer = db.relationship('User', foreign_keys=[changed_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'translation_id': self.translation_id,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'changed_by': self.changed_by,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None
        }