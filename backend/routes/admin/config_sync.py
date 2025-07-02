"""
Admin Configuration Sync Routes
Handles real-time configuration synchronization management
"""
from flask import Blueprint, jsonify, request, g
from datetime import datetime

from models import db
from services.config_sync_service import config_sync_service
from utils.decorators import admin_required, audit_log

admin_config_sync_bp = Blueprint('admin_config_sync', __name__)


@admin_config_sync_bp.route('/api/admin/config-sync/status/<int:client_id>', methods=['GET'])
@admin_required
def get_sync_status(client_id):
    """Get configuration sync status for a client"""
    try:
        status = config_sync_service.get_sync_status(client_id)
        
        return jsonify({
            'success': True,
            'client_id': client_id,
            'sync_status': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_config_sync_bp.route('/api/admin/config-sync/sync/<int:client_id>', methods=['POST'])
@admin_required
@audit_log('config_sync_client')
def sync_client_config(client_id):
    """Force configuration sync for a specific client"""
    try:
        data = request.get_json() or {}
        force = data.get('force', True)
        
        # Get admin ID
        admin_id = g.current_user.admin_profile.id if hasattr(g.current_user, 'admin_profile') else None
        
        # Perform sync
        result = config_sync_service.sync_client_config(client_id, force=force)
        
        if result.get('error'):
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        return jsonify({
            'success': True,
            'result': result,
            'message': f"Configuration synced for client {client_id}"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_config_sync_bp.route('/api/admin/config-sync/sync-all', methods=['POST'])
@admin_required
@audit_log('config_sync_bulk')
def sync_all_clients():
    """Sync configuration for multiple clients"""
    try:
        data = request.get_json() or {}
        platform = data.get('platform')
        package_id = data.get('package_id')
        
        # Perform bulk sync
        result = config_sync_service.sync_all_clients(
            platform=platform,
            package_id=package_id
        )
        
        if result.get('error'):
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        return jsonify({
            'success': True,
            'result': result,
            'message': f"Synced {result.get('synced', 0)} clients"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_config_sync_bp.route('/api/admin/config-sync/mark-pending', methods=['POST'])
@admin_required
@audit_log('config_sync_mark_pending')
def mark_pending_sync():
    """Mark clients for pending configuration sync"""
    try:
        data = request.get_json()
        client_ids = data.get('client_ids', [])
        reason = data.get('reason', 'manual')
        
        if not client_ids:
            return jsonify({
                'success': False,
                'error': 'No client IDs provided'
            }), 400
        
        # Mark for sync
        config_sync_service.mark_pending_sync(client_ids, reason)
        
        return jsonify({
            'success': True,
            'marked_count': len(client_ids),
            'message': f"Marked {len(client_ids)} clients for sync"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_config_sync_bp.route('/api/admin/config-sync/process-pending', methods=['POST'])
@admin_required
@audit_log('config_sync_process_pending')
def process_pending_syncs():
    """Process all pending configuration syncs"""
    try:
        result = config_sync_service.process_pending_syncs()
        
        return jsonify({
            'success': True,
            'result': result,
            'message': f"Processed {result.get('processed', 0)} pending syncs"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_config_sync_bp.route('/api/admin/config-sync/history/<int:client_id>', methods=['GET'])
@admin_required
def get_sync_history(client_id):
    """Get configuration sync history for a client"""
    try:
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        from models import ConfigSync
        
        # Get sync history
        syncs = ConfigSync.query\
            .filter_by(client_id=client_id)\
            .order_by(ConfigSync.synced_at.desc())\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        # Get total count
        total = ConfigSync.query.filter_by(client_id=client_id).count()
        
        return jsonify({
            'success': True,
            'client_id': client_id,
            'history': [sync.to_dict() for sync in syncs],
            'total': total,
            'has_more': offset + limit < total
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_config_sync_bp.route('/api/admin/config-sync/cleanup', methods=['POST'])
@admin_required
@audit_log('config_sync_cleanup')
def cleanup_old_syncs():
    """Clean up old sync records"""
    try:
        data = request.get_json() or {}
        days = data.get('days', 7)
        
        if days < 1:
            return jsonify({
                'success': False,
                'error': 'Days must be at least 1'
            }), 400
        
        # Perform cleanup
        deleted = config_sync_service.cleanup_old_syncs(days)
        
        return jsonify({
            'success': True,
            'deleted': deleted,
            'message': f"Cleaned up {deleted} sync records older than {days} days"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_config_sync_bp.route('/api/admin/config-sync/stats', methods=['GET'])
@admin_required
def get_sync_statistics():
    """Get configuration sync statistics"""
    try:
        from models import ConfigSync, Client
        from sqlalchemy import func
        
        # Get statistics
        total_clients = Client.query.filter_by(is_active=True).count()
        
        # Synced in last 24 hours
        recent_syncs = ConfigSync.query.filter(
            ConfigSync.synced_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # Failed syncs
        failed_syncs = ConfigSync.query.filter_by(sync_status='failed').count()
        
        # Average sync time (if we tracked duration)
        sync_stats = db.session.query(
            func.count(ConfigSync.id).label('total_syncs'),
            func.avg(func.extract('epoch', ConfigSync.synced_at)).label('avg_interval')
        ).first()
        
        # Pending syncs
        pending_count = len(config_sync_service.pending_syncs)
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_clients': total_clients,
                'recent_syncs_24h': recent_syncs,
                'failed_syncs': failed_syncs,
                'total_syncs': sync_stats.total_syncs if sync_stats else 0,
                'pending_syncs': pending_count,
                'sync_health': 'healthy' if failed_syncs < 10 else 'degraded'
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Import timedelta for time calculations
from datetime import timedelta