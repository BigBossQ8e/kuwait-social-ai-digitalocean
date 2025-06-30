"""
Prayer Times Service for Kuwait
Fetches accurate prayer times from external APIs
"""

import os
import requests
import json
from datetime import datetime, date, time, timedelta
from typing import Dict, List, Optional, Tuple
import pytz
from cachetools import TTLCache
import logging
from exceptions import KuwaitSocialAIException
from pathlib import Path

class PrayerTimesException(KuwaitSocialAIException):
    """Exception for prayer times service errors"""
    status_code = 503
    error_code = 'PRAYER_TIMES_ERROR'


class PrayerTimesService:
    """Service to fetch and manage prayer times for Kuwait"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.kuwait_tz = pytz.timezone('Asia/Kuwait')
        
        # Cache prayer times for 1 hour
        self.cache = TTLCache(maxsize=100, ttl=3600)
        
        # Long-term cache file for fallback when all APIs fail
        self.cache_dir = Path('cache')
        self.cache_dir.mkdir(exist_ok=True)
        self.persistent_cache_file = self.cache_dir / 'prayer_times_cache.json'
        
        # Track API failures for admin notifications
        self.consecutive_failures = 0
        self.max_failures_before_alert = 3
        
        # API endpoints (in order of preference)
        self.api_endpoints = [
            {
                'name': 'Aladhan',
                'url': 'http://api.aladhan.com/v1/timingsByCity',
                'params': {
                    'city': 'Kuwait City',
                    'country': 'Kuwait',
                    'method': 8,  # Gulf Region method
                    'school': 0   # Shafi school
                }
            },
            {
                'name': 'Islamic Finder',
                'url': 'https://api.pray.zone/v2/times/today.json',
                'params': {
                    'city': 'kuwait-city',
                    'school': 'Shafi'
                }
            }
        ]
        
        # Fallback prayer times (approximate)
        self.fallback_times = {
            'Fajr': time(4, 30),
            'Sunrise': time(5, 45),
            'Dhuhr': time(11, 45),
            'Asr': time(15, 0),
            'Maghrib': time(17, 30),
            'Isha': time(19, 0)
        }
    
    def get_prayer_times(self, date_obj: Optional[date] = None) -> Dict[str, Dict]:
        """
        Get prayer times for a specific date
        
        Args:
            date_obj: Date to get prayer times for (default: today)
            
        Returns:
            Dictionary with prayer names and their start/end times
        """
        if date_obj is None:
            date_obj = datetime.now(self.kuwait_tz).date()
        
        # Check cache
        cache_key = f"prayer_times_{date_obj.isoformat()}"
        cached_times = self.cache.get(cache_key)
        if cached_times:
            return cached_times
        
        # Try each API endpoint
        for api_config in self.api_endpoints:
            try:
                times = self._fetch_from_api(api_config, date_obj)
                if times:
                    # Add buffer times (duration for each prayer)
                    times_with_duration = self._add_prayer_durations(times)
                    self.cache[cache_key] = times_with_duration
                    
                    # Save to persistent cache on successful fetch
                    self._save_to_persistent_cache(date_obj, times_with_duration)
                    
                    # Reset failure counter on success
                    self.consecutive_failures = 0
                    
                    return times_with_duration
            except Exception as e:
                self.logger.warning(
                    f"Failed to fetch from {api_config['name']}: {str(e)}"
                )
                continue
        
        # If all APIs fail, try persistent cache first
        self.logger.error("All prayer time APIs failed, checking persistent cache")
        
        # Increment failure counter
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.max_failures_before_alert:
            self._notify_admin_of_api_failure()
        
        # Try to get from persistent cache
        cached_data = self._get_from_persistent_cache(date_obj)
        if cached_data:
            self.logger.info(f"Using cached prayer times from {cached_data['cached_date']}")
            return cached_data['times']
        
        # Last resort: use fallback with date adjustment
        self.logger.warning("No cached data available, using fallback times")
        return self._get_fallback_times(date_obj)
    
    def _fetch_from_api(self, api_config: Dict, date_obj: date) -> Dict[str, time]:
        """Fetch prayer times from a specific API"""
        if api_config['name'] == 'Aladhan':
            return self._fetch_from_aladhan(api_config, date_obj)
        elif api_config['name'] == 'Islamic Finder':
            return self._fetch_from_islamic_finder(api_config, date_obj)
        else:
            raise ValueError(f"Unknown API: {api_config['name']}")
    
    def _fetch_from_aladhan(self, api_config: Dict, date_obj: date) -> Dict[str, time]:
        """Fetch from Aladhan API"""
        params = api_config['params'].copy()
        params['date'] = date_obj.strftime('%d-%m-%Y')
        
        response = requests.get(
            api_config['url'],
            params=params,
            timeout=5
        )
        response.raise_for_status()
        
        data = response.json()
        if data.get('code') != 200:
            raise PrayerTimesException(
                f"Aladhan API error: {data.get('status', 'Unknown error')}"
            )
        
        timings = data['data']['timings']
        
        # Convert to time objects
        prayer_times = {}
        for prayer in ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
            time_str = timings.get(prayer, '')
            if time_str:
                # Remove timezone info if present
                time_str = time_str.split(' ')[0]
                hour, minute = map(int, time_str.split(':'))
                prayer_times[prayer] = time(hour, minute)
        
        return prayer_times
    
    def _fetch_from_islamic_finder(self, api_config: Dict, date_obj: date) -> Dict[str, time]:
        """Fetch from Islamic Finder API"""
        # This is a placeholder - implement based on actual API documentation
        # For now, raise an exception to move to next API
        raise NotImplementedError("Islamic Finder API integration pending")
    
    def _add_prayer_durations(self, prayer_times: Dict[str, time]) -> Dict[str, Dict]:
        """Add duration/end times for each prayer"""
        # Approximate durations for each prayer
        durations = {
            'Fajr': 60,      # 60 minutes until sunrise
            'Sunrise': 15,   # 15 minutes
            'Dhuhr': 45,     # 45 minutes
            'Asr': 45,       # 45 minutes
            'Maghrib': 45,   # 45 minutes
            'Isha': 60       # 60 minutes
        }
        
        result = {}
        prayer_list = list(prayer_times.keys())
        
        for i, (prayer, start_time) in enumerate(prayer_times.items()):
            # Calculate end time
            if prayer in durations:
                duration_minutes = durations[prayer]
            else:
                duration_minutes = 30  # Default duration
            
            # Special case: Fajr ends at sunrise
            if prayer == 'Fajr' and 'Sunrise' in prayer_times:
                end_time = prayer_times['Sunrise']
            else:
                # Calculate end time
                start_datetime = datetime.combine(date.today(), start_time)
                end_datetime = start_datetime + timedelta(minutes=duration_minutes)
                end_time = end_datetime.time()
            
            result[prayer] = {
                'start': start_time,
                'end': end_time,
                'duration_minutes': duration_minutes
            }
        
        return result
    
    def _get_fallback_times(self, date_obj: date) -> Dict[str, Dict]:
        """Get fallback prayer times with seasonal adjustment"""
        # Basic seasonal adjustment (simplified)
        month = date_obj.month
        
        # Summer months (April to September) - prayers are later
        if 4 <= month <= 9:
            adjustment = timedelta(minutes=30)
        # Winter months - prayers are earlier
        else:
            adjustment = timedelta(minutes=-20)
        
        adjusted_times = {}
        for prayer, base_time in self.fallback_times.items():
            # Adjust time
            base_datetime = datetime.combine(date.today(), base_time)
            adjusted_datetime = base_datetime + adjustment
            adjusted_time = adjusted_datetime.time()
            
            adjusted_times[prayer] = adjusted_time
        
        return self._add_prayer_durations(adjusted_times)
    
    def is_prayer_time(self, check_time: Optional[datetime] = None) -> Tuple[bool, Optional[str]]:
        """
        Check if current time is during prayer
        
        Args:
            check_time: Time to check (default: current time)
            
        Returns:
            Tuple of (is_prayer_time, prayer_name)
        """
        if check_time is None:
            check_time = datetime.now(self.kuwait_tz)
        
        # Get prayer times for the date
        prayer_times = self.get_prayer_times(check_time.date())
        
        # Check each prayer
        current_time = check_time.time()
        for prayer_name, times in prayer_times.items():
            if times['start'] <= current_time <= times['end']:
                return True, prayer_name
        
        return False, None
    
    def get_next_prayer(self, from_time: Optional[datetime] = None) -> Dict[str, any]:
        """
        Get the next upcoming prayer
        
        Args:
            from_time: Reference time (default: current time)
            
        Returns:
            Dictionary with prayer name, time, and time until prayer
        """
        if from_time is None:
            from_time = datetime.now(self.kuwait_tz)
        
        prayer_times = self.get_prayer_times(from_time.date())
        current_time = from_time.time()
        
        # Find next prayer today
        for prayer_name, times in prayer_times.items():
            if times['start'] > current_time:
                time_until = self._calculate_time_until(
                    from_time, 
                    datetime.combine(from_time.date(), times['start'])
                )
                return {
                    'name': prayer_name,
                    'time': times['start'],
                    'time_until_minutes': time_until,
                    'date': from_time.date()
                }
        
        # If no prayer left today, get first prayer tomorrow
        tomorrow = from_time.date() + timedelta(days=1)
        tomorrow_prayers = self.get_prayer_times(tomorrow)
        first_prayer = list(tomorrow_prayers.keys())[0]
        
        time_until = self._calculate_time_until(
            from_time,
            datetime.combine(tomorrow, tomorrow_prayers[first_prayer]['start'])
        )
        
        return {
            'name': first_prayer,
            'time': tomorrow_prayers[first_prayer]['start'],
            'time_until_minutes': time_until,
            'date': tomorrow
        }
    
    def _calculate_time_until(self, from_time: datetime, to_time: datetime) -> int:
        """Calculate minutes between two times"""
        # Ensure both times are timezone-aware
        if from_time.tzinfo is None:
            from_time = self.kuwait_tz.localize(from_time)
        if to_time.tzinfo is None:
            to_time = self.kuwait_tz.localize(to_time)
        
        delta = to_time - from_time
        return int(delta.total_seconds() / 60)
    
    def get_friday_prayer_time(self, date_obj: Optional[date] = None) -> Dict[str, time]:
        """Get Friday (Jummah) prayer time"""
        if date_obj is None:
            date_obj = datetime.now(self.kuwait_tz).date()
        
        # Friday prayer is typically 30 minutes after Dhuhr
        prayer_times = self.get_prayer_times(date_obj)
        dhuhr_time = prayer_times.get('Dhuhr', {}).get('start')
        
        if dhuhr_time:
            # Add 30 minutes for Khutbah
            jummah_start = datetime.combine(date.today(), dhuhr_time)
            jummah_start += timedelta(minutes=30)
            
            return {
                'start': jummah_start.time(),
                'end': (jummah_start + timedelta(minutes=60)).time(),
                'khutbah_start': dhuhr_time
            }
        
        # Fallback
        return {
            'start': time(12, 30),
            'end': time(13, 30),
            'khutbah_start': time(12, 00)
        }
    
    def get_prayer_times_for_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Dict[str, Dict]]:
        """Get prayer times for a date range"""
        result = {}
        current_date = start_date
        
        while current_date <= end_date:
            try:
                result[current_date.isoformat()] = self.get_prayer_times(current_date)
            except Exception as e:
                self.logger.error(
                    f"Failed to get prayer times for {current_date}: {str(e)}"
                )
                result[current_date.isoformat()] = self._get_fallback_times(current_date)
            
            current_date += timedelta(days=1)
        
        return result
    
    def _save_to_persistent_cache(self, date_obj: date, times: Dict[str, Dict]):
        """Save prayer times to persistent cache file"""
        try:
            # Load existing cache
            cache_data = {}
            if self.persistent_cache_file.exists():
                with open(self.persistent_cache_file, 'r') as f:
                    cache_data = json.load(f)
            
            # Convert time objects to strings for JSON serialization
            serializable_times = {}
            for prayer, time_data in times.items():
                serializable_times[prayer] = {
                    'start': time_data['start'].isoformat(),
                    'end': time_data['end'].isoformat(),
                    'duration_minutes': time_data['duration_minutes']
                }
            
            # Save times with metadata
            cache_data[date_obj.isoformat()] = {
                'times': serializable_times,
                'cached_at': datetime.now().isoformat(),
                'source': 'api'
            }
            
            # Keep only last 30 days of cache
            cutoff_date = (date.today() - timedelta(days=30)).isoformat()
            cache_data = {k: v for k, v in cache_data.items() if k >= cutoff_date}
            
            # Write to file
            with open(self.persistent_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save to persistent cache: {str(e)}")
    
    def _get_from_persistent_cache(self, date_obj: date) -> Optional[Dict]:
        """Get prayer times from persistent cache"""
        try:
            if not self.persistent_cache_file.exists():
                return None
            
            with open(self.persistent_cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # First, try exact date match
            date_key = date_obj.isoformat()
            if date_key in cache_data:
                return self._deserialize_cached_times(cache_data[date_key])
            
            # If no exact match, find closest date within 7 days
            target_date = date_obj
            for days_offset in [1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7]:
                check_date = target_date + timedelta(days=days_offset)
                check_key = check_date.isoformat()
                if check_key in cache_data:
                    self.logger.info(f"Using prayer times from {check_date} (closest available)")
                    cached_entry = cache_data[check_key]
                    
                    # Adjust times for the different date
                    adjusted_times = self._adjust_times_for_date(
                        cached_entry['times'], 
                        check_date, 
                        target_date
                    )
                    
                    return {
                        'times': adjusted_times,
                        'cached_date': check_date.isoformat()
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to read from persistent cache: {str(e)}")
            return None
    
    def _deserialize_cached_times(self, cached_entry: Dict) -> Dict:
        """Convert cached time strings back to time objects"""
        times = {}
        for prayer, time_data in cached_entry['times'].items():
            times[prayer] = {
                'start': time.fromisoformat(time_data['start']),
                'end': time.fromisoformat(time_data['end']),
                'duration_minutes': time_data['duration_minutes']
            }
        return {
            'times': times,
            'cached_date': cached_entry.get('cached_at', 'unknown')
        }
    
    def _adjust_times_for_date(self, times: Dict, from_date: date, to_date: date) -> Dict:
        """Adjust prayer times from one date to another (simple approximation)"""
        # Calculate day difference
        day_diff = (to_date - from_date).days
        
        # Approximate adjustment: ~2 minutes per day
        minute_adjustment = day_diff * 2
        
        adjusted_times = {}
        for prayer, time_data in times.items():
            start_time = time.fromisoformat(time_data['start'])
            end_time = time.fromisoformat(time_data['end'])
            
            # Apply adjustment
            start_datetime = datetime.combine(date.today(), start_time)
            end_datetime = datetime.combine(date.today(), end_time)
            
            start_datetime += timedelta(minutes=minute_adjustment)
            end_datetime += timedelta(minutes=minute_adjustment)
            
            adjusted_times[prayer] = {
                'start': start_datetime.time(),
                'end': end_datetime.time(),
                'duration_minutes': time_data['duration_minutes']
            }
        
        return adjusted_times
    
    def _notify_admin_of_api_failure(self):
        """Send notification to admin about API failures"""
        try:
            # Import here to avoid circular dependency
            from services.admin_notification_service import send_critical_alert
            
            message = f"""
            CRITICAL: All prayer time APIs have failed {self.consecutive_failures} times in a row.
            
            Affected services:
            - {', '.join([api['name'] for api in self.api_endpoints])}
            
            The system is currently using cached or fallback prayer times.
            Please investigate the API connectivity issues.
            
            Time: {datetime.now(self.kuwait_tz).strftime('%Y-%m-%d %H:%M:%S')} Kuwait Time
            """
            
            send_critical_alert(
                subject="Prayer Time API Failure",
                message=message,
                service="PrayerTimesService"
            )
            
            # Reset counter after notification
            self.consecutive_failures = 0
            
        except Exception as e:
            self.logger.error(f"Failed to send admin notification: {str(e)}")


# Note: No singleton instance created here
# Use get_prayer_times_service() from services.container instead


# Convenience functions
def get_prayer_times(date_obj: Optional[date] = None) -> Dict[str, Dict]:
    """Get prayer times for a specific date"""
    return prayer_times_service.get_prayer_times(date_obj)


def is_prayer_time(check_time: Optional[datetime] = None) -> Tuple[bool, Optional[str]]:
    """Check if current time is during prayer"""
    return prayer_times_service.is_prayer_time(check_time)


def get_next_prayer(from_time: Optional[datetime] = None) -> Dict[str, any]:
    """Get the next upcoming prayer"""
    return prayer_times_service.get_next_prayer(from_time)