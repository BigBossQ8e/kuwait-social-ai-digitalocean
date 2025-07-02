# Dependency Injection Guide - Kuwait Social AI

## Overview
We've refactored the services architecture to use dependency injection pattern instead of module-level singleton instantiation. This prevents circular imports and ensures services are initialized in the proper order.

## Architecture Changes

### Old Pattern (Problematic)
```python
# In ai_service.py
class AIService:
    def __init__(self):
        # initialization code
        
# Singleton created at module level - causes circular imports!
ai_service = AIService()
```

### New Pattern (Recommended)
```python
# In ai_service.py
class AIService:
    def __init__(self):
        # initialization code
        
# No singleton - use service container instead
```

## Service Container Usage

### Getting Service Instances

```python
# Option 1: Import from services package
from services import get_ai_service

# Get service instance when needed
ai_service = get_ai_service()
result = ai_service.generate_content(...)

# Option 2: Use service container directly
from services.container import get_service_container

container = get_service_container()
ai_service = container.get_ai_service()
```

### Available Service Factory Functions

```python
from services import (
    get_ai_service,                  # AI content generation
    get_cache_service,               # Redis/memory caching
    get_content_generator,           # Legacy content generator
    get_prayer_times_service,        # Prayer times API
    get_image_processor,             # Image processing
    get_competitor_analysis_service, # Competitor analysis
    get_hashtag_strategy_service,    # Hashtag strategy
    get_admin_notification_service   # Admin notifications
)
```

## Migration Guide

### Updating Route Files

**Before:**
```python
from services.ai_service import ai_service

@app.route('/generate')
def generate():
    result = ai_service.generate_content(...)
```

**After:**
```python
from services import get_ai_service

@app.route('/generate')
def generate():
    ai_service = get_ai_service()
    result = ai_service.generate_content(...)
```

### Updating Scripts

**Before:**
```python
from services.ai_service import AIService
ai_service = AIService()
```

**After:**
```python
from services.container import get_ai_service
ai_service = get_ai_service()
```

## Benefits

1. **No Circular Imports**: Services are created on-demand, not at import time
2. **Proper Initialization Order**: Environment variables and configs load first
3. **Better Testing**: Easy to mock services for unit tests
4. **Memory Efficiency**: Services created only when needed
5. **Flask Context Handling**: Services can properly handle Flask app context

## Service Container API

The service container provides these methods:

```python
container = get_service_container()

# Get service instances (creates if not exists)
container.get_ai_service()
container.get_cache_service()
# ... etc

# Reset specific service
container.reset_service('ai_service')

# Reset all services
container.reset_all_services()
```

## Environment Variable Handling

Services that depend on environment variables now handle loading properly:

```python
class ContentGenerator:
    def __init__(self):
        # Load env vars if not already loaded
        from dotenv import load_dotenv
        load_dotenv()
        
        self.api_key = os.getenv('OPENAI_API_KEY')
```

## Flask App Context

Services that need Flask app context handle it gracefully:

```python
class CacheService:
    def __init__(self, redis_url: str = None):
        if redis_url:
            self.redis_url = redis_url
        else:
            try:
                from flask import current_app
                self.redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379')
            except (RuntimeError, ImportError):
                # Outside Flask context - use env var
                import os
                self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
```

## Testing

The new pattern makes testing easier:

```python
def test_ai_generation():
    # Get fresh service instance
    from services import get_service_container
    container = get_service_container()
    container.reset_service('ai_service')  # Ensure clean state
    
    ai_service = container.get_ai_service()
    # Run tests...
```

## Backward Compatibility

For convenience, the services package still exports helper functions that match the old API:

```python
# These work for prayer times service
from services import get_prayer_times, is_prayer_time, get_next_prayer

# These work for admin notifications  
from services import get_notification_service, send_critical_alert
```

## Next Steps

When adding new services:

1. Create the service class without singleton
2. Add getter method to ServiceContainer
3. Export the getter from services/__init__.py
4. Use the getter in routes/scripts

This pattern ensures clean, maintainable code without circular import issues.