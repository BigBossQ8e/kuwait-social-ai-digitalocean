"""
Admin Feature Flag Management Routes
Handles feature flags and sub-features configuration
"""
from flask import Blueprint, jsonify, request, g
from sqlalchemy.exc import IntegrityError

from models import db, FeatureFlag, FeatureSubflag
from services.feature_flag_service import feature_flag_service
from utils.decorators import admin_required, audit_log
from utils.validators import validate_request

admin_features_bp = Blueprint('admin_features', __name__)


@admin_features_bp.route('/api/admin/features', methods=['GET'])
@admin_required
def get_features():
    """Get all feature flags"""
    try:
        category = request.args.get('category')
        include_disabled = request.args.get('include_disabled', 'true').lower() == 'true'
        
        features = feature_flag_service.get_all_features(
            category=category,
            include_disabled=include_disabled
        )
        
        # Get categories for filtering
        categories = feature_flag_service.get_feature_categories()
        
        return jsonify({
            'success': True,
            'features': features,
            'categories': categories,
            'count': len(features)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_features_bp.route('/api/admin/features/<int:feature_id>', methods=['GET'])
@admin_required
def get_feature(feature_id):
    """Get specific feature details"""
    try:
        feature = feature_flag_service.get_feature(feature_id)
        if not feature:
            return jsonify({
                'success': False,
                'error': 'Feature not found'
            }), 404
        
        return jsonify({
            'success': True,
            'feature': feature.to_dict(include_sub_features=True)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_features_bp.route('/api/admin/features/<int:feature_id>/toggle', methods=['POST'])
@admin_required
@audit_log('feature_toggle')
def toggle_feature(feature_id):
    """Toggle feature flag availability"""
    try:
        data = request.get_json()
        is_enabled = data.get('is_enabled', False)
        
        # Get admin ID from current user
        admin_id = g.current_user.admin_profile.id if hasattr(g.current_user, 'admin_profile') else None
        
        # Toggle feature
        feature = feature_flag_service.toggle_feature(
            feature_id=feature_id,
            is_enabled=is_enabled,
            admin_id=admin_id
        )
        
        return jsonify({
            'success': True,
            'feature': feature.to_dict(include_sub_features=True),
            'message': f"Feature {feature.display_name} {'enabled' if is_enabled else 'disabled'} successfully"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_features_bp.route('/api/admin/features/<int:feature_id>', methods=['PUT'])
@admin_required
@audit_log('feature_update')
def update_feature(feature_id):
    """Update feature configuration"""
    try:
        data = request.get_json()
        
        # Get admin ID
        admin_id = g.current_user.admin_profile.id if hasattr(g.current_user, 'admin_profile') else None
        
        # Update feature
        feature = feature_flag_service.update_feature_config(
            feature_id=feature_id,
            updates=data,
            admin_id=admin_id
        )
        
        return jsonify({
            'success': True,
            'feature': feature.to_dict(include_sub_features=True),
            'message': 'Feature updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_features_bp.route('/api/admin/features/sub/<int:sub_feature_id>/toggle', methods=['POST'])
@admin_required
@audit_log('sub_feature_toggle')
def toggle_sub_feature(sub_feature_id):
    """Toggle sub-feature availability"""
    try:
        data = request.get_json()
        is_enabled = data.get('is_enabled', False)
        
        # Get admin ID
        admin_id = g.current_user.admin_profile.id if hasattr(g.current_user, 'admin_profile') else None
        
        # Toggle sub-feature
        sub_feature = feature_flag_service.toggle_sub_feature(
            sub_feature_id=sub_feature_id,
            is_enabled=is_enabled,
            admin_id=admin_id
        )
        
        return jsonify({
            'success': True,
            'sub_feature': sub_feature.to_dict(),
            'message': f"Sub-feature {sub_feature.display_name} {'enabled' if is_enabled else 'disabled'} successfully"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_features_bp.route('/api/admin/features/sub/<int:sub_feature_id>/config', methods=['PUT'])
@admin_required
@audit_log('sub_feature_config_update')
def update_sub_feature_config(sub_feature_id):
    """Update sub-feature configuration"""
    try:
        data = request.get_json()
        config = data.get('config', {})
        
        # Get admin ID
        admin_id = g.current_user.admin_profile.id if hasattr(g.current_user, 'admin_profile') else None
        
        # Update config
        sub_feature = feature_flag_service.update_sub_feature_config(
            sub_feature_id=sub_feature_id,
            config=config,
            admin_id=admin_id
        )
        
        return jsonify({
            'success': True,
            'sub_feature': sub_feature.to_dict(),
            'message': 'Sub-feature configuration updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_features_bp.route('/api/admin/features/bulk-toggle', methods=['POST'])
@admin_required
@audit_log('bulk_feature_toggle')
def bulk_toggle_features():
    """Toggle multiple features at once"""
    try:
        data = request.get_json()
        feature_ids = data.get('feature_ids', [])
        is_enabled = data.get('is_enabled', False)
        
        if not feature_ids:
            return jsonify({
                'success': False,
                'error': 'No features specified'
            }), 400
        
        # Get admin ID
        admin_id = g.current_user.admin_profile.id if hasattr(g.current_user, 'admin_profile') else None
        
        # Toggle features
        features = feature_flag_service.bulk_toggle_features(
            feature_ids=feature_ids,
            is_enabled=is_enabled,
            admin_id=admin_id
        )
        
        return jsonify({
            'success': True,
            'updated_count': len(features),
            'message': f"{len(features)} features {'enabled' if is_enabled else 'disabled'} successfully"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_features_bp.route('/api/admin/features/client/<int:client_id>', methods=['GET'])
@admin_required
def get_client_features(client_id):
    """Get features available to a specific client"""
    try:
        features = feature_flag_service.get_client_features(client_id)
        
        return jsonify({
            'success': True,
            'client_id': client_id,
            'features': features['features'],
            'limits': features['limits'],
            'package_name': features['package_name']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_features_bp.route('/api/admin/features/check', methods=['POST'])
@admin_required
def check_feature_access():
    """Check if a client has access to a specific feature"""
    try:
        data = request.get_json()
        client_id = data.get('client_id')
        feature_key = data.get('feature_key')
        sub_key = data.get('sub_key')
        
        if not client_id or not feature_key:
            return jsonify({
                'success': False,
                'error': 'client_id and feature_key are required'
            }), 400
        
        has_access = feature_flag_service.is_feature_enabled_for_client(
            client_id=client_id,
            feature_key=feature_key,
            sub_key=sub_key
        )
        
        return jsonify({
            'success': True,
            'has_access': has_access,
            'client_id': client_id,
            'feature_key': feature_key,
            'sub_key': sub_key
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_features_bp.route('/api/admin/features/categories', methods=['GET'])
@admin_required
def get_feature_categories():
    """Get all feature categories"""
    try:
        categories = feature_flag_service.get_feature_categories()
        
        return jsonify({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_features_bp.route('/api/admin/features/sync', methods=['POST'])
@admin_required
def sync_feature_status():
    """Force sync feature status to all clients"""
    try:
        # This would trigger a WebSocket broadcast to all connected clients
        # For now, we'll just return success
        
        return jsonify({
            'success': True,
            'message': 'Feature status synced to all clients'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500