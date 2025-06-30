"""
Platform configuration for Kuwait Social AI
Centralized configuration for platform-specific settings
"""

from datetime import time
import os
import json

class PlatformConfig:
    """Configuration for social media platforms"""
    
    # Load from environment or use defaults
    _config_file = os.getenv('PLATFORM_CONFIG_FILE', 'config/platform_settings.json')
    
    # Default configuration
    PLATFORM_LIMITS = {
        'instagram': {
            'caption_max_length': 2200,
            'hashtag_max_count': 30,
            'bio_max_length': 150,
            'story_duration': 15,  # seconds
            'reel_max_duration': 90,  # seconds
            'carousel_max_items': 10,
            'username_max_length': 30,
            'formats': {
                'square': {'width': 1080, 'height': 1080},
                'portrait': {'width': 1080, 'height': 1350},
                'landscape': {'width': 1080, 'height': 566},
                'story': {'width': 1080, 'height': 1920}
            }
        },
        'snapchat': {
            'caption_max_length': 250,
            'hashtag_max_count': 100,
            'story_duration': 10,  # seconds
            'snap_duration': 10,  # seconds
            'formats': {
                'story': {'width': 1080, 'height': 1920},
                'ad': {'width': 1080, 'height': 1920}
            }
        },
        'tiktok': {
            'caption_max_length': 2200,
            'hashtag_max_count': 100,
            'video_max_duration': 180,  # seconds
            'bio_max_length': 80,
            'formats': {
                'video': {'width': 1080, 'height': 1920}
            }
        },
        'twitter': {
            'tweet_max_length': 280,
            'thread_max_tweets': 25,
            'video_max_duration': 140,  # seconds
            'formats': {
                'landscape': {'width': 1200, 'height': 675},
                'portrait': {'width': 1080, 'height': 1350}
            }
        }
    }
    
    # Kuwait-specific settings
    KUWAIT_SETTINGS = {
        'timezone': 'Asia/Kuwait',
        'business_days': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday'],
        'weekend_days': ['Friday', 'Saturday'],
        'business_hours': {
            'start': time(8, 0),
            'end': time(17, 0),
            'break_start': time(12, 0),
            'break_end': time(13, 0)
        },
        'prayer_times': {
            # Fallback times - actual times are fetched from API via get_prayer_times()
            # These are only used if the API is unavailable
            'Fajr': {'start': time(4, 30), 'end': time(5, 30)},
            'Sunrise': {'start': time(5, 45), 'end': time(6, 15)},
            'Dhuhr': {'start': time(11, 45), 'end': time(12, 30)},
            'Asr': {'start': time(15, 0), 'end': time(15, 45)},
            'Maghrib': {'start': time(17, 30), 'end': time(18, 15)},
            'Isha': {'start': time(19, 0), 'end': time(19, 45)}
        },
        'ramadan_mode': False,  # Should be updated based on Islamic calendar
        'friday_prayer': {
            'start': time(11, 30),
            'end': time(13, 0)
        }
    }
    
    # Optimal posting times for Kuwait
    OPTIMAL_POSTING_TIMES = {
        'weekdays': [
            {'time': time(9, 0), 'engagement': 'high'},
            {'time': time(13, 0), 'engagement': 'medium'},
            {'time': time(17, 0), 'engagement': 'high'},
            {'time': time(20, 0), 'engagement': 'very_high'}
        ],
        'weekends': [
            {'time': time(10, 0), 'engagement': 'medium'},
            {'time': time(14, 0), 'engagement': 'high'},
            {'time': time(18, 0), 'engagement': 'high'},
            {'time': time(21, 0), 'engagement': 'very_high'}
        ]
    }
    
    # Content moderation settings
    MODERATION_SETTINGS = {
        'inappropriate_terms': [
            'alcohol', 'beer', 'wine', 'vodka', 'whiskey',
            'pork', 'bacon', 'ham',
            'gambling', 'casino', 'betting', 'lottery',
            'dating', 'hookup',
            'nude', 'naked', 'nsfw'
        ],
        'positive_terms': [
            'halal', 'family', 'traditional', 'quality',
            'authentic', 'fresh', 'healthy', 'blessed',
            'kuwait', 'kuwaiti', 'ramadan', 'eid'
        ],
        'cultural_guidelines': {
            'respect_prayer_times': True,
            'include_arabic': True,
            'family_friendly': True,
            'gender_appropriate': True
        }
    }
    
    # Trending hashtags (should be updated regularly)
    TRENDING_HASHTAGS = {
        'general': ['#Kuwait', '#الكويت', '#Q8', '#KuwaitCity'],
        'food': ['#KuwaitFood', '#مطاعم_الكويت', '#KuwaitRestaurants'],
        'shopping': ['#KuwaitShopping', '#تسوق_الكويت', '#KuwaitMalls'],
        'events': ['#KuwaitEvents', '#فعاليات_الكويت'],
        'ramadan': ['#RamadanKuwait', '#رمضان_الكويت', '#رمضان_كريم'],
        'national': ['#KuwaitNationalDay', '#العيد_الوطني_الكويتي']
    }
    
    @classmethod
    def load_from_file(cls):
        """Load configuration from JSON file if it exists"""
        if os.path.exists(cls._config_file):
            try:
                with open(cls._config_file, 'r') as f:
                    config = json.load(f)
                    
                # Update configuration with file contents
                if 'platform_limits' in config:
                    cls.PLATFORM_LIMITS.update(config['platform_limits'])
                if 'kuwait_settings' in config:
                    cls.KUWAIT_SETTINGS.update(config['kuwait_settings'])
                if 'moderation_settings' in config:
                    cls.MODERATION_SETTINGS.update(config['moderation_settings'])
                    
            except Exception as e:
                print(f"Error loading platform config: {e}")
    
    @classmethod
    def get_platform_limit(cls, platform: str, limit_type: str, default=None):
        """Get specific platform limit"""
        platform_config = cls.PLATFORM_LIMITS.get(platform, {})
        return platform_config.get(limit_type, default)
    
    @classmethod
    def get_prayer_times(cls, date_obj=None):
        """Get prayer times from external API"""
        try:
            from services.prayer_times_service import get_prayer_times
            return get_prayer_times(date_obj)
        except Exception as e:
            # Fallback to cached/default times if API fails
            print(f"Prayer times API failed: {e}")
            return cls.KUWAIT_SETTINGS['prayer_times']
    
    @classmethod
    def is_prayer_time(cls, check_time=None):
        """Check if given time is during prayer time"""
        try:
            from services.prayer_times_service import is_prayer_time
            return is_prayer_time(check_time)
        except Exception as e:
            # Fallback to hardcoded check
            from datetime import datetime
            
            if check_time is None:
                check_time = datetime.now().time()
            
            for prayer_name, times in cls.KUWAIT_SETTINGS['prayer_times'].items():
                if times['start'] <= check_time <= times['end']:
                    return True, prayer_name
            
            return False, None
    
    @classmethod
    def get_optimal_posting_time(cls, day_type='weekday'):
        """Get optimal posting times for given day type"""
        if day_type == 'weekend':
            return cls.OPTIMAL_POSTING_TIMES['weekends']
        return cls.OPTIMAL_POSTING_TIMES['weekdays']
    
    @classmethod
    def save_to_file(cls):
        """Save current configuration to file"""
        config = {
            'platform_limits': cls.PLATFORM_LIMITS,
            'kuwait_settings': cls.KUWAIT_SETTINGS,
            'moderation_settings': cls.MODERATION_SETTINGS,
            'trending_hashtags': cls.TRENDING_HASHTAGS
        }
        
        # Convert time objects to strings for JSON serialization
        def time_to_str(obj):
            if isinstance(obj, time):
                return obj.strftime('%H:%M')
            elif isinstance(obj, dict):
                return {k: time_to_str(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [time_to_str(item) for item in obj]
            return obj
        
        config_serializable = time_to_str(config)
        
        os.makedirs(os.path.dirname(cls._config_file), exist_ok=True)
        with open(cls._config_file, 'w') as f:
            json.dump(config_serializable, f, indent=2)

# Load configuration on import
PlatformConfig.load_from_file()