"""
Service Container for Dependency Injection
Kuwait Social AI - Service Factory Pattern

Uses lazy initialization with module-level globals for simplicity.
Services are created only when first requested within proper app context.
"""

import logging
from typing import Optional
from dotenv import load_dotenv

# Import service classes (not instances)
from .ai_service import AIService
from .cache_service import CacheService
from .content_generator import ContentGenerator
from .competitor_analysis_service import CompetitorAnalysisService
from .hashtag_strategy_service import HashtagStrategyService
from .prayer_times_service import PrayerTimesService
from .image_processor import ImageProcessor
from .admin_notification_service import AdminNotificationService

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger(__name__)

# Module-level service instances (lazy initialization)
_ai_service: Optional[AIService] = None
_cache_service: Optional[CacheService] = None
_content_generator: Optional[ContentGenerator] = None
_competitor_analysis_service: Optional[CompetitorAnalysisService] = None
_hashtag_strategy_service: Optional[HashtagStrategyService] = None
_prayer_times_service: Optional[PrayerTimesService] = None
_image_processor: Optional[ImageProcessor] = None
_admin_notification_service: Optional[AdminNotificationService] = None


def get_cache_service() -> CacheService:
    """Get or create cache service instance"""
    global _cache_service
    if _cache_service is None:
        logger.debug("Creating new CacheService instance")
        _cache_service = CacheService()
    return _cache_service


def get_ai_service() -> AIService:
    """Get or create AI service instance with dependencies"""
    global _ai_service
    if _ai_service is None:
        logger.debug("Creating new AIService instance")
        # AI service might need cache service
        # Pass dependencies explicitly if needed
        _ai_service = AIService()
    return _ai_service


def get_content_generator() -> ContentGenerator:
    """Get or create content generator instance"""
    global _content_generator
    if _content_generator is None:
        logger.debug("Creating new ContentGenerator instance")
        _content_generator = ContentGenerator()
    return _content_generator


def get_competitor_analysis_service() -> CompetitorAnalysisService:
    """Get or create competitor analysis service instance"""
    global _competitor_analysis_service
    if _competitor_analysis_service is None:
        logger.debug("Creating new CompetitorAnalysisService instance")
        # This service might need cache service
        cache_service = get_cache_service()
        _competitor_analysis_service = CompetitorAnalysisService()
    return _competitor_analysis_service


def get_hashtag_strategy_service() -> HashtagStrategyService:
    """Get or create hashtag strategy service instance"""
    global _hashtag_strategy_service
    if _hashtag_strategy_service is None:
        logger.debug("Creating new HashtagStrategyService instance")
        # This service might need cache service
        cache_service = get_cache_service()
        _hashtag_strategy_service = HashtagStrategyService()
    return _hashtag_strategy_service


def get_prayer_times_service() -> PrayerTimesService:
    """Get or create prayer times service instance"""
    global _prayer_times_service
    if _prayer_times_service is None:
        logger.debug("Creating new PrayerTimesService instance")
        # This service uses cache service
        cache_service = get_cache_service()
        _prayer_times_service = PrayerTimesService()
    return _prayer_times_service


def get_image_processor() -> ImageProcessor:
    """Get or create image processor instance"""
    global _image_processor
    if _image_processor is None:
        logger.debug("Creating new ImageProcessor instance")
        _image_processor = ImageProcessor()
    return _image_processor


def get_admin_notification_service() -> AdminNotificationService:
    """Get or create admin notification service instance"""
    global _admin_notification_service
    if _admin_notification_service is None:
        logger.debug("Creating new AdminNotificationService instance")
        _admin_notification_service = AdminNotificationService()
    return _admin_notification_service


def reset_service(service_name: str) -> None:
    """Reset a specific service instance"""
    global _ai_service, _cache_service, _content_generator
    global _competitor_analysis_service, _hashtag_strategy_service
    global _prayer_times_service, _image_processor, _admin_notification_service
    
    service_map = {
        'ai_service': lambda: globals().update({'_ai_service': None}),
        'cache_service': lambda: globals().update({'_cache_service': None}),
        'content_generator': lambda: globals().update({'_content_generator': None}),
        'competitor_analysis_service': lambda: globals().update({'_competitor_analysis_service': None}),
        'hashtag_strategy_service': lambda: globals().update({'_hashtag_strategy_service': None}),
        'prayer_times_service': lambda: globals().update({'_prayer_times_service': None}),
        'image_processor': lambda: globals().update({'_image_processor': None}),
        'admin_notification_service': lambda: globals().update({'_admin_notification_service': None}),
    }
    
    if service_name in service_map:
        service_map[service_name]()
        logger.info(f"Reset service: {service_name}")


def reset_all_services() -> None:
    """Reset all service instances"""
    global _ai_service, _cache_service, _content_generator
    global _competitor_analysis_service, _hashtag_strategy_service
    global _prayer_times_service, _image_processor, _admin_notification_service
    
    _ai_service = None
    _cache_service = None
    _content_generator = None
    _competitor_analysis_service = None
    _hashtag_strategy_service = None
    _prayer_times_service = None
    _image_processor = None
    _admin_notification_service = None
    
    logger.info("Reset all services")


# For backward compatibility with the class-based approach
class ServiceContainer:
    """Wrapper class for backward compatibility"""
    
    @staticmethod
    def get_ai_service() -> AIService:
        return get_ai_service()
    
    @staticmethod
    def get_cache_service() -> CacheService:
        return get_cache_service()
    
    @staticmethod
    def get_content_generator() -> ContentGenerator:
        return get_content_generator()
    
    @staticmethod
    def get_competitor_analysis_service() -> CompetitorAnalysisService:
        return get_competitor_analysis_service()
    
    @staticmethod
    def get_hashtag_strategy_service() -> HashtagStrategyService:
        return get_hashtag_strategy_service()
    
    @staticmethod
    def get_prayer_times_service() -> PrayerTimesService:
        return get_prayer_times_service()
    
    @staticmethod
    def get_image_processor() -> ImageProcessor:
        return get_image_processor()
    
    @staticmethod
    def get_admin_notification_service() -> AdminNotificationService:
        return get_admin_notification_service()
    
    @staticmethod
    def reset_service(service_name: str) -> None:
        reset_service(service_name)
    
    @staticmethod
    def reset_all_services() -> None:
        reset_all_services()


def get_service_container() -> ServiceContainer:
    """Get service container for backward compatibility"""
    return ServiceContainer()