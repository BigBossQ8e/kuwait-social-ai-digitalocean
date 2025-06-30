# Application Factory Pattern Implementation

## Overview

The Kuwait Social AI backend has been refactored to use the Flask application factory pattern. This provides better flexibility, testability, and configuration management.

## Benefits

1. **Better Testing**: Easy to create app instances with different configurations for testing
2. **Multiple Configurations**: Support for development, testing, and production environments
3. **Cleaner Code Organization**: Separation of concerns between configuration, initialization, and runtime
4. **Easier Extension Management**: Extensions are initialized properly with `init_app`
5. **Blueprint Registration**: Centralized blueprint registration

## Structure

### 1. **app_factory.py**
The main factory module containing:
- `create_app()`: Main factory function
- `configure_app()`: Configuration loader
- `initialize_extensions()`: Extension initialization
- `register_blueprints()`: Blueprint registration
- `register_error_handlers()`: Error handler setup
- `configure_celery()`: Celery configuration

### 2. **config/config.py**
Configuration classes:
- `Config`: Base configuration
- `DevelopmentConfig`: Development settings
- `ProductionConfig`: Production settings
- `TestingConfig`: Testing settings

### 3. **wsgi.py**
WSGI entry point for production deployment

### 4. **app_refactored.py**
Development entry point with health check

## Usage

### Development
```bash
# Using the refactored app
python app_refactored.py

# Or set environment and run
export FLASK_ENV=development
flask run
```

### Production
```bash
# Using gunicorn
gunicorn wsgi:application

# Or with specific settings
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:application
```

### Testing
```python
# In test files
from app_factory import create_app, db

def test_something():
    app = create_app('testing')
    with app.app_context():
        # Run tests
        pass
```

## Extension Initialization

All extensions now use the `init_app` pattern:

```python
# OLD (direct initialization)
db = SQLAlchemy(app)
limiter = Limiter(app=app, ...)

# NEW (factory pattern)
db = SQLAlchemy()
limiter = Limiter(...)

# Later in factory
db.init_app(app)
limiter.init_app(app)
```

## Configuration Management

### Environment Variables
Configuration values can be overridden by environment variables:

```bash
# Override database URL
export SQLALCHEMY_DATABASE_URI=postgresql://prod-server/db

# Override JWT secret
export JWT_SECRET_KEY=your-production-secret
```

### Configuration Precedence
1. Environment variables (highest priority)
2. Configuration class settings
3. Default values (lowest priority)

## Error Handling

Centralized error handlers are registered in the factory:
- Custom exception handler for `KuwaitSocialAIException`
- 404 handler for not found errors
- 500 handler for internal errors
- 429 handler for rate limit errors

## Celery Integration

The factory configures Celery with Flask app context:
```python
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)
```

## Migration from Old Structure

To migrate existing code:

1. **Import changes**:
   ```python
   # Old
   from app import app, db
   
   # New
   from app_factory import create_app, db
   app = create_app()
   ```

2. **Testing**:
   ```python
   # Old
   app.config['TESTING'] = True
   
   # New
   app = create_app('testing')
   ```

3. **CLI Commands**:
   ```python
   # Create custom CLI commands in factory
   @app.cli.command()
   def init_db():
       db.create_all()
   ```

## Best Practices

1. **Don't import app directly**: Always use the factory
2. **Use app context**: When accessing app or extensions outside request context
3. **Configuration**: Keep sensitive data in environment variables
4. **Testing**: Create new app instances for each test
5. **Blueprints**: Register all blueprints in the factory

## Deployment Considerations

1. **Environment**: Set `FLASK_ENV=production` in production
2. **Secrets**: Never commit secrets to version control
3. **Database**: Run migrations before starting the app
4. **Static Files**: Serve through nginx in production
5. **Logging**: Configure appropriate log levels and handlers