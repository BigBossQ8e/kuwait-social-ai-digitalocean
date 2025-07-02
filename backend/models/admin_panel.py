"""
Admin Panel Models
Models for platform configuration, feature flags, and admin functionality
"""
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, JSON, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from models import db


class PlatformConfig(db.Model):
    """Platform configuration for social media platforms"""
    __tablename__ = 'platform_configs'
    
    id = Column(Integer, primary_key=True)
    platform = Column(String(50), unique=True, nullable=False)
    is_enabled = Column(Boolean, default=False)
    icon = Column(String(10))
    display_name = Column(String(100))
    api_endpoint = Column(String(500))
    active_clients = Column(Integer, default=0)
    created_at = Column(db.DateTime, default=datetime.utcnow)
    updated_at = Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'platform': self.platform,
            'is_enabled': self.is_enabled,
            'icon': self.icon,
            'display_name': self.display_name,
            'api_endpoint': self.api_endpoint,
            'active_clients': self.active_clients,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class FeatureFlag(db.Model):
    """Feature flags for controlling platform features"""
    __tablename__ = 'feature_flags'
    
    id = Column(Integer, primary_key=True)
    feature_key = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))
    display_name = Column(String(200))
    description = Column(db.Text)
    is_enabled = Column(Boolean, default=True)
    icon = Column(String(10))
    created_at = Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sub_features = relationship('FeatureSubflag', back_populates='feature', cascade='all, delete-orphan')
    package_mappings = relationship('PackageFeature', back_populates='feature')
    
    def to_dict(self, include_sub_features: bool = True) -> Dict[str, Any]:
        data = {
            'id': self.id,
            'feature_key': self.feature_key,
            'category': self.category,
            'display_name': self.display_name,
            'description': self.description,
            'is_enabled': self.is_enabled,
            'icon': self.icon,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sub_features:
            data['sub_features'] = [sf.to_dict() for sf in self.sub_features]
        
        return data


class FeatureSubflag(db.Model):
    """Sub-features under main feature flags"""
    __tablename__ = 'feature_subflags'
    
    id = Column(Integer, primary_key=True)
    feature_id = Column(Integer, ForeignKey('feature_flags.id', ondelete='CASCADE'))
    sub_key = Column(String(100), nullable=False)
    display_name = Column(String(200))
    is_enabled = Column(Boolean, default=True)
    config = Column(JSON)
    
    # Relationships
    feature = relationship('FeatureFlag', back_populates='sub_features')
    
    __table_args__ = (
        UniqueConstraint('feature_id', 'sub_key', name='uq_feature_sub_key'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'feature_id': self.feature_id,
            'sub_key': self.sub_key,
            'display_name': self.display_name,
            'is_enabled': self.is_enabled,
            'config': self.config
        }


class Package(db.Model):
    """Service packages with pricing and features"""
    __tablename__ = 'packages'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(100))
    description = Column(db.Text)
    price_kwd = Column(DECIMAL(10, 2))
    billing_period = Column(String(20), default='monthly')
    is_active = Column(Boolean, default=True)
    features = Column(JSON)  # Quick feature summary
    limits = Column(JSON)    # Usage limits
    created_at = Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    feature_mappings = relationship('PackageFeature', back_populates='package', cascade='all, delete-orphan')
    
    def to_dict(self, include_features: bool = False) -> Dict[str, Any]:
        data = {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'price_kwd': float(self.price_kwd) if self.price_kwd else 0,
            'billing_period': self.billing_period,
            'is_active': self.is_active,
            'features': self.features,
            'limits': self.limits,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_features:
            data['included_features'] = [
                pm.feature.to_dict(include_sub_features=False) 
                for pm in self.feature_mappings 
                if pm.is_included
            ]
        
        return data


class PackageFeature(db.Model):
    """Mapping between packages and features"""
    __tablename__ = 'package_features'
    
    id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey('packages.id', ondelete='CASCADE'))
    feature_id = Column(Integer, ForeignKey('feature_flags.id', ondelete='CASCADE'))
    is_included = Column(Boolean, default=True)
    custom_config = Column(JSON)
    
    # Relationships
    package = relationship('Package', back_populates='feature_mappings')
    feature = relationship('FeatureFlag', back_populates='package_mappings')
    
    __table_args__ = (
        UniqueConstraint('package_id', 'feature_id', name='uq_package_feature'),
    )


class APIConfig(db.Model):
    """API configuration for external services"""
    __tablename__ = 'api_configs'
    
    id = Column(Integer, primary_key=True)
    service_name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))
    api_key = Column(db.Text)  # Encrypted
    api_secret = Column(db.Text)  # Encrypted
    endpoint = Column(String(500))
    is_active = Column(Boolean, default=True)
    monthly_budget = Column(DECIMAL(10, 2))
    current_usage = Column(DECIMAL(10, 2), default=0)
    last_checked = Column(db.DateTime)
    health_status = Column(String(20), default='unknown')
    config = Column(JSON)
    created_at = Column(db.DateTime, default=datetime.utcnow)
    updated_at = Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        data = {
            'id': self.id,
            'service_name': self.service_name,
            'category': self.category,
            'endpoint': self.endpoint,
            'is_active': self.is_active,
            'monthly_budget': float(self.monthly_budget) if self.monthly_budget else None,
            'current_usage': float(self.current_usage) if self.current_usage else 0,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'health_status': self.health_status,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data['has_api_key'] = bool(self.api_key)
            data['has_api_secret'] = bool(self.api_secret)
        
        return data


class AdminActivity(db.Model):
    """Log of admin activities for audit trail"""
    __tablename__ = 'admin_activities'
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey('admins.id'))
    action = Column(String(100))
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    changes = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    admin = relationship('Admin', backref='activities')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'admin_id': self.admin_id,
            'admin_name': self.admin.full_name if self.admin else None,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'changes': self.changes,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ConfigHistory(db.Model):
    """History of configuration changes"""
    __tablename__ = 'config_history'
    
    id = Column(Integer, primary_key=True)
    config_type = Column(String(50))
    config_id = Column(Integer)
    previous_value = Column(JSON)
    new_value = Column(JSON)
    changed_by = Column(Integer, ForeignKey('users.id'))
    changed_at = Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'config_type': self.config_type,
            'config_id': self.config_id,
            'previous_value': self.previous_value,
            'new_value': self.new_value,
            'changed_by': self.changed_by,
            'changed_by_email': self.user.email if self.user else None,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None
        }


class ConfigCache(db.Model):
    """Cache for real-time configuration updates"""
    __tablename__ = 'config_cache'
    
    id = Column(Integer, primary_key=True)
    cache_key = Column(String(255), unique=True, nullable=False)
    cache_value = Column(JSON)
    expires_at = Column(db.DateTime)
    created_at = Column(db.DateTime, default=datetime.utcnow)
    updated_at = Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'cache_key': self.cache_key,
            'cache_value': self.cache_value,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ConfigSync(db.Model):
    """Configuration sync tracking for clients"""
    __tablename__ = 'config_syncs'
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    sync_version = Column(String(50))
    config_hash = Column(String(64))  # MD5 hash of configuration
    synced_data = Column(JSON)  # Store the actual synced configuration
    synced_at = Column(db.DateTime, default=datetime.utcnow)
    sync_status = Column(String(20), default='success')  # success, failed, partial
    error_message = Column(db.Text)
    
    # Relationships
    client = relationship('Client', backref='config_syncs')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_config_sync_client', 'client_id'),
        Index('idx_config_sync_timestamp', 'synced_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'client_id': self.client_id,
            'sync_version': self.sync_version,
            'config_hash': self.config_hash,
            'synced_at': self.synced_at.isoformat() if self.synced_at else None,
            'sync_status': self.sync_status,
            'error_message': self.error_message
        }