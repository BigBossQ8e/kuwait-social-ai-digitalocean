"""
Admin WebSocket Routes
Handles real-time communication for admin panel
"""
from flask import Blueprint, request
from flask_socketio import emit, join_room, leave_room
from extensions import socketio
from services.websocket_service import websocket_service
from utils.decorators import admin_required
from flask_jwt_extended import decode_token
import logging

logger = logging.getLogger(__name__)

admin_ws_bp = Blueprint('admin_websocket', __name__)


@socketio.on('admin_connect', namespace='/admin')
def handle_admin_connect(auth_data):
    """Handle admin WebSocket connection"""
    try:
        # Validate admin authentication
        token = auth_data.get('token')
        if not token:
            emit('error', {'message': 'Authentication required'})
            return False
        
        # Decode and validate token
        try:
            from services.auth_service import auth_service
            user_data = auth_service.decode_token(token)
            
            if not user_data or not user_data.get('is_admin'):
                emit('error', {'message': 'Admin access required'})
                return False
            
            # Join admin room and role-specific room
            join_room('admin')
            admin_role = user_data.get('admin_role', 'admin')
            join_room(f'admin_{admin_role}')
            
            # Send connection confirmation
            emit('admin_connected', {
                'user_id': user_data['user_id'],
                'role': admin_role,
                'permissions': user_data.get('permissions', [])
            })
            
            logger.info(f"Admin connected: {user_data['user_id']} with role {admin_role}")
            return True
            
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            emit('error', {'message': 'Invalid authentication'})
            return False
            
    except Exception as e:
        logger.error(f"Admin connection error: {str(e)}")
        emit('error', {'message': 'Connection failed'})
        return False


@socketio.on('admin_disconnect', namespace='/admin')
def handle_admin_disconnect():
    """Handle admin disconnection"""
    logger.info("Admin disconnected")
    leave_room('admin')


@socketio.on('request_dashboard_update', namespace='/admin')
def handle_dashboard_update_request(data):
    """Handle request for dashboard data update"""
    try:
        update_type = data.get('type', 'all')
        
        # Import here to avoid circular imports
        from routes.admin.dashboard import get_dashboard_data
        
        # Get fresh dashboard data
        dashboard_data = get_dashboard_data(update_type)
        
        # Emit update to requesting admin
        emit('dashboard_update', {
            'type': update_type,
            'data': dashboard_data,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Dashboard update error: {str(e)}")
        emit('error', {'message': 'Failed to fetch dashboard data'})


@socketio.on('request_activity_feed', namespace='/admin')
def handle_activity_feed_request(data):
    """Handle request for activity feed updates"""
    try:
        limit = data.get('limit', 50)
        offset = data.get('offset', 0)
        
        # Get activity feed
        from models import AdminAuditLog
        activities = AdminAuditLog.query\
            .order_by(AdminAuditLog.created_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        # Format and emit
        activity_data = [activity.to_dict() for activity in activities]
        
        emit('activity_feed_update', {
            'activities': activity_data,
            'has_more': len(activity_data) == limit,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Activity feed error: {str(e)}")
        emit('error', {'message': 'Failed to fetch activity feed'})


@socketio.on('subscribe_entity_updates', namespace='/admin')
def handle_entity_subscription(data):
    """Subscribe to updates for specific entities"""
    try:
        entity_type = data.get('entity_type')  # platform, feature, package, client
        entity_id = data.get('entity_id')
        
        if entity_type and entity_id:
            room_name = f"{entity_type}_{entity_id}"
            join_room(room_name)
            
            emit('subscribed', {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'room': room_name
            })
            
            logger.info(f"Admin subscribed to {room_name}")
        
    except Exception as e:
        logger.error(f"Subscription error: {str(e)}")
        emit('error', {'message': 'Failed to subscribe'})


@socketio.on('unsubscribe_entity_updates', namespace='/admin')
def handle_entity_unsubscription(data):
    """Unsubscribe from entity updates"""
    try:
        entity_type = data.get('entity_type')
        entity_id = data.get('entity_id')
        
        if entity_type and entity_id:
            room_name = f"{entity_type}_{entity_id}"
            leave_room(room_name)
            
            emit('unsubscribed', {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'room': room_name
            })
            
    except Exception as e:
        logger.error(f"Unsubscription error: {str(e)}")


@socketio.on('broadcast_announcement', namespace='/admin')
def handle_broadcast_announcement(data):
    """Handle admin broadcasting announcements"""
    try:
        # Verify admin has permission to broadcast
        # This would check the token and permissions
        
        announcement_type = data.get('type', 'info')
        message = data.get('message')
        target = data.get('target', 'all')  # all, admins, clients, specific_client
        
        if not message:
            emit('error', {'message': 'Message is required'})
            return
        
        announcement_data = {
            'type': announcement_type,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Broadcast based on target
        if target == 'all':
            socketio.emit('announcement', announcement_data, namespace='/')
        elif target == 'admins':
            socketio.emit('announcement', announcement_data, room='admin', namespace='/admin')
        elif target == 'clients':
            socketio.emit('announcement', announcement_data, room='clients', namespace='/client')
        elif target.startswith('client_'):
            client_id = target.replace('client_', '')
            socketio.emit('announcement', announcement_data, 
                          room=f'client_{client_id}', namespace='/client')
        
        emit('announcement_sent', {
            'target': target,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"Broadcast error: {str(e)}")
        emit('error', {'message': 'Failed to broadcast announcement'})


@socketio.on('request_system_metrics', namespace='/admin')
def handle_system_metrics_request():
    """Handle request for real-time system metrics"""
    try:
        # Get system metrics
        from services.monitoring_service import monitoring_service
        metrics = monitoring_service.get_current_metrics()
        
        emit('system_metrics_update', {
            'metrics': metrics,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Metrics error: {str(e)}")
        emit('error', {'message': 'Failed to fetch system metrics'})


# Import datetime for timestamps
from datetime import datetime