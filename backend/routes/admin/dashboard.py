"""
Admin Dashboard API Routes
Main dashboard endpoints for admin panel
"""
from flask import Blueprint, jsonify, request, g
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_

from models import db, Client, Post, SocialAccount, User, Analytics, AdminActivity
from services.platform_service import platform_service
from services.feature_flag_service import feature_flag_service
from services.package_service import package_service
from utils.decorators import admin_required, permission_required

admin_dashboard_bp = Blueprint('admin_dashboard', __name__)


@admin_dashboard_bp.route('/api/admin/dashboard/overview', methods=['GET'])
@admin_required
def get_dashboard_overview():
    """Get main dashboard overview statistics"""
    try:
        # Get date range
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Platform statistics
        platforms = platform_service.get_all_platforms(include_stats=True)
        enabled_platforms = [p for p in platforms if p['is_enabled']]
        
        # Client statistics
        total_clients = Client.query.count()
        active_clients = Client.query.filter_by(is_active=True).count()
        new_clients = Client.query.filter(Client.created_at >= start_date).count()
        
        # Post statistics
        total_posts = Post.query.count()
        posts_this_period = Post.query.filter(Post.created_at >= start_date).count()
        pending_posts = Post.query.filter_by(status='pending').count()
        
        # User statistics
        total_users = User.query.count()
        active_users = User.query.filter(User.last_login >= start_date).count()
        
        # Revenue statistics (simplified)
        active_subscriptions = Client.query.filter_by(
            is_active=True,
            subscription_status='active'
        ).count()
        
        # Feature flags
        features = feature_flag_service.get_all_features(include_disabled=False)
        active_features = len(features)
        
        # Recent activity
        recent_activities = AdminActivity.query.order_by(
            AdminActivity.created_at.desc()
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'overview': {
                'platforms': {
                    'total': len(platforms),
                    'enabled': len(enabled_platforms),
                    'stats': {p['platform']: p.get('active_clients', 0) for p in platforms}
                },
                'clients': {
                    'total': total_clients,
                    'active': active_clients,
                    'new': new_clients,
                    'growth_rate': (new_clients / total_clients * 100) if total_clients > 0 else 0
                },
                'posts': {
                    'total': total_posts,
                    'this_period': posts_this_period,
                    'pending': pending_posts,
                    'daily_average': posts_this_period / days if days > 0 else 0
                },
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'activity_rate': (active_users / total_users * 100) if total_users > 0 else 0
                },
                'revenue': {
                    'active_subscriptions': active_subscriptions,
                    'mrr_estimate': active_subscriptions * 50  # Placeholder calculation
                },
                'features': {
                    'active': active_features,
                    'total': len(feature_flag_service.get_all_features())
                },
                'recent_activities': [a.to_dict() for a in recent_activities]
            },
            'period': {
                'days': days,
                'start_date': start_date.isoformat(),
                'end_date': datetime.utcnow().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_dashboard_bp.route('/api/admin/dashboard/activity-feed', methods=['GET'])
@admin_required
def get_activity_feed():
    """Get detailed activity feed"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        filter_type = request.args.get('type')
        admin_id = request.args.get('admin_id')
        
        # Build query
        query = AdminActivity.query
        
        if filter_type:
            query = query.filter_by(resource_type=filter_type)
        
        if admin_id:
            query = query.filter_by(admin_id=admin_id)
        
        # Paginate
        activities = query.order_by(AdminActivity.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'activities': [a.to_dict() for a in activities.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': activities.total,
                'pages': activities.pages,
                'has_prev': activities.has_prev,
                'has_next': activities.has_next
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_dashboard_bp.route('/api/admin/dashboard/system-health', methods=['GET'])
@admin_required
@permission_required('settings')
def get_system_health():
    """Get system health and status"""
    try:
        from extensions import redis_client
        from services.telegram_bot_manager import bot_manager
        
        health = {
            'database': 'healthy',
            'redis': 'unavailable',
            'telegram_bots': {
                'active': len(bot_manager.bots),
                'status': 'healthy'
            },
            'disk_usage': _get_disk_usage(),
            'api_status': _check_api_status()
        }
        
        # Check Redis
        if redis_client:
            try:
                redis_client.ping()
                health['redis'] = 'healthy'
            except:
                pass
        
        # Check database
        try:
            db.session.execute('SELECT 1')
        except:
            health['database'] = 'unhealthy'
        
        return jsonify({
            'success': True,
            'health': health,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_dashboard_bp.route('/api/admin/dashboard/quick-actions', methods=['GET'])
@admin_required
def get_quick_actions():
    """Get available quick actions based on role"""
    try:
        admin = g.current_user.admin_profile
        
        # Base actions for all admins
        actions = [
            {
                'id': 'view_clients',
                'title': 'View Clients',
                'icon': '👥',
                'url': '/admin/clients',
                'permission': 'clients:read'
            },
            {
                'id': 'view_posts',
                'title': 'Content Queue',
                'icon': '📝',
                'url': '/admin/content',
                'permission': 'content:read'
            },
            {
                'id': 'analytics',
                'title': 'Analytics',
                'icon': '📊',
                'url': '/admin/analytics',
                'permission': 'analytics:read'
            }
        ]
        
        # Role-specific actions
        if admin.role in ['owner', 'admin']:
            actions.extend([
                {
                    'id': 'manage_platforms',
                    'title': 'Platform Settings',
                    'icon': '⚙️',
                    'url': '/admin/platforms',
                    'permission': 'settings:write'
                },
                {
                    'id': 'feature_flags',
                    'title': 'Feature Flags',
                    'icon': '🚀',
                    'url': '/admin/features',
                    'permission': 'settings:write'
                }
            ])
        
        if admin.role == 'owner':
            actions.extend([
                {
                    'id': 'manage_packages',
                    'title': 'Packages & Pricing',
                    'icon': '💰',
                    'url': '/admin/packages',
                    'permission': 'all'
                },
                {
                    'id': 'admin_users',
                    'title': 'Admin Users',
                    'icon': '🔐',
                    'url': '/admin/users',
                    'permission': 'all'
                }
            ])
        
        # Filter based on permissions
        permissions = g.token_payload.get('permissions', [])
        if 'all' not in permissions:
            actions = [a for a in actions if a['permission'] in permissions or 
                      any(p.startswith(a['permission'].split(':')[0]) for p in permissions)]
        
        return jsonify({
            'success': True,
            'actions': actions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_dashboard_bp.route('/api/admin/dashboard/metrics', methods=['GET'])
@admin_required
@permission_required('analytics')
def get_dashboard_metrics():
    """Get detailed metrics for charts and graphs"""
    try:
        days = int(request.args.get('days', 30))
        metric_type = request.args.get('type', 'all')
        
        metrics = {}
        
        if metric_type in ['all', 'posts']:
            metrics['posts'] = _get_post_metrics(days)
        
        if metric_type in ['all', 'clients']:
            metrics['clients'] = _get_client_metrics(days)
        
        if metric_type in ['all', 'engagement']:
            metrics['engagement'] = _get_engagement_metrics(days)
        
        if metric_type in ['all', 'revenue']:
            metrics['revenue'] = _get_revenue_metrics(days)
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'period': {
                'days': days,
                'start_date': (datetime.utcnow() - timedelta(days=days)).isoformat(),
                'end_date': datetime.utcnow().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Helper functions
def _get_disk_usage():
    """Get disk usage statistics"""
    import shutil
    
    try:
        stat = shutil.disk_usage('/')
        return {
            'total': stat.total,
            'used': stat.used,
            'free': stat.free,
            'percent': (stat.used / stat.total * 100)
        }
    except:
        return None


def _check_api_status():
    """Check external API status"""
    # Placeholder - would check actual API health
    return {
        'openai': 'healthy',
        'anthropic': 'healthy',
        'social_apis': 'healthy'
    }


def _get_post_metrics(days):
    """Get post-related metrics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily post counts
    daily_posts = db.session.query(
        func.date(Post.created_at).label('date'),
        func.count(Post.id).label('count')
    ).filter(
        Post.created_at >= start_date
    ).group_by(
        func.date(Post.created_at)
    ).all()
    
    # Platform distribution
    platform_dist = db.session.query(
        Post.platform,
        func.count(Post.id).label('count')
    ).filter(
        Post.created_at >= start_date
    ).group_by(Post.platform).all()
    
    return {
        'daily': [{'date': str(d.date), 'count': d.count} for d in daily_posts],
        'by_platform': {p.platform: p.count for p in platform_dist},
        'total': sum(d.count for d in daily_posts)
    }


def _get_client_metrics(days):
    """Get client-related metrics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily signups
    daily_signups = db.session.query(
        func.date(Client.created_at).label('date'),
        func.count(Client.id).label('count')
    ).filter(
        Client.created_at >= start_date
    ).group_by(
        func.date(Client.created_at)
    ).all()
    
    # Plan distribution
    plan_dist = db.session.query(
        Client.subscription_plan,
        func.count(Client.id).label('count')
    ).filter(
        Client.is_active == True
    ).group_by(Client.subscription_plan).all()
    
    return {
        'daily_signups': [{'date': str(d.date), 'count': d.count} for d in daily_signups],
        'by_plan': {p.subscription_plan: p.count for p in plan_dist},
        'total_new': sum(d.count for d in daily_signups)
    }


def _get_engagement_metrics(days):
    """Get engagement metrics"""
    # Placeholder - would calculate actual engagement
    return {
        'average_likes': 125,
        'average_comments': 23,
        'average_shares': 45,
        'engagement_rate': 3.2
    }


def _get_revenue_metrics(days):
    """Get revenue metrics"""
    # Placeholder - would calculate actual revenue
    active_clients = Client.query.filter_by(
        is_active=True,
        subscription_status='active'
    ).count()
    
    return {
        'mrr': active_clients * 50,
        'arr': active_clients * 50 * 12,
        'growth_rate': 15.2,
        'churn_rate': 2.1
    }