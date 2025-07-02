"""
Platform Management Service
Handles platform configuration and real-time updates
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import redis
import json
from flask import current_app
from sqlalchemy import func

from models import db, PlatformConfig, Client, SocialAccount, AdminActivity, ConfigHistory
from extensions import redis_client
from services.websocket_service import websocket_service

logger = logging.getLogger(__name__)


class PlatformService:
    """Service for managing platform configurations"""
    
    def __init__(self):
        self.redis_prefix = "platform:"
        self.cache_ttl = 300  # 5 minutes
    
    def get_all_platforms(self, include_stats: bool = False) -> List[Dict[str, Any]]:
        """Get all platform configurations with optional statistics"""
        # Try cache first
        cache_key = f"{self.redis_prefix}all"
        cached = self._get_from_cache(cache_key)
        
        if cached and not include_stats:
            return cached
        
        # Get from database
        platforms = PlatformConfig.query.all()
        result = []
        
        for platform in platforms:
            platform_data = platform.to_dict()
            
            if include_stats:
                # Get active client count
                active_count = db.session.query(func.count(SocialAccount.id))\
                    .filter(SocialAccount.platform == platform.platform)\
                    .filter(SocialAccount.is_active == True)\
                    .scalar()
                
                platform_data['active_clients'] = active_count
                platform_data['stats'] = self._get_platform_stats(platform.platform)
            
            result.append(platform_data)
        
        # Cache the result
        if not include_stats:
            self._set_cache(cache_key, result)
        
        return result
    
    def get_platform(self, platform_id: int) -> Optional[PlatformConfig]:
        """Get a specific platform configuration"""
        return PlatformConfig.query.get(platform_id)
    
    def toggle_platform(self, platform_id: int, is_enabled: bool, admin_id: int = None) -> PlatformConfig:
        """Toggle platform availability"""
        platform = PlatformConfig.query.get_or_404(platform_id)
        old_state = platform.is_enabled
        
        # Update platform state
        platform.is_enabled = is_enabled
        platform.updated_at = datetime.utcnow()
        
        # Log the change
        self._log_config_change(
            config_type='platform',
            config_id=platform_id,
            previous_value={'is_enabled': old_state},
            new_value={'is_enabled': is_enabled}
        )
        
        # Log admin activity
        if admin_id:
            self._log_admin_activity(
                admin_id=admin_id,
                action='platform_toggle',
                resource_type='platform',
                resource_id=platform_id,
                changes={
                    'platform': platform.platform,
                    'old_state': old_state,
                    'new_state': is_enabled
                }
            )
        
        db.session.commit()
        
        # Clear cache
        self._invalidate_cache()
        
        # Broadcast change (will be implemented with WebSocket)
        self._broadcast_platform_change(platform)
        
        return platform
    
    def update_platform_config(self, platform_id: int, updates: Dict[str, Any], admin_id: int = None) -> PlatformConfig:
        """Update platform configuration"""
        platform = PlatformConfig.query.get_or_404(platform_id)
        old_values = {}
        
        # Track changes
        for field, value in updates.items():
            if hasattr(platform, field) and getattr(platform, field) != value:
                old_values[field] = getattr(platform, field)
                setattr(platform, field, value)
        
        if old_values:
            platform.updated_at = datetime.utcnow()
            
            # Log the change
            self._log_config_change(
                config_type='platform',
                config_id=platform_id,
                previous_value=old_values,
                new_value=updates
            )
            
            # Log admin activity
            if admin_id:
                self._log_admin_activity(
                    admin_id=admin_id,
                    action='platform_update',
                    resource_type='platform',
                    resource_id=platform_id,
                    changes={
                        'platform': platform.platform,
                        'updates': updates
                    }
                )
            
            db.session.commit()
            
            # Clear cache
            self._invalidate_cache()
            
            # Broadcast change
            self._broadcast_platform_change(platform)
        
        return platform
    
    def get_platform_stats(self, platform: str) -> Dict[str, Any]:
        """Get detailed statistics for a platform"""
        stats_key = f"{self.redis_prefix}stats:{platform}"
        cached = self._get_from_cache(stats_key)
        
        if cached:
            return cached
        
        stats = self._calculate_platform_stats(platform)
        self._set_cache(stats_key, stats, ttl=60)  # Cache for 1 minute
        
        return stats
    
    def get_enabled_platforms_for_client(self, client_id: int) -> List[str]:
        """Get list of enabled platforms for a specific client"""
        # Get globally enabled platforms
        enabled_platforms = PlatformConfig.query.filter_by(is_enabled=True).all()
        
        # Get client's package
        client = Client.query.get(client_id)
        if not client:
            return []
        
        # Filter based on package features if applicable
        platform_list = []
        for platform in enabled_platforms:
            # Check if client's package includes this platform
            if self._client_has_platform_access(client, platform.platform):
                platform_list.append(platform.platform)
        
        return platform_list
    
    def _calculate_platform_stats(self, platform: str) -> Dict[str, Any]:
        """Calculate detailed statistics for a platform"""
        from models import Post, PostAnalytics
        
        # Get basic counts
        total_accounts = db.session.query(func.count(SocialAccount.id))\
            .filter(SocialAccount.platform == platform)\
            .scalar()
        
        active_accounts = db.session.query(func.count(SocialAccount.id))\
            .filter(SocialAccount.platform == platform)\
            .filter(SocialAccount.is_active == True)\
            .scalar()
        
        # Get post statistics
        total_posts = db.session.query(func.count(Post.id))\
            .join(SocialAccount)\
            .filter(SocialAccount.platform == platform)\
            .scalar()
        
        # Get engagement statistics
        total_engagement = db.session.query(
            func.sum(PostAnalytics.likes + PostAnalytics.comments + PostAnalytics.shares)
        ).join(Post).join(SocialAccount)\
            .filter(SocialAccount.platform == platform)\
            .scalar() or 0
        
        return {
            'total_accounts': total_accounts,
            'active_accounts': active_accounts,
            'total_posts': total_posts,
            'total_engagement': total_engagement,
            'activity_rate': (active_accounts / total_accounts * 100) if total_accounts > 0 else 0,
            'avg_engagement_per_post': (total_engagement / total_posts) if total_posts > 0 else 0
        }
    
    def _client_has_platform_access(self, client: Client, platform: str) -> bool:
        """Check if client's package includes access to a platform"""
        # For now, simplified logic - can be enhanced based on package features
        return True
    
    def _log_config_change(self, config_type: str, config_id: int, previous_value: Dict, new_value: Dict):
        """Log configuration change to history"""
        history = ConfigHistory(
            config_type=config_type,
            config_id=config_id,
            previous_value=previous_value,
            new_value=new_value
        )
        db.session.add(history)
    
    def _log_admin_activity(self, admin_id: int, action: str, resource_type: str, resource_id: int, changes: Dict):
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
    
    def _broadcast_platform_change(self, platform: PlatformConfig):
        """Broadcast platform change to all connected clients"""
        logger.info(f"Platform {platform.platform} changed to {'enabled' if platform.is_enabled else 'disabled'}")
        
        # Broadcast via WebSocket
        try:
            websocket_service.broadcast_platform_update(
                platform_id=platform.id,
                platform_data=platform.to_dict(),
                change_type='toggle' if hasattr(platform, '_is_toggle') else 'update'
            )
        except Exception as e:
            logger.error(f"WebSocket broadcast error: {e}")
        
        # Also publish to Redis for other services
        if redis_client:
            try:
                redis_client.publish('platform_changes', json.dumps({
                    'platform': platform.platform,
                    'is_enabled': platform.is_enabled,
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
        """Invalidate all platform-related cache"""
        if not redis_client:
            return
        
        try:
            # Delete all platform cache keys
            for key in redis_client.scan_iter(f"{self.redis_prefix}*"):
                redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")


# Singleton instance
platform_service = PlatformService()