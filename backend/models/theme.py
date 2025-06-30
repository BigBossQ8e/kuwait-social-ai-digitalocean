"""
Theme and branding models for Kuwait Social AI
"""

from datetime import datetime
from sqlalchemy import JSON
from extensions import db


class ThemeSetting(db.Model):
    """Individual theme settings"""
    __tablename__ = 'theme_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(50), nullable=False, default='text')
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    updater = db.relationship('User', backref='theme_updates')
    
    def to_dict(self):
        return {
            'key': self.setting_key,
            'value': self.setting_value,
            'type': self.setting_type,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_all_settings(cls):
        """Get all settings as a dictionary"""
        settings = cls.query.all()
        return {s.setting_key: s.setting_value for s in settings}
    
    @classmethod
    def update_setting(cls, key, value, user_id=None):
        """Update or create a setting"""
        setting = cls.query.filter_by(setting_key=key).first()
        if setting:
            setting.setting_value = value
            setting.updated_by = user_id
        else:
            setting = cls(
                setting_key=key,
                setting_value=value,
                updated_by=user_id
            )
            db.session.add(setting)
        db.session.commit()
        return setting


class ThemePreset(db.Model):
    """Complete theme configurations"""
    __tablename__ = 'theme_presets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    settings = db.Column(JSON, nullable=False)
    screenshot_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_themes')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_themes')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'settings': self.settings,
            'screenshot_url': self.screenshot_url,
            'is_active': self.is_active,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def activate(self, user_id=None):
        """Activate this preset and deactivate others"""
        # Deactivate all presets
        ThemePreset.query.update({'is_active': False})
        
        # Activate this preset
        self.is_active = True
        self.updated_by = user_id
        
        # Apply settings to theme_settings table
        for key, value in self.settings.items():
            ThemeSetting.update_setting(key, value, user_id)
        
        # Record in history
        history = ThemeHistory(
            preset_id=self.id,
            settings_snapshot=self.settings,
            changed_by=user_id,
            change_reason=f"Activated theme: {self.name}"
        )
        db.session.add(history)
        db.session.commit()
        
        return True
    
    @classmethod
    def get_active(cls):
        """Get the currently active theme"""
        return cls.query.filter_by(is_active=True).first()


class ThemeHistory(db.Model):
    """Track theme changes for audit and rollback"""
    __tablename__ = 'theme_history'
    
    id = db.Column(db.Integer, primary_key=True)
    preset_id = db.Column(db.Integer, db.ForeignKey('theme_presets.id'))
    settings_snapshot = db.Column(JSON, nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    change_reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    preset = db.relationship('ThemePreset', backref='history')
    changer = db.relationship('User', backref='theme_changes')
    
    def to_dict(self):
        return {
            'id': self.id,
            'preset_id': self.preset_id,
            'preset_name': self.preset.name if self.preset else None,
            'settings_snapshot': self.settings_snapshot,
            'changed_by': self.changer.email if self.changer else None,
            'change_reason': self.change_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }