"""
WebSocket Service for Real-time Updates
Handles broadcasting configuration changes to connected clients
"""
from flask import current_app
from extensions import socketio, redis_client
try:
    from flask_socketio import emit, join_room, leave_room
except ImportError:
    # WebSocket functionality will be disabled
    emit = join_room = leave_room = lambda *args, **kwargs: None
from functools import wraps
import json
from datetime import datetime
from typing import Dict, Any, Optional, List


class WebSocketService:
    """Service for managing WebSocket connections and broadcasts"""
    
    # Event names
    PLATFORM_UPDATE = 'platform_update'
    FEATURE_UPDATE = 'feature_update'
    PACKAGE_UPDATE = 'package_update'
    CONFIG_SYNC = 'config_sync'
    ADMIN_NOTIFICATION = 'admin_notification'
    CLIENT_NOTIFICATION = 'client_notification'
    SYSTEM_STATUS = 'system_status'
    
    # Room prefixes
    ADMIN_ROOM = 'admin'
    CLIENT_ROOM_PREFIX = 'client_'
    GLOBAL_ROOM = 'global'
    
    def __init__(self):
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Set up SocketIO event handlers"""
        
        @socketio.on('connect')
        def handle_connect(auth):
            """Handle client connection"""
            try:
                # Auth should contain token and user type
                if not auth or 'token' not in auth:
                    return False
                
                # Verify token and get user info
                from services.auth_service import auth_service
                user_data = auth_service.decode_token(auth['token'])
                
                if not user_data:
                    return False
                
                # Join appropriate rooms based on user type
                if user_data.get('is_admin'):
                    join_room(self.ADMIN_ROOM)
                    emit('connected', {
                        'message': 'Connected to admin channel',
                        'user_id': user_data['user_id'],
                        'role': user_data.get('admin_role')
                    })
                else:
                    client_id = user_data.get('client_id')
                    if client_id:
                        join_room(f"{self.CLIENT_ROOM_PREFIX}{client_id}")
                        emit('connected', {
                            'message': 'Connected to client channel',
                            'client_id': client_id
                        })
                
                # Everyone joins global room for system-wide updates
                join_room(self.GLOBAL_ROOM)
                
                current_app.logger.info(f"WebSocket connected: {user_data.get('user_id')}")
                return True
                
            except Exception as e:
                current_app.logger.error(f"WebSocket connection error: {str(e)}")
                return False
        
        @socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            current_app.logger.info("WebSocket client disconnected")
        
        @socketio.on('subscribe')
        def handle_subscribe(data):
            """Handle subscription to specific events"""
            event_type = data.get('event_type')
            entity_id = data.get('entity_id')
            
            if event_type and entity_id:
                room_name = f"{event_type}_{entity_id}"
                join_room(room_name)
                emit('subscribed', {
                    'event_type': event_type,
                    'entity_id': entity_id
                })
        
        @socketio.on('unsubscribe')
        def handle_unsubscribe(data):
            """Handle unsubscription from specific events"""
            event_type = data.get('event_type')
            entity_id = data.get('entity_id')
            
            if event_type and entity_id:
                room_name = f"{event_type}_{entity_id}"
                leave_room(room_name)
                emit('unsubscribed', {
                    'event_type': event_type,
                    'entity_id': entity_id
                })
    
    def broadcast_platform_update(self, platform_id: int, platform_data: Dict[str, Any], 
                                  change_type: str = 'update'):
        """Broadcast platform configuration changes"""
        event_data = {
            'type': change_type,
            'platform_id': platform_id,
            'data': platform_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Broadcast to admin room
        socketio.emit(self.PLATFORM_UPDATE, event_data, room=self.ADMIN_ROOM)
        
        # Broadcast to affected clients
        if platform_data.get('is_enabled'):
            # Platform enabled - notify all clients
            socketio.emit(self.PLATFORM_UPDATE, event_data, room=self.GLOBAL_ROOM)
        else:
            # Platform disabled - notify clients using this platform
            self._notify_affected_clients('platform', platform_id, event_data)
        
        # Store in Redis for persistence
        if redis_client:
            try:
                redis_client.publish(f'platform_update_{platform_id}', json.dumps(event_data))
            except Exception as e:
                current_app.logger.error(f"Redis publish error: {str(e)}")
    
    def broadcast_feature_update(self, feature_id: int, feature_data: Dict[str, Any], 
                                 change_type: str = 'update'):
        """Broadcast feature flag changes"""
        event_data = {
            'type': change_type,
            'feature_id': feature_id,
            'data': feature_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Broadcast to admin room
        socketio.emit(self.FEATURE_UPDATE, event_data, room=self.ADMIN_ROOM)
        
        # Notify affected clients based on their packages
        self._notify_affected_clients('feature', feature_id, event_data)
        
        # Store in Redis
        if redis_client:
            try:
                redis_client.publish(f'feature_update_{feature_id}', json.dumps(event_data))
            except Exception as e:
                current_app.logger.error(f"Redis publish error: {str(e)}")
    
    def broadcast_package_update(self, package_id: int, package_data: Dict[str, Any], 
                                 change_type: str = 'update'):
        """Broadcast package changes"""
        event_data = {
            'type': change_type,
            'package_id': package_id,
            'data': package_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Broadcast to admin room
        socketio.emit(self.PACKAGE_UPDATE, event_data, room=self.ADMIN_ROOM)
        
        # Notify clients on this package
        self._notify_clients_by_package(package_id, event_data)
        
        # Store in Redis
        if redis_client:
            try:
                redis_client.publish(f'package_update_{package_id}', json.dumps(event_data))
            except Exception as e:
                current_app.logger.error(f"Redis publish error: {str(e)}")
    
    def broadcast_config_sync(self, client_id: Optional[int] = None):
        """Broadcast configuration sync request"""
        event_data = {
            'type': 'sync_required',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if client_id:
            # Sync specific client
            socketio.emit(self.CONFIG_SYNC, event_data, 
                          room=f"{self.CLIENT_ROOM_PREFIX}{client_id}")
        else:
            # Sync all clients
            socketio.emit(self.CONFIG_SYNC, event_data, room=self.GLOBAL_ROOM)
    
    def send_admin_notification(self, notification_type: str, message: str, 
                                data: Optional[Dict[str, Any]] = None,
                                severity: str = 'info'):
        """Send notification to admin dashboard"""
        event_data = {
            'type': notification_type,
            'message': message,
            'severity': severity,  # info, warning, error, success
            'data': data or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        socketio.emit(self.ADMIN_NOTIFICATION, event_data, room=self.ADMIN_ROOM)
    
    def send_client_notification(self, client_id: int, notification_type: str, 
                                 message: str, data: Optional[Dict[str, Any]] = None):
        """Send notification to specific client"""
        event_data = {
            'type': notification_type,
            'message': message,
            'data': data or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        
        socketio.emit(self.CLIENT_NOTIFICATION, event_data, 
                      room=f"{self.CLIENT_ROOM_PREFIX}{client_id}")
    
    def broadcast_system_status(self, status: str, metrics: Dict[str, Any]):
        """Broadcast system health status"""
        event_data = {
            'status': status,  # healthy, degraded, critical
            'metrics': metrics,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Send to admins
        socketio.emit(self.SYSTEM_STATUS, event_data, room=self.ADMIN_ROOM)
        
        # If critical, notify all clients
        if status == 'critical':
            socketio.emit(self.SYSTEM_STATUS, {
                'status': status,
                'message': 'System experiencing issues',
                'timestamp': event_data['timestamp']
            }, room=self.GLOBAL_ROOM)
    
    def _notify_affected_clients(self, entity_type: str, entity_id: int, 
                                 event_data: Dict[str, Any]):
        """Notify clients affected by entity changes"""
        # This would query the database to find affected clients
        # For now, we'll broadcast to all clients
        socketio.emit(f'{entity_type}_update', event_data, room=self.GLOBAL_ROOM)
    
    def _notify_clients_by_package(self, package_id: int, event_data: Dict[str, Any]):
        """Notify clients on a specific package"""
        # Query clients on this package and notify them
        from models import Client
        try:
            clients = Client.query.filter_by(
                package_id=package_id,
                is_active=True
            ).all()
            
            for client in clients:
                socketio.emit(self.PACKAGE_UPDATE, event_data, 
                              room=f"{self.CLIENT_ROOM_PREFIX}{client.id}")
        except Exception as e:
            current_app.logger.error(f"Error notifying clients: {str(e)}")


# Create singleton instance
websocket_service = WebSocketService()


def websocket_required(f):
    """Decorator to ensure WebSocket functionality is available"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not socketio:
            return {'error': 'WebSocket functionality not available'}, 503
        return f(*args, **kwargs)
    return decorated_function