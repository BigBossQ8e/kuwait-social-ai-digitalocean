"""
Services package for Kuwait Social AI

This package exports service classes and factory functions.
Services are instantiated through the service container to prevent
circular imports and ensure proper initialization order.
"""

# Export service classes (not instances)
from .ai_service import AIService
from .cache_service import CacheService
from .content_generator import ContentGenerator
from .prayer_times_service import PrayerTimesService
from .image_processor import ImageProcessor
from .competitor_analysis_service import CompetitorAnalysisService
from .hashtag_strategy_service import HashtagStrategyService
from .admin_notification_service import AdminNotificationService

# Export factory functions from container
from .container import (
    get_service_container,
    get_ai_service,
    get_cache_service,
    get_content_generator,
    get_prayer_times_service,
    get_image_processor,
    get_competitor_analysis_service,
    get_hashtag_strategy_service,
    get_admin_notification_service
)

# Export convenience functions from prayer times service
# These will use the service container internally
def get_prayer_times(*args, **kwargs):
    """Get prayer times using the prayer times service"""
    return get_prayer_times_service().get_prayer_times(*args, **kwargs)

def is_prayer_time(*args, **kwargs):
    """Check if current time is during prayer time"""
    return get_prayer_times_service().is_prayer_time(*args, **kwargs)

def get_next_prayer(*args, **kwargs):
    """Get the next prayer time"""
    return get_prayer_times_service().get_next_prayer(*args, **kwargs)

# Export admin notification convenience functions
def get_notification_service():
    """Get admin notification service instance"""
    return get_admin_notification_service()

def send_critical_alert(*args, **kwargs):
    """Send critical alert using notification service"""
    return get_admin_notification_service().send_critical_alert(*args, **kwargs)

__all__ = [
    # Service classes
    'AIService',
    'CacheService',
    'ContentGenerator',
    'PrayerTimesService',
    'ImageProcessor',
    'CompetitorAnalysisService',
    'HashtagStrategyService',
    'AdminNotificationService',
    
    # Factory functions
    'get_service_container',
    'get_ai_service',
    'get_cache_service',
    'get_content_generator',
    'get_prayer_times_service',
    'get_image_processor',
    'get_competitor_analysis_service',
    'get_hashtag_strategy_service',
    'get_admin_notification_service',
    
    # Convenience functions
    'get_prayer_times',
    'is_prayer_time',
    'get_next_prayer',
    'get_notification_service',
    'send_critical_alert'
]