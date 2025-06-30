from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from models.base import Base

class Translation(Base):
    __tablename__ = 'translations'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=False)
    locale = Column(String(10), nullable=False)
    value = Column(Text, nullable=False)
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    creator = relationship('User', foreign_keys=[created_by])
    history = relationship('TranslationHistory', back_populates='translation', cascade='all, delete-orphan')
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('key', 'locale', name='_key_locale_uc'),
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


class TranslationHistory(Base):
    __tablename__ = 'translation_history'
    
    id = Column(Integer, primary_key=True)
    translation_id = Column(Integer, ForeignKey('translations.id', ondelete='CASCADE'), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    changed_by = Column(Integer, ForeignKey('users.id'))
    changed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    translation = relationship('Translation', back_populates='history')
    changer = relationship('User', foreign_keys=[changed_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'translation_id': self.translation_id,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'changed_by': self.changed_by,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None
        }