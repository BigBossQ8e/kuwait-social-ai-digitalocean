"""
Theme management routes for admin panel
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, ThemeSetting, ThemePreset, ThemeHistory
from models.theme import ThemeSetting, ThemePreset, ThemeHistory
from extensions import db
from utils.decorators import admin_required
import json

theme_bp = Blueprint('theme', __name__)


@theme_bp.route('/settings', methods=['GET'])
def get_theme_settings():
    """Get all theme settings (public endpoint for frontend)"""
    try:
        settings = ThemeSetting.get_all_settings()
        return jsonify({
            'success': True,
            'settings': settings
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@theme_bp.route('/settings/<key>', methods=['GET'])
def get_theme_setting(key):
    """Get a specific theme setting"""
    try:
        setting = ThemeSetting.query.filter_by(setting_key=key).first()
        if not setting:
            return jsonify({
                'success': False,
                'error': 'Setting not found'
            }), 404
        
        return jsonify({
            'success': True,
            'setting': setting.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@theme_bp.route('/settings', methods=['PUT'])
@jwt_required()
@admin_required
def update_theme_settings():
    """Update multiple theme settings (admin only)"""
    try:
        user_id = get_jwt_identity()
        settings = request.json.get('settings', {})
        
        for key, value in settings.items():
            ThemeSetting.update_setting(key, value, user_id)
        
        # Record change in history
        active_preset = ThemePreset.get_active()
        history = ThemeHistory(
            preset_id=active_preset.id if active_preset else None,
            settings_snapshot=settings,
            changed_by=user_id,
            change_reason="Manual settings update"
        )
        db.session.add(history)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@theme_bp.route('/presets', methods=['GET'])
@jwt_required()
@admin_required
def get_theme_presets():
    """Get all theme presets (admin only)"""
    try:
        presets = ThemePreset.query.order_by(ThemePreset.created_at.desc()).all()
        return jsonify({
            'success': True,
            'presets': [p.to_dict() for p in presets]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@theme_bp.route('/presets', methods=['POST'])
@jwt_required()
@admin_required
def create_theme_preset():
    """Create a new theme preset"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Preset name is required'
            }), 400
        
        # Create preset from current settings if not provided
        if not data.get('settings'):
            data['settings'] = ThemeSetting.get_all_settings()
        
        preset = ThemePreset(
            name=data['name'],
            description=data.get('description', ''),
            settings=data['settings'],
            screenshot_url=data.get('screenshot_url'),
            created_by=user_id,
            updated_by=user_id
        )
        
        db.session.add(preset)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'preset': preset.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@theme_bp.route('/presets/<int:preset_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_theme_preset(preset_id):
    """Update a theme preset"""
    try:
        user_id = get_jwt_identity()
        data = request.json
        
        preset = ThemePreset.query.get(preset_id)
        if not preset:
            return jsonify({
                'success': False,
                'error': 'Preset not found'
            }), 404
        
        # Don't allow editing default preset
        if preset.is_default:
            return jsonify({
                'success': False,
                'error': 'Cannot modify default preset'
            }), 403
        
        # Update fields
        if 'name' in data:
            preset.name = data['name']
        if 'description' in data:
            preset.description = data['description']
        if 'settings' in data:
            preset.settings = data['settings']
        if 'screenshot_url' in data:
            preset.screenshot_url = data['screenshot_url']
        
        preset.updated_by = user_id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'preset': preset.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@theme_bp.route('/presets/<int:preset_id>/activate', methods=['POST'])
@jwt_required()
@admin_required
def activate_theme_preset(preset_id):
    """Activate a theme preset"""
    try:
        user_id = get_jwt_identity()
        
        preset = ThemePreset.query.get(preset_id)
        if not preset:
            return jsonify({
                'success': False,
                'error': 'Preset not found'
            }), 404
        
        # Activate the preset
        preset.activate(user_id)
        
        return jsonify({
            'success': True,
            'message': f'Theme "{preset.name}" activated successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@theme_bp.route('/presets/<int:preset_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_theme_preset(preset_id):
    """Delete a theme preset"""
    try:
        preset = ThemePreset.query.get(preset_id)
        if not preset:
            return jsonify({
                'success': False,
                'error': 'Preset not found'
            }), 404
        
        # Don't allow deleting active or default preset
        if preset.is_active:
            return jsonify({
                'success': False,
                'error': 'Cannot delete active preset'
            }), 403
        
        if preset.is_default:
            return jsonify({
                'success': False,
                'error': 'Cannot delete default preset'
            }), 403
        
        db.session.delete(preset)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Preset deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@theme_bp.route('/history', methods=['GET'])
@jwt_required()
@admin_required
def get_theme_history():
    """Get theme change history"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        history = ThemeHistory.query\
            .order_by(ThemeHistory.created_at.desc())\
            .paginate(page=page, per_page=per_page)
        
        return jsonify({
            'success': True,
            'history': [h.to_dict() for h in history.items],
            'total': history.total,
            'pages': history.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@theme_bp.route('/preview', methods=['POST'])
@jwt_required()
@admin_required
def preview_theme_settings():
    """Preview theme settings without saving"""
    try:
        settings = request.json.get('settings', {})
        
        # Return preview data
        return jsonify({
            'success': True,
            'preview_url': f'/admin/theme-preview?settings={json.dumps(settings)}',
            'settings': settings
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500