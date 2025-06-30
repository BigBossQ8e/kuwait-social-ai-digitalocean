"""
Security middleware for Kuwait Social AI
Adds security headers and protections
"""

from flask import current_app


def init_security_headers(app):
    """Initialize security headers middleware"""
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        
        # Only apply strict security in production
        if app.config.get('ENV') == 'production':
            # Prevent XSS attacks
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # Enable HSTS
            if app.config.get('HSTS_ENABLED', True):
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            
            # Content Security Policy
            if app.config.get('CSP_ENABLED', True):
                csp = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                    "font-src 'self' https://fonts.gstatic.com; "
                    "img-src 'self' data: https:; "
                    "connect-src 'self' https://api.openai.com https://api.myfatoorah.com"
                )
                response.headers['Content-Security-Policy'] = csp
            
            # Referrer Policy
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Permissions Policy
            response.headers['Permissions-Policy'] = (
                'accelerometer=(), camera=(), geolocation=(), gyroscope=(), '
                'magnetometer=(), microphone=(), payment=(), usb=()'
            )
        
        return response
    
    @app.before_request
    def security_checks():
        """Perform security checks before processing requests"""
        
        # Add any pre-request security checks here
        # For example: rate limiting, IP blocking, etc.
        pass
    
    return app