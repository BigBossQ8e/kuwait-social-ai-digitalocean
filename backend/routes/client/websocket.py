"""
Client WebSocket Routes
Handles real-time communication for client applications
"""
from flask import Blueprint, request
from flask_socketio import emit, join_room, leave_room
from extensions import socketio
from services.websocket_service import websocket_service
from utils.decorators import client_required
from flask_jwt_extended import decode_token
import logging

logger = logging.getLogger(__name__)

client_ws_bp = Blueprint('client_websocket', __name__)


@socketio.on('client_connect', namespace='/client')
def handle_client_connect(auth_data):
    """Handle client WebSocket connection"""
    try:
        # Validate client authentication
        token = auth_data.get('token')
        if not token:
            emit('error', {'message': 'Authentication required'})
            return False
        
        # Decode and validate token
        try:
            from services.auth_service import auth_service
            user_data = auth_service.decode_token(token)
            
            if not user_data or not user_data.get('client_id'):
                emit('error', {'message': 'Client access required'})
                return False
            
            client_id = user_data['client_id']
            
            # Join client-specific room
            join_room(f'client_{client_id}')
            join_room('clients')  # General clients room
            
            # Get client's current configuration
            from services.feature_flag_service import feature_flag_service
            from services.platform_service import platform_service
            
            client_features = feature_flag_service.get_client_features(client_id)
            available_platforms = platform_service.get_enabled_platforms()
            
            # Send connection confirmation with current config
            emit('client_connected', {
                'client_id': client_id,
                'features': client_features,
                'platforms': available_platforms,
                'message': 'Connected to real-time updates'
            })
            
            logger.info(f"Client connected: {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            emit('error', {'message': 'Invalid authentication'})
            return False
            
    except Exception as e:
        logger.error(f"Client connection error: {str(e)}")
        emit('error', {'message': 'Connection failed'})
        return False


@socketio.on('client_disconnect', namespace='/client')
def handle_client_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected")
    leave_room('clients')


@socketio.on('config_check', namespace='/client')
def handle_config_check(data):
    """Handle client request to check current configuration"""
    try:
        # Get client ID from session/token
        from flask_socketio import request as ws_request
        client_id = data.get('client_id')
        
        if not client_id:
            emit('error', {'message': 'Client ID required'})
            return
        
        # Get current configuration
        from services.feature_flag_service import feature_flag_service
        from services.platform_service import platform_service
        
        features = feature_flag_service.get_client_features(client_id)
        platforms = platform_service.get_enabled_platforms()
        
        emit('config_update', {
            'features': features,
            'platforms': platforms,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Config check error: {str(e)}")
        emit('error', {'message': 'Failed to fetch configuration'})


@socketio.on('feature_check', namespace='/client')
def handle_feature_check(data):
    """Check if a specific feature is enabled for client"""
    try:
        client_id = data.get('client_id')
        feature_key = data.get('feature_key')
        sub_key = data.get('sub_key')
        
        if not client_id or not feature_key:
            emit('error', {'message': 'Client ID and feature key required'})
            return
        
        from services.feature_flag_service import feature_flag_service
        
        is_enabled = feature_flag_service.is_feature_enabled_for_client(
            client_id=client_id,
            feature_key=feature_key,
            sub_key=sub_key
        )
        
        emit('feature_check_result', {
            'feature_key': feature_key,
            'sub_key': sub_key,
            'is_enabled': is_enabled,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Feature check error: {str(e)}")
        emit('error', {'message': 'Failed to check feature'})


@socketio.on('report_metrics', namespace='/client')
def handle_metrics_report(data):
    """Handle client reporting usage metrics"""
    try:
        client_id = data.get('client_id')
        metrics = data.get('metrics', {})
        
        if not client_id:
            emit('error', {'message': 'Client ID required'})
            return
        
        # Store metrics (would be processed by monitoring service)
        logger.info(f"Received metrics from client {client_id}: {metrics}")
        
        # Acknowledge receipt
        emit('metrics_received', {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Metrics report error: {str(e)}")
        emit('error', {'message': 'Failed to process metrics'})


@socketio.on('heartbeat', namespace='/client')
def handle_heartbeat(data):
    """Handle client heartbeat for connection monitoring"""
    client_id = data.get('client_id')
    
    if client_id:
        # Update last seen timestamp
        logger.debug(f"Heartbeat from client {client_id}")
        emit('heartbeat_ack', {
            'timestamp': datetime.utcnow().isoformat()
        })


# Import datetime for timestamps
from datetime import datetime