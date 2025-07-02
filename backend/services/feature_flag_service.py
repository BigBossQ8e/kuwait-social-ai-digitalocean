"""
Feature Flag Management Service
Handles feature flags and sub-features with real-time updates
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import redis
import json
from flask import current_app
from sqlalchemy import func, and_
from sqlalchemy.orm import joinedload

from models import db, FeatureFlag, FeatureSubflag, Client, AdminActivity, ConfigHistory, Package, PackageFeature
from extensions import redis_client
from services.websocket_service import websocket_service

logger = logging.getLogger(__name__)


class FeatureFlagService:
    """Service for managing feature flags and sub-features"""
    
    def __init__(self):
        self.redis_prefix = "feature:"
        self.cache_ttl = 300  # 5 minutes
    
    def get_all_features(self, category: Optional[str] = None, include_disabled: bool = True) -> List[Dict[str, Any]]:
        """Get all feature flags with optional filtering"""
        cache_key = f"{self.redis_prefix}all:{category or 'all'}:{include_disabled}"
        cached = self._get_from_cache(cache_key)
        
        if cached:
            return cached
        
        # Build query
        query = FeatureFlag.query.options(joinedload(FeatureFlag.sub_features))
        
        if category:
            query = query.filter_by(category=category)
        
        if not include_disabled:
            query = query.filter_by(is_enabled=True)
        
        features = query.all()
        result = [f.to_dict(include_sub_features=True) for f in features]
        
        # Cache the result
        self._set_cache(cache_key, result)
        
        return result
    
    def get_feature(self, feature_id: int) -> Optional[FeatureFlag]:
        """Get a specific feature flag"""
        return FeatureFlag.query.options(joinedload(FeatureFlag.sub_features)).get(feature_id)
    
    def get_feature_by_key(self, feature_key: str) -> Optional[FeatureFlag]:
        """Get a feature flag by its key"""
        cache_key = f"{self.redis_prefix}key:{feature_key}"
        cached = self._get_from_cache(cache_key)
        
        if cached:
            return FeatureFlag.query.get(cached['id'])
        
        feature = FeatureFlag.query.filter_by(feature_key=feature_key).first()
        if feature:
            self._set_cache(cache_key, {'id': feature.id})
        
        return feature
    
    def toggle_feature(self, feature_id: int, is_enabled: bool, admin_id: int = None) -> FeatureFlag:
        """Toggle a feature flag"""
        feature = FeatureFlag.query.get_or_404(feature_id)
        old_state = feature.is_enabled
        
        # Update feature state
        feature.is_enabled = is_enabled
        
        # Log the change
        self._log_config_change(
            config_type='feature_flag',
            config_id=feature_id,
            previous_value={'is_enabled': old_state},
            new_value={'is_enabled': is_enabled}
        )
        
        # Log admin activity
        if admin_id:
            self._log_admin_activity(
                admin_id=admin_id,
                action='feature_toggle',
                resource_type='feature_flag',
                resource_id=feature_id,
                changes={
                    'feature': feature.feature_key,
                    'old_state': old_state,
                    'new_state': is_enabled
                }
            )
        
        db.session.commit()
        
        # Clear cache
        self._invalidate_cache()
        
        # Broadcast change
        self._broadcast_feature_change(feature)
        
        return feature
    
    def toggle_sub_feature(self, sub_feature_id: int, is_enabled: bool, admin_id: int = None) -> FeatureSubflag:
        """Toggle a sub-feature"""
        sub_feature = FeatureSubflag.query.get_or_404(sub_feature_id)
        old_state = sub_feature.is_enabled
        
        # Update sub-feature state
        sub_feature.is_enabled = is_enabled
        
        # Log the change
        self._log_config_change(
            config_type='feature_subflag',
            config_id=sub_feature_id,
            previous_value={'is_enabled': old_state},
            new_value={'is_enabled': is_enabled}
        )
        
        # Log admin activity
        if admin_id:
            self._log_admin_activity(
                admin_id=admin_id,
                action='sub_feature_toggle',
                resource_type='feature_subflag',
                resource_id=sub_feature_id,
                changes={
                    'feature': sub_feature.feature.feature_key,
                    'sub_feature': sub_feature.sub_key,
                    'old_state': old_state,
                    'new_state': is_enabled
                }
            )
        
        db.session.commit()
        
        # Clear cache
        self._invalidate_cache()
        
        # Broadcast change
        self._broadcast_feature_change(sub_feature.feature)
        
        return sub_feature
    
    def update_feature_config(self, feature_id: int, updates: Dict[str, Any], admin_id: int = None) -> FeatureFlag:
        """Update feature configuration"""
        feature = FeatureFlag.query.get_or_404(feature_id)
        old_values = {}
        
        # Track changes
        allowed_fields = ['display_name', 'description', 'icon', 'category']
        for field, value in updates.items():
            if field in allowed_fields and hasattr(feature, field):
                old_value = getattr(feature, field)
                if old_value != value:
                    old_values[field] = old_value
                    setattr(feature, field, value)
        
        if old_values:
            # Log the change
            self._log_config_change(
                config_type='feature_flag',
                config_id=feature_id,
                previous_value=old_values,
                new_value={k: v for k, v in updates.items() if k in old_values}
            )
            
            # Log admin activity
            if admin_id:
                self._log_admin_activity(
                    admin_id=admin_id,
                    action='feature_update',
                    resource_type='feature_flag',
                    resource_id=feature_id,
                    changes={
                        'feature': feature.feature_key,
                        'updates': updates
                    }
                )
            
            db.session.commit()
            
            # Clear cache
            self._invalidate_cache()
            
            # Broadcast change
            self._broadcast_feature_change(feature)
        
        return feature
    
    def update_sub_feature_config(self, sub_feature_id: int, config: Dict[str, Any], admin_id: int = None) -> FeatureSubflag:
        """Update sub-feature configuration"""
        sub_feature = FeatureSubflag.query.get_or_404(sub_feature_id)
        old_config = sub_feature.config or {}
        
        # Update config
        sub_feature.config = config
        
        # Log the change
        self._log_config_change(
            config_type='feature_subflag',
            config_id=sub_feature_id,
            previous_value={'config': old_config},
            new_value={'config': config}
        )
        
        # Log admin activity
        if admin_id:
            self._log_admin_activity(
                admin_id=admin_id,
                action='sub_feature_config_update',
                resource_type='feature_subflag',
                resource_id=sub_feature_id,
                changes={
                    'feature': sub_feature.feature.feature_key,
                    'sub_feature': sub_feature.sub_key,
                    'old_config': old_config,
                    'new_config': config
                }
            )
        
        db.session.commit()
        
        # Clear cache
        self._invalidate_cache()
        
        # Broadcast change
        self._broadcast_feature_change(sub_feature.feature)
        
        return sub_feature
    
    def get_client_features(self, client_id: int) -> Dict[str, Any]:
        """Get all enabled features for a specific client based on their package"""
        cache_key = f"{self.redis_prefix}client:{client_id}"
        cached = self._get_from_cache(cache_key)
        
        if cached:
            return cached
        
        # Get client and their package
        client = Client.query.get(client_id)
        if not client or not client.package_id:
            return {'features': {}, 'limits': {}}
        
        # Get package features
        package_features = PackageFeature.query.filter_by(
            package_id=client.package_id,
            is_included=True
        ).join(FeatureFlag).filter(
            FeatureFlag.is_enabled == True
        ).all()
        
        # Build feature map
        features = {}
        for pf in package_features:
            feature = pf.feature
            feature_data = {
                'enabled': True,
                'display_name': feature.display_name,
                'icon': feature.icon,
                'sub_features': {}
            }
            
            # Add sub-features
            for sub in feature.sub_features:
                if sub.is_enabled:
                    feature_data['sub_features'][sub.sub_key] = {
                        'enabled': True,
                        'display_name': sub.display_name,
                        'config': sub.config or {}
                    }
            
            # Apply custom config if any
            if pf.custom_config:
                feature_data.update(pf.custom_config)
            
            features[feature.feature_key] = feature_data
        
        # Get package limits
        package = Package.query.get(client.package_id)
        limits = package.limits or {} if package else {}
        
        result = {
            'features': features,
            'limits': limits,
            'package_name': package.name if package else None
        }
        
        # Cache the result
        self._set_cache(cache_key, result, ttl=600)  # Cache for 10 minutes
        
        return result
    
    def is_feature_enabled_for_client(self, client_id: int, feature_key: str, sub_key: Optional[str] = None) -> bool:
        """Check if a specific feature is enabled for a client"""
        client_features = self.get_client_features(client_id)
        
        if feature_key not in client_features['features']:
            return False
        
        feature = client_features['features'][feature_key]
        if not feature.get('enabled', False):
            return False
        
        if sub_key:
            sub_features = feature.get('sub_features', {})
            return sub_features.get(sub_key, {}).get('enabled', False)
        
        return True
    
    def get_feature_categories(self) -> List[str]:
        """Get all unique feature categories"""
        categories = db.session.query(FeatureFlag.category).distinct().filter(
            FeatureFlag.category != None
        ).all()
        
        return [c[0] for c in categories]
    
    def bulk_toggle_features(self, feature_ids: List[int], is_enabled: bool, admin_id: int = None) -> List[FeatureFlag]:
        """Toggle multiple features at once"""
        features = FeatureFlag.query.filter(FeatureFlag.id.in_(feature_ids)).all()
        
        for feature in features:
            old_state = feature.is_enabled
            feature.is_enabled = is_enabled
            
            # Log each change
            self._log_config_change(
                config_type='feature_flag',
                config_id=feature.id,
                previous_value={'is_enabled': old_state},
                new_value={'is_enabled': is_enabled}
            )
        
        # Log admin activity
        if admin_id and features:
            self._log_admin_activity(
                admin_id=admin_id,
                action='bulk_feature_toggle',
                resource_type='feature_flag',
                resource_id=None,
                changes={
                    'feature_count': len(features),
                    'feature_keys': [f.feature_key for f in features],
                    'new_state': is_enabled
                }
            )
        
        db.session.commit()
        
        # Clear cache
        self._invalidate_cache()
        
        # Broadcast changes
        for feature in features:
            self._broadcast_feature_change(feature)
        
        return features
    
    def _log_config_change(self, config_type: str, config_id: int, previous_value: Dict, new_value: Dict):
        """Log configuration change to history"""
        history = ConfigHistory(
            config_type=config_type,
            config_id=config_id,
            previous_value=previous_value,
            new_value=new_value
        )
        db.session.add(history)
    
    def _log_admin_activity(self, admin_id: int, action: str, resource_type: str, resource_id: Optional[int], changes: Dict):
        """Log admin activity"""
        from flask import request
        
        activity = AdminActivity(
            admin_id=admin_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=changes,
            ip_address=request.remote_addr if request else None
        )
        db.session.add(activity)
    
    def _broadcast_feature_change(self, feature: FeatureFlag):
        """Broadcast feature change to all connected clients"""
        logger.info(f"Feature {feature.feature_key} changed to {'enabled' if feature.is_enabled else 'disabled'}")
        
        # Broadcast via WebSocket
        try:
            websocket_service.broadcast_feature_update(
                feature_id=feature.id,
                feature_data=feature.to_dict(include_sub_features=True),
                change_type='toggle' if hasattr(feature, '_is_toggle') else 'update'
            )
        except Exception as e:
            logger.error(f"WebSocket broadcast error: {e}")
        
        # Also publish to Redis for other services
        if redis_client:
            try:
                redis_client.publish('feature_changes', json.dumps({
                    'feature_key': feature.feature_key,
                    'is_enabled': feature.is_enabled,
                    'timestamp': datetime.utcnow().isoformat()
                }))
            except Exception as e:
                logger.error(f"Redis publish error: {e}")
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        if not redis_client:
            return None
        
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        
        return None
    
    def _set_cache(self, key: str, value: Any, ttl: int = None):
        """Set value in Redis cache"""
        if not redis_client:
            return
        
        try:
            redis_client.setex(
                key,
                ttl or self.cache_ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def _invalidate_cache(self):
        """Invalidate all feature-related cache"""
        if not redis_client:
            return
        
        try:
            # Delete all feature cache keys
            for key in redis_client.scan_iter(f"{self.redis_prefix}*"):
                redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")


# Singleton instance
feature_flag_service = FeatureFlagService()