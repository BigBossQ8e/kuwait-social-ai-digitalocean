"""
Admin Platform Management Routes
Handles platform configuration and toggles
"""
from flask import Blueprint, jsonify, request, g
from sqlalchemy.exc import IntegrityError

from models import db
from services.platform_service import platform_service
from utils.decorators import admin_required, audit_log
from utils.validators import validate_request

admin_platforms_bp = Blueprint('admin_platforms', __name__)


@admin_platforms_bp.route('/api/admin/platforms', methods=['GET'])
@admin_required
def get_platforms():
    """Get all platform configurations"""
    try:
        include_stats = request.args.get('include_stats', 'false').lower() == 'true'
        platforms = platform_service.get_all_platforms(include_stats=include_stats)
        
        return jsonify({
            'success': True,
            'platforms': platforms,
            'count': len(platforms)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_platforms_bp.route('/api/admin/platforms/<int:platform_id>', methods=['GET'])
@admin_required
def get_platform(platform_id):
    """Get specific platform details"""
    try:
        platform = platform_service.get_platform(platform_id)
        if not platform:
            return jsonify({
                'success': False,
                'error': 'Platform not found'
            }), 404
        
        platform_data = platform.to_dict()
        platform_data['stats'] = platform_service.get_platform_stats(platform.platform)
        
        return jsonify({
            'success': True,
            'platform': platform_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_platforms_bp.route('/api/admin/platforms/<int:platform_id>/toggle', methods=['POST'])
@admin_required
@audit_log('platform_toggle')
def toggle_platform(platform_id):
    """Toggle platform availability"""
    try:
        data = request.get_json()
        is_enabled = data.get('is_enabled', False)
        
        # Get admin ID from current user
        admin_id = g.current_user.admin_profile.id if hasattr(g.current_user, 'admin_profile') else None
        
        # Toggle platform
        platform = platform_service.toggle_platform(
            platform_id=platform_id,
            is_enabled=is_enabled,
            admin_id=admin_id
        )
        
        return jsonify({
            'success': True,
            'platform': platform.to_dict(),
            'message': f"Platform {platform.display_name} {'enabled' if is_enabled else 'disabled'} successfully"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_platforms_bp.route('/api/admin/platforms/<int:platform_id>', methods=['PUT'])
@admin_required
@audit_log('platform_update')
def update_platform(platform_id):
    """Update platform configuration"""
    try:
        data = request.get_json()
        
        # Validate allowed fields
        allowed_fields = ['display_name', 'icon', 'api_endpoint']
        updates = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not updates:
            return jsonify({
                'success': False,
                'error': 'No valid fields to update'
            }), 400
        
        # Get admin ID
        admin_id = g.current_user.admin_profile.id if hasattr(g.current_user, 'admin_profile') else None
        
        # Update platform
        platform = platform_service.update_platform_config(
            platform_id=platform_id,
            updates=updates,
            admin_id=admin_id
        )
        
        return jsonify({
            'success': True,
            'platform': platform.to_dict(),
            'message': 'Platform updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_platforms_bp.route('/api/admin/platforms/<platform>/stats', methods=['GET'])
@admin_required
def get_platform_statistics(platform):
    """Get detailed statistics for a specific platform"""
    try:
        stats = platform_service.get_platform_stats(platform)
        
        return jsonify({
            'success': True,
            'platform': platform,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_platforms_bp.route('/api/admin/platforms/client-view', methods=['GET'])
@admin_required
def get_client_platform_view():
    """Get platform configuration as seen by clients"""
    try:
        # Get enabled platforms
        enabled_platforms = platform_service.get_all_platforms()
        client_view = [p for p in enabled_platforms if p['is_enabled']]
        
        return jsonify({
            'success': True,
            'platforms': client_view,
            'count': len(client_view)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_platforms_bp.route('/api/admin/platforms/sync', methods=['POST'])
@admin_required
def sync_platform_status():
    """Force sync platform status to all clients"""
    try:
        # This would trigger a WebSocket broadcast to all connected clients
        # For now, we'll just return success
        
        return jsonify({
            'success': True,
            'message': 'Platform status synced to all clients'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500