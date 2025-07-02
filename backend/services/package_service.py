"""
Package Management Service
Handles service packages, pricing, and feature assignments
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal
import redis
import json
from flask import current_app
from sqlalchemy import func, and_
from sqlalchemy.orm import joinedload

from models import db, Package, PackageFeature, FeatureFlag, Client, AdminActivity, ConfigHistory
from extensions import redis_client

logger = logging.getLogger(__name__)


class PackageService:
    """Service for managing packages and their features"""
    
    def __init__(self):
        self.redis_prefix = "package:"
        self.cache_ttl = 300  # 5 minutes
    
    def get_all_packages(self, include_features: bool = False, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all packages with optional feature details"""
        cache_key = f"{self.redis_prefix}all:{include_features}:{active_only}"
        cached = self._get_from_cache(cache_key)
        
        if cached:
            return cached
        
        # Build query
        query = Package.query
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        if include_features:
            query = query.options(joinedload(Package.feature_mappings).joinedload(PackageFeature.feature))
        
        packages = query.all()
        result = [p.to_dict(include_features=include_features) for p in packages]
        
        # Add client counts
        for package_data in result:
            package_id = package_data['id']
            client_count = Client.query.filter_by(package_id=package_id).count()
            package_data['client_count'] = client_count
        
        # Cache the result
        self._set_cache(cache_key, result)
        
        return result
    
    def get_package(self, package_id: int) -> Optional[Package]:
        """Get a specific package"""
        return Package.query.options(
            joinedload(Package.feature_mappings).joinedload(PackageFeature.feature)
        ).get(package_id)
    
    def get_package_by_name(self, name: str) -> Optional[Package]:
        """Get a package by its name"""
        return Package.query.filter_by(name=name).first()
    
    def create_package(self, data: Dict[str, Any], admin_id: int = None) -> Package:
        """Create a new package"""
        # Validate required fields
        required_fields = ['name', 'display_name', 'price_kwd']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create package
        package = Package(
            name=data['name'],
            display_name=data['display_name'],
            description=data.get('description'),
            price_kwd=Decimal(str(data['price_kwd'])),
            billing_period=data.get('billing_period', 'monthly'),
            is_active=data.get('is_active', True),
            features=data.get('features', {}),
            limits=data.get('limits', {})
        )
        
        db.session.add(package)
        db.session.flush()  # Get the package ID
        
        # Add feature mappings if provided
        if 'feature_ids' in data:
            for feature_id in data['feature_ids']:
                feature_mapping = PackageFeature(
                    package_id=package.id,
                    feature_id=feature_id,
                    is_included=True
                )
                db.session.add(feature_mapping)
        
        # Log admin activity
        if admin_id:
            self._log_admin_activity(
                admin_id=admin_id,
                action='package_create',
                resource_type='package',
                resource_id=package.id,
                changes={
                    'package_name': package.name,
                    'price': float(package.price_kwd),
                    'features': data.get('feature_ids', [])
                }
            )
        
        db.session.commit()
        
        # Clear cache
        self._invalidate_cache()
        
        return package
    
    def update_package(self, package_id: int, updates: Dict[str, Any], admin_id: int = None) -> Package:
        """Update package details"""
        package = Package.query.get_or_404(package_id)
        old_values = {}
        
        # Track changes
        allowed_fields = ['display_name', 'description', 'price_kwd', 'billing_period', 'is_active', 'features', 'limits']
        for field, value in updates.items():
            if field in allowed_fields and hasattr(package, field):
                old_value = getattr(package, field)
                if field == 'price_kwd':
                    value = Decimal(str(value))
                if old_value != value:
                    old_values[field] = old_value
                    setattr(package, field, value)
        
        if old_values:
            # Log the change
            self._log_config_change(
                config_type='package',
                config_id=package_id,
                previous_value=old_values,
                new_value={k: v for k, v in updates.items() if k in old_values}
            )
            
            # Log admin activity
            if admin_id:
                self._log_admin_activity(
                    admin_id=admin_id,
                    action='package_update',
                    resource_type='package',
                    resource_id=package_id,
                    changes={
                        'package_name': package.name,
                        'updates': updates
                    }
                )
            
            db.session.commit()
            
            # Clear cache
            self._invalidate_cache()
        
        return package
    
    def assign_features_to_package(self, package_id: int, feature_ids: List[int], admin_id: int = None) -> Package:
        """Assign features to a package"""
        package = Package.query.get_or_404(package_id)
        
        # Get current feature IDs
        current_feature_ids = {pf.feature_id for pf in package.feature_mappings}
        new_feature_ids = set(feature_ids)
        
        # Remove features that are no longer assigned
        to_remove = current_feature_ids - new_feature_ids
        if to_remove:
            PackageFeature.query.filter(
                and_(
                    PackageFeature.package_id == package_id,
                    PackageFeature.feature_id.in_(to_remove)
                )
            ).delete(synchronize_session='fetch')
        
        # Add new features
        to_add = new_feature_ids - current_feature_ids
        for feature_id in to_add:
            feature_mapping = PackageFeature(
                package_id=package_id,
                feature_id=feature_id,
                is_included=True
            )
            db.session.add(feature_mapping)
        
        if to_remove or to_add:
            # Log the change
            self._log_config_change(
                config_type='package_features',
                config_id=package_id,
                previous_value={'feature_ids': list(current_feature_ids)},
                new_value={'feature_ids': feature_ids}
            )
            
            # Log admin activity
            if admin_id:
                self._log_admin_activity(
                    admin_id=admin_id,
                    action='package_features_update',
                    resource_type='package',
                    resource_id=package_id,
                    changes={
                        'package_name': package.name,
                        'added_features': list(to_add),
                        'removed_features': list(to_remove)
                    }
                )
            
            db.session.commit()
            
            # Clear cache
            self._invalidate_cache()
            
            # Clear client feature cache for affected clients
            self._invalidate_client_caches(package_id)
        
        return package
    
    def get_package_comparison(self) -> List[Dict[str, Any]]:
        """Get a comparison of all active packages"""
        packages = self.get_all_packages(include_features=True, active_only=True)
        
        # Get all features
        all_features = FeatureFlag.query.filter_by(is_enabled=True).all()
        
        # Build comparison matrix
        comparison = []
        for package in packages:
            package_features = {pf['feature_key'] for pf in package.get('included_features', [])}
            
            feature_matrix = {}
            for feature in all_features:
                feature_matrix[feature.feature_key] = {
                    'included': feature.feature_key in package_features,
                    'display_name': feature.display_name,
                    'category': feature.category
                }
            
            comparison.append({
                'package': package,
                'features': feature_matrix
            })
        
        return comparison
    
    def get_package_statistics(self, package_id: int) -> Dict[str, Any]:
        """Get detailed statistics for a package"""
        package = Package.query.get_or_404(package_id)
        
        # Get client statistics
        total_clients = Client.query.filter_by(package_id=package_id).count()
        active_clients = Client.query.filter_by(package_id=package_id, is_active=True).count()
        
        # Calculate revenue
        monthly_revenue = float(package.price_kwd) * active_clients if package.billing_period == 'monthly' else 0
        yearly_revenue = float(package.price_kwd) * active_clients if package.billing_period == 'yearly' else monthly_revenue * 12
        
        # Get feature usage
        feature_count = PackageFeature.query.filter_by(package_id=package_id, is_included=True).count()
        
        return {
            'package_id': package_id,
            'package_name': package.name,
            'total_clients': total_clients,
            'active_clients': active_clients,
            'inactive_clients': total_clients - active_clients,
            'monthly_revenue_kwd': monthly_revenue,
            'yearly_revenue_kwd': yearly_revenue,
            'feature_count': feature_count,
            'price_kwd': float(package.price_kwd),
            'billing_period': package.billing_period
        }
    
    def duplicate_package(self, package_id: int, new_name: str, admin_id: int = None) -> Package:
        """Create a copy of an existing package"""
        source_package = Package.query.get_or_404(package_id)
        
        # Create new package
        new_package = Package(
            name=new_name,
            display_name=f"{source_package.display_name} (Copy)",
            description=source_package.description,
            price_kwd=source_package.price_kwd,
            billing_period=source_package.billing_period,
            is_active=False,  # Start as inactive
            features=source_package.features,
            limits=source_package.limits
        )
        
        db.session.add(new_package)
        db.session.flush()
        
        # Copy feature mappings
        for mapping in source_package.feature_mappings:
            new_mapping = PackageFeature(
                package_id=new_package.id,
                feature_id=mapping.feature_id,
                is_included=mapping.is_included,
                custom_config=mapping.custom_config
            )
            db.session.add(new_mapping)
        
        # Log admin activity
        if admin_id:
            self._log_admin_activity(
                admin_id=admin_id,
                action='package_duplicate',
                resource_type='package',
                resource_id=new_package.id,
                changes={
                    'source_package': source_package.name,
                    'new_package': new_package.name
                }
            )
        
        db.session.commit()
        
        # Clear cache
        self._invalidate_cache()
        
        return new_package
    
    def _log_config_change(self, config_type: str, config_id: int, previous_value: Dict, new_value: Dict):
        """Log configuration change to history"""
        history = ConfigHistory(
            config_type=config_type,
            config_id=config_id,
            previous_value=previous_value,
            new_value=new_value
        )
        db.session.add(history)
    
    def _log_admin_activity(self, admin_id: int, action: str, resource_type: str, resource_id: int, changes: Dict):
        """Log admin activity"""
        from flask import request
        
        activity = AdminActivity(
            admin_id=admin_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            changes=changes,
            ip_address=request.remote_addr if request else None
        )
        db.session.add(activity)
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        if not redis_client:
            return None
        
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        
        return None
    
    def _set_cache(self, key: str, value: Any, ttl: int = None):
        """Set value in Redis cache"""
        if not redis_client:
            return
        
        try:
            redis_client.setex(
                key,
                ttl or self.cache_ttl,
                json.dumps(value, default=str)  # Handle Decimal serialization
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def _invalidate_cache(self):
        """Invalidate all package-related cache"""
        if not redis_client:
            return
        
        try:
            # Delete all package cache keys
            for key in redis_client.scan_iter(f"{self.redis_prefix}*"):
                redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
    
    def _invalidate_client_caches(self, package_id: int):
        """Invalidate feature caches for clients with this package"""
        if not redis_client:
            return
        
        try:
            # Get all clients with this package
            clients = Client.query.filter_by(package_id=package_id).all()
            
            # Delete their feature caches
            for client in clients:
                cache_key = f"feature:client:{client.id}"
                redis_client.delete(cache_key)
        except Exception as e:
            logger.error(f"Client cache invalidation error: {e}")


# Singleton instance
package_service = PackageService()