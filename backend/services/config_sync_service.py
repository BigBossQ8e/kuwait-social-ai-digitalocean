"""
Configuration Sync Service
Handles real-time synchronization of configuration changes across clients
"""
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import json
from flask import current_app
from sqlalchemy import and_, or_

from models import db, Client, PlatformConfig, FeatureFlag, Package, ConfigSync, SocialAccount
from extensions import redis_client
from services.websocket_service import websocket_service
from services.platform_service import platform_service
from services.feature_flag_service import feature_flag_service

logger = logging.getLogger(__name__)


class ConfigSyncService:
    """Service for managing configuration synchronization"""
    
    def __init__(self):
        self.sync_interval = 300  # 5 minutes
        self.sync_cache_prefix = "config_sync:"
        self.pending_syncs: Set[int] = set()
    
    def sync_client_config(self, client_id: int, force: bool = False) -> Dict[str, Any]:
        """Sync configuration for a specific client"""
        try:
            client = Client.query.get(client_id)
            if not client:
                logger.error(f"Client {client_id} not found")
                return {'error': 'Client not found'}
            
            # Check if sync is needed
            if not force and not self._needs_sync(client):
                logger.debug(f"Client {client_id} config is up to date")
                return {'status': 'up_to_date'}
            
            # Get current configuration
            config = self._get_client_config(client)
            
            # Store sync record
            self._record_sync(client_id, config)
            
            # Broadcast update to client
            websocket_service.broadcast_config_sync(client_id)
            
            # Send specific configuration
            websocket_service.send_client_notification(
                client_id=client_id,
                notification_type='config_update',
                message='Configuration updated',
                data=config
            )
            
            logger.info(f"Synced config for client {client_id}")
            return {
                'status': 'synced',
                'config': config,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error syncing client {client_id}: {str(e)}")
            return {'error': str(e)}
    
    def sync_all_clients(self, platform: Optional[str] = None, 
                         package_id: Optional[int] = None) -> Dict[str, Any]:
        """Sync configuration for multiple clients"""
        try:
            # Build query
            query = Client.query.filter_by(is_active=True)
            
            if platform:
                # Get clients using this platform
                query = query.join(SocialAccount).filter(
                    SocialAccount.platform == platform,
                    SocialAccount.is_active == True
                )
            
            if package_id:
                query = query.filter_by(package_id=package_id)
            
            clients = query.all()
            
            # Sync each client
            results = {
                'total': len(clients),
                'synced': 0,
                'failed': 0,
                'errors': []
            }
            
            for client in clients:
                try:
                    result = self.sync_client_config(client.id)
                    if result.get('status') in ['synced', 'up_to_date']:
                        results['synced'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append({
                            'client_id': client.id,
                            'error': result.get('error')
                        })
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({
                        'client_id': client.id,
                        'error': str(e)
                    })
            
            # Broadcast global sync if many clients affected
            if results['synced'] > 10:
                websocket_service.broadcast_config_sync()
            
            logger.info(f"Bulk sync completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk sync: {str(e)}")
            return {'error': str(e)}
    
    def mark_pending_sync(self, client_ids: List[int], reason: str = 'manual'):
        """Mark clients as needing configuration sync"""
        for client_id in client_ids:
            self.pending_syncs.add(client_id)
            
            # Store in Redis for persistence
            if redis_client:
                key = f"{self.sync_cache_prefix}pending:{client_id}"
                redis_client.setex(key, 3600, json.dumps({
                    'reason': reason,
                    'timestamp': datetime.utcnow().isoformat()
                }))
        
        logger.info(f"Marked {len(client_ids)} clients for sync: {reason}")
    
    def process_pending_syncs(self) -> Dict[str, Any]:
        """Process all pending configuration syncs"""
        if not self.pending_syncs:
            return {'processed': 0}
        
        results = {
            'processed': 0,
            'success': 0,
            'failed': 0
        }
        
        # Copy set to avoid modification during iteration
        pending = list(self.pending_syncs)
        
        for client_id in pending:
            try:
                result = self.sync_client_config(client_id, force=True)
                if result.get('status') == 'synced':
                    results['success'] += 1
                else:
                    results['failed'] += 1
                
                # Remove from pending
                self.pending_syncs.discard(client_id)
                if redis_client:
                    redis_client.delete(f"{self.sync_cache_prefix}pending:{client_id}")
                    
            except Exception as e:
                logger.error(f"Error processing sync for client {client_id}: {e}")
                results['failed'] += 1
            
            results['processed'] += 1
        
        return results
    
    def get_sync_status(self, client_id: int) -> Dict[str, Any]:
        """Get sync status for a client"""
        try:
            # Check last sync
            last_sync = ConfigSync.query.filter_by(client_id=client_id)\
                .order_by(ConfigSync.synced_at.desc())\
                .first()
            
            if not last_sync:
                return {
                    'status': 'never_synced',
                    'needs_sync': True
                }
            
            # Check if pending
            is_pending = client_id in self.pending_syncs
            if not is_pending and redis_client:
                is_pending = redis_client.exists(f"{self.sync_cache_prefix}pending:{client_id}")
            
            # Get client for checking if sync needed
            client = Client.query.get(client_id)
            needs_sync = self._needs_sync(client) if client else False
            
            return {
                'status': 'synced',
                'last_sync': last_sync.synced_at.isoformat(),
                'sync_version': last_sync.sync_version,
                'needs_sync': needs_sync,
                'is_pending': is_pending,
                'config_hash': last_sync.config_hash
            }
            
        except Exception as e:
            logger.error(f"Error getting sync status: {e}")
            return {'error': str(e)}
    
    def _needs_sync(self, client: Client) -> bool:
        """Check if client needs configuration sync"""
        # Get last sync
        last_sync = ConfigSync.query.filter_by(client_id=client.id)\
            .order_by(ConfigSync.synced_at.desc())\
            .first()
        
        if not last_sync:
            return True
        
        # Check if too old
        if datetime.utcnow() - last_sync.synced_at > timedelta(seconds=self.sync_interval):
            return True
        
        # Check if configuration changed
        current_hash = self._calculate_config_hash(client)
        if current_hash != last_sync.config_hash:
            return True
        
        # Check if marked as pending
        if client.id in self.pending_syncs:
            return True
        
        return False
    
    def _get_client_config(self, client: Client) -> Dict[str, Any]:
        """Get complete configuration for a client"""
        # Get enabled platforms
        platforms = platform_service.get_enabled_platforms()
        
        # Get client features based on package
        features = feature_flag_service.get_client_features(client.id)
        
        # Get package details
        package = client.package.to_dict() if client.package else None
        
        # Build configuration
        config = {
            'client_id': client.id,
            'platforms': platforms,
            'features': features['features'],
            'limits': features['limits'],
            'package': package,
            'settings': {
                'language': client.language_preference,
                'timezone': client.timezone,
                'notifications_enabled': client.notifications_enabled
            },
            'version': self._get_config_version(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return config
    
    def _calculate_config_hash(self, client: Client) -> str:
        """Calculate hash of client configuration for change detection"""
        import hashlib
        
        # Get configuration components
        config_parts = []
        
        # Platform states
        platforms = PlatformConfig.query.filter_by(is_enabled=True).all()
        config_parts.append(','.join([p.platform for p in platforms]))
        
        # Package and features
        if client.package:
            config_parts.append(f"package:{client.package.id}:{client.package.updated_at}")
            feature_ids = [pf.feature_id for pf in client.package.package_features]
            config_parts.append(','.join(map(str, sorted(feature_ids))))
        
        # Client settings
        config_parts.append(f"settings:{client.updated_at}")
        
        # Calculate hash
        config_string = '|'.join(config_parts)
        return hashlib.md5(config_string.encode()).hexdigest()
    
    def _record_sync(self, client_id: int, config: Dict[str, Any]):
        """Record configuration sync"""
        sync_record = ConfigSync(
            client_id=client_id,
            sync_version=self._get_config_version(),
            config_hash=self._calculate_config_hash(Client.query.get(client_id)),
            synced_data=config
        )
        db.session.add(sync_record)
        db.session.commit()
        
        # Cache the sync
        if redis_client:
            key = f"{self.sync_cache_prefix}last:{client_id}"
            redis_client.setex(key, 3600, json.dumps({
                'synced_at': datetime.utcnow().isoformat(),
                'version': sync_record.sync_version,
                'hash': sync_record.config_hash
            }))
    
    def _get_config_version(self) -> str:
        """Get current configuration version"""
        # This could be based on deployment version or timestamp
        return f"v1.0.{datetime.utcnow().strftime('%Y%m%d')}"
    
    def cleanup_old_syncs(self, days: int = 7):
        """Clean up old sync records"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        deleted = ConfigSync.query.filter(
            ConfigSync.synced_at < cutoff
        ).delete()
        
        db.session.commit()
        logger.info(f"Cleaned up {deleted} old sync records")
        
        return deleted


# Create singleton instance
config_sync_service = ConfigSyncService()