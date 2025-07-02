"""
Admin Package Management Routes
Handles service packages, pricing, and feature assignments
"""
from flask import Blueprint, jsonify, request, g
from sqlalchemy.exc import IntegrityError
from decimal import Decimal, InvalidOperation

from models import db
from services.package_service import package_service
from utils.decorators import admin_required, audit_log, owner_required
from utils.validators import validate_request

admin_packages_bp = Blueprint('admin_packages', __name__)


@admin_packages_bp.route('/api/admin/packages', methods=['GET'])
@admin_required
def get_packages():
    """Get all packages"""
    try:
        include_features = request.args.get('include_features', 'false').lower() == 'true'
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        packages = package_service.get_all_packages(
            include_features=include_features,
            active_only=active_only
        )
        
        return jsonify({
            'success': True,
            'packages': packages,
            'count': len(packages)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_packages_bp.route('/api/admin/packages/<int:package_id>', methods=['GET'])
@admin_required
def get_package(package_id):
    """Get specific package details"""
    try:
        package = package_service.get_package(package_id)
        if not package:
            return jsonify({
                'success': False,
                'error': 'Package not found'
            }), 404
        
        package_data = package.to_dict(include_features=True)
        package_data['statistics'] = package_service.get_package_statistics(package_id)
        
        return jsonify({
            'success': True,
            'package': package_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_packages_bp.route('/api/admin/packages', methods=['POST'])
@owner_required  # Only owners can create packages
@audit_log('package_create')
def create_package():
    """Create a new package"""
    try:
        data = request.get_json()
        
        # Validate price
        try:
            price = Decimal(str(data.get('price_kwd', 0)))
            if price < 0:
                raise ValueError("Price cannot be negative")
        except (InvalidOperation, ValueError) as e:
            return jsonify({
                'success': False,
                'error': f"Invalid price: {str(e)}"
            }), 400
        
        # Get admin ID
        admin_id = g.current_user.admin_profile.id if hasattr(g.current_user, 'admin_profile') else None
        
        # Create package
        package = package_service.create_package(data, admin_id=admin_id)
        
        return jsonify({
            'success': True,
            'package': package.to_dict(include_features=True),
            'message': f"Package '{package.display_name}' created successfully"
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Package with this name already exists'
        }), 400
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_packages_bp.route('/api/admin/packages/<int:package_id>', methods=['PUT'])
@owner_required  # Only owners can update packages
@audit_log('package_update')
def update_package(package_id):
    """Update package details"""
    try:
        data = request.get_json()
        
        # Validate price if provided
        if 'price_kwd' in data:
            try:
                price = Decimal(str(data['price_kwd']))
                if price < 0:
                    raise ValueError("Price cannot be negative")
            except (InvalidOperation, ValueError) as e:
                return jsonify({
                    'success': False,
                    'error': f"Invalid price: {str(e)}"
                }), 400
        
        # Get admin ID
        admin_id = g.current_user.admin_profile.id if hasattr(g.current_user, 'admin_profile') else None
        
        # Update package
        package = package_service.update_package(
            package_id=package_id,
            updates=data,
            admin_id=admin_id
        )
        
        return jsonify({
            'success': True,
            'package': package.to_dict(include_features=True),
            'message': 'Package updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_packages_bp.route('/api/admin/packages/<int:package_id>/features', methods=['PUT'])
@owner_required  # Only owners can modify package features
@audit_log('package_features_update')
def update_package_features(package_id):
    """Update features assigned to a package"""
    try:
        data = request.get_json()
        feature_ids = data.get('feature_ids', [])
        
        if not isinstance(feature_ids, list):
            return jsonify({
                'success': False,
                'error': 'feature_ids must be a list'
            }), 400
        
        # Get admin ID
        admin_id = g.current_user.admin_profile.id if hasattr(g.current_user, 'admin_profile') else None
        
        # Update features
        package = package_service.assign_features_to_package(
            package_id=package_id,
            feature_ids=feature_ids,
            admin_id=admin_id
        )
        
        return jsonify({
            'success': True,
            'package': package.to_dict(include_features=True),
            'message': 'Package features updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_packages_bp.route('/api/admin/packages/comparison', methods=['GET'])
@admin_required
def get_package_comparison():
    """Get comparison of all active packages"""
    try:
        comparison = package_service.get_package_comparison()
        
        return jsonify({
            'success': True,
            'comparison': comparison
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_packages_bp.route('/api/admin/packages/<int:package_id>/statistics', methods=['GET'])
@admin_required
def get_package_statistics(package_id):
    """Get detailed statistics for a package"""
    try:
        stats = package_service.get_package_statistics(package_id)
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_packages_bp.route('/api/admin/packages/<int:package_id>/duplicate', methods=['POST'])
@owner_required  # Only owners can duplicate packages
@audit_log('package_duplicate')
def duplicate_package(package_id):
    """Create a copy of an existing package"""
    try:
        data = request.get_json()
        new_name = data.get('new_name')
        
        if not new_name:
            return jsonify({
                'success': False,
                'error': 'new_name is required'
            }), 400
        
        # Get admin ID
        admin_id = g.current_user.admin_profile.id if hasattr(g.current_user, 'admin_profile') else None
        
        # Duplicate package
        new_package = package_service.duplicate_package(
            package_id=package_id,
            new_name=new_name,
            admin_id=admin_id
        )
        
        return jsonify({
            'success': True,
            'package': new_package.to_dict(include_features=True),
            'message': f"Package duplicated successfully as '{new_package.display_name}'"
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Package with this name already exists'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_packages_bp.route('/api/admin/packages/<int:package_id>/toggle', methods=['POST'])
@owner_required  # Only owners can activate/deactivate packages
@audit_log('package_toggle')
def toggle_package_status(package_id):
    """Toggle package active status"""
    try:
        data = request.get_json()
        is_active = data.get('is_active', False)
        
        # Get admin ID
        admin_id = g.current_user.admin_profile.id if hasattr(g.current_user, 'admin_profile') else None
        
        # Update package status
        package = package_service.update_package(
            package_id=package_id,
            updates={'is_active': is_active},
            admin_id=admin_id
        )
        
        return jsonify({
            'success': True,
            'package': package.to_dict(),
            'message': f"Package {'activated' if is_active else 'deactivated'} successfully"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500