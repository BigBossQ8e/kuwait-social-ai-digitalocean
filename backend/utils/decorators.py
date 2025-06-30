"""
Custom decorators for Kuwait Social AI
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from models import db, User, Client, Admin, Owner

def role_required(*allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({
                    'error': 'Access denied',
                    'message': f'This endpoint requires one of these roles: {", ".join(allowed_roles)}'
                }), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def owner_required(f):
    """Decorator to ensure user is platform owner"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        
        if claims.get('role') != 'owner':
            return jsonify({'error': 'Owner access required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to ensure user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        
        if claims.get('role') not in ['admin', 'owner']:
            return jsonify({'error': 'Admin access required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def client_required(f):
    """Decorator to ensure user is client"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        
        if claims.get('role') != 'client':
            return jsonify({'error': 'Client access required'}), 403
            
        # Verify client is active
        client_id = claims.get('client_id')
        if client_id:
            client = Client.query.get(client_id)
            if not client or client.subscription_status != 'active':
                return jsonify({'error': 'Active subscription required'}), 403
                
        return f(*args, **kwargs)
    return decorated_function

def feature_required(feature_name):
    """Decorator to check if client has specific feature enabled"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            
            if claims.get('role') != 'client':
                return jsonify({'error': 'This feature is for clients only'}), 403
            
            client_id = claims.get('client_id')
            if not client_id:
                return jsonify({'error': 'Client ID not found'}), 403
            
            # Check if client has feature
            client = Client.query.get(client_id)
            if not client:
                return jsonify({'error': 'Client not found'}), 404
            
            has_feature = any(
                f.name == feature_name and f.platform_enabled 
                for f in client.features
            )
            
            if not has_feature:
                return jsonify({
                    'error': 'Feature not available',
                    'message': f'The {feature_name} feature is not enabled for your account. Please contact support to upgrade.',
                    'feature': feature_name
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def subscription_required(min_plan='basic'):
    """Decorator to check if client has minimum subscription plan"""
    plan_hierarchy = {
        'trial': 0,
        'basic': 1,
        'professional': 2,
        'enterprise': 3
    }
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            
            if claims.get('role') != 'client':
                return f(*args, **kwargs)  # Non-clients bypass subscription check
            
            client_id = claims.get('client_id')
            if not client_id:
                return jsonify({'error': 'Client ID not found'}), 403
            
            client = Client.query.get(client_id)
            if not client:
                return jsonify({'error': 'Client not found'}), 404
            
            client_plan_level = plan_hierarchy.get(client.subscription_plan, 0)
            required_plan_level = plan_hierarchy.get(min_plan, 1)
            
            if client_plan_level < required_plan_level:
                return jsonify({
                    'error': 'Subscription upgrade required',
                    'message': f'This feature requires at least {min_plan} plan. You currently have {client.subscription_plan} plan.',
                    'current_plan': client.subscription_plan,
                    'required_plan': min_plan,
                    'upgrade_url': '/pricing'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def audit_log(action, resource_type=None):
    """Decorator to automatically log actions to audit trail"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            from models import AuditLog
            
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # Execute the function
            result = f(*args, **kwargs)
            
            # Log the action if successful (2xx status codes)
            if hasattr(result, 'status_code') and 200 <= result.status_code < 300:
                try:
                    audit = AuditLog(
                        user_id=int(user_id),
                        action=action,
                        resource_type=resource_type,
                        resource_id=kwargs.get('id') or kwargs.get('post_id') or kwargs.get('client_id'),
                        details={
                            'method': request.method,
                            'endpoint': request.endpoint,
                            'args': kwargs
                        },
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent')
                    )
                    db.session.add(audit)
                    db.session.commit()
                except Exception as e:
                    # Don't fail the request if audit logging fails
                    print(f"Audit logging failed: {e}")
            
            return result
        return decorated_function
    return decorator

def validate_ownership(resource_type):
    """Decorator to validate user owns the resource they're accessing"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_id = int(get_jwt_identity())
            
            # Get resource ID from kwargs
            resource_id = kwargs.get('id') or kwargs.get(f'{resource_type}_id')
            if not resource_id:
                return jsonify({'error': 'Resource ID not provided'}), 400
            
            # Check ownership based on resource type
            if resource_type == 'post':
                from models import Post
                resource = Post.query.get(resource_id)
                if not resource:
                    return jsonify({'error': 'Post not found'}), 404
                    
                # Check if user owns the post
                if claims.get('role') == 'client' and resource.client_id != claims.get('client_id'):
                    return jsonify({'error': 'You do not have access to this post'}), 403
                    
            elif resource_type == 'social_account':
                from models import SocialAccount
                resource = SocialAccount.query.get(resource_id)
                if not resource:
                    return jsonify({'error': 'Social account not found'}), 404
                    
                # Check if user owns the social account
                if claims.get('role') == 'client' and resource.client_id != claims.get('client_id'):
                    return jsonify({'error': 'You do not have access to this social account'}), 403
            
            # Add more resource types as needed
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def cache_response(timeout=300, key_prefix='api'):
    """
    Decorator to cache responses using Redis
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for cache keys (default: 'api')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, current_app, jsonify
            import json
            import hashlib
            import redis
            from redis.exceptions import RedisError
            
            # Check if caching is enabled
            if not current_app.config.get('CACHE_ENABLED', True):
                return f(*args, **kwargs)
            
            # Skip caching for authenticated requests or non-GET methods
            if request.method != 'GET' or request.headers.get('Authorization'):
                return f(*args, **kwargs)
            
            # Try to get Redis instance
            try:
                redis_client = current_app.extensions.get('redis')
                if not redis_client:
                    # Initialize Redis if not already done
                    redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
                    redis_client = redis.from_url(redis_url, decode_responses=True)
                    current_app.extensions['redis'] = redis_client
            except Exception as e:
                current_app.logger.warning(f"Redis initialization failed: {str(e)}")
                # If Redis is not available, execute function without caching
                return f(*args, **kwargs)
            
            # Generate cache key based on endpoint, method, and parameters
            cache_data = {
                'endpoint': request.endpoint,
                'method': request.method,
                'args': dict(request.args),
                'view_args': kwargs
            }
            cache_string = json.dumps(cache_data, sort_keys=True)
            cache_hash = hashlib.md5(cache_string.encode()).hexdigest()
            cache_key = f"{key_prefix}:{request.endpoint}:{cache_hash}"
            
            # Try to get from cache
            try:
                cached_response = redis_client.get(cache_key)
                if cached_response:
                    current_app.logger.debug(f"Cache hit for key: {cache_key}")
                    # Deserialize the cached response
                    cached_data = json.loads(cached_response)
                    return jsonify(cached_data['data']), cached_data['status_code']
            except RedisError as e:
                current_app.logger.error(f"Redis get error: {str(e)}")
            except json.JSONDecodeError as e:
                current_app.logger.error(f"Invalid cached data: {str(e)}")
                # Invalid cache entry, delete it
                try:
                    redis_client.delete(cache_key)
                except:
                    pass
            
            # Execute the function
            result = f(*args, **kwargs)
            
            # Cache the response if it's successful
            if hasattr(result, 'status_code') and 200 <= result[1] if isinstance(result, tuple) else result.status_code < 300:
                try:
                    # Handle different response formats
                    if isinstance(result, tuple):
                        response_data, status_code = result[0], result[1]
                    else:
                        response_data = result.get_json()
                        status_code = result.status_code
                    
                    # Serialize and cache the response
                    cache_data = {
                        'data': response_data,
                        'status_code': status_code
                    }
                    redis_client.setex(
                        cache_key,
                        timeout,
                        json.dumps(cache_data)
                    )
                    current_app.logger.debug(f"Cached response for key: {cache_key} (timeout: {timeout}s)")
                except RedisError as e:
                    current_app.logger.error(f"Redis set error: {str(e)}")
                except Exception as e:
                    current_app.logger.error(f"Cache storage error: {str(e)}")
            
            return result
        return decorated_function
    return decorator

def clear_cache(pattern=None):
    """
    Utility function to clear cache entries
    
    Args:
        pattern: Redis key pattern to match (e.g., 'api:*')
    """
    from flask import current_app
    import redis
    
    try:
        redis_client = current_app.extensions.get('redis')
        if not redis_client:
            redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
            redis_client = redis.from_url(redis_url, decode_responses=True)
        
        if pattern:
            # Delete keys matching pattern
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
                current_app.logger.info(f"Cleared {len(keys)} cache entries matching pattern: {pattern}")
        else:
            # Clear all cache
            redis_client.flushdb()
            current_app.logger.info("Cleared all cache entries")
            
        return True
    except Exception as e:
        current_app.logger.error(f"Clear cache error: {str(e)}")
        return False