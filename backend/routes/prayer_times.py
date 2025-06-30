"""
Prayer Times API Routes
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, date, timedelta
from services.prayer_times_service import (
    get_prayer_times, is_prayer_time, get_next_prayer,
    PrayerTimesException
)
import pytz

prayer_times_bp = Blueprint('prayer_times', __name__)
kuwait_tz = pytz.timezone('Asia/Kuwait')


@prayer_times_bp.route('/today', methods=['GET'])
def get_today_prayer_times():
    """Get prayer times for today"""
    try:
        times = get_prayer_times()
        
        # Format times for JSON response
        formatted_times = {}
        for prayer, time_data in times.items():
            formatted_times[prayer] = {
                'start': time_data['start'].strftime('%H:%M'),
                'end': time_data['end'].strftime('%H:%M'),
                'duration_minutes': time_data['duration_minutes']
            }
        
        return jsonify({
            'success': True,
            'date': date.today().isoformat(),
            'prayer_times': formatted_times,
            'timezone': 'Asia/Kuwait'
        })
        
    except PrayerTimesException as e:
        return jsonify({
            'error': str(e),
            'error_code': e.error_code
        }), e.status_code
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch prayer times',
            'error_code': 'PRAYER_TIMES_ERROR',
            'details': str(e)
        }), 500


@prayer_times_bp.route('/date/<date_str>', methods=['GET'])
def get_prayer_times_by_date(date_str):
    """Get prayer times for a specific date"""
    try:
        # Parse date
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Check date range (within 1 year)
        today = date.today()
        if abs((target_date - today).days) > 365:
            return jsonify({
                'error': 'Date must be within 1 year from today',
                'error_code': 'INVALID_DATE_RANGE'
            }), 400
        
        times = get_prayer_times(target_date)
        
        # Format times for JSON response
        formatted_times = {}
        for prayer, time_data in times.items():
            formatted_times[prayer] = {
                'start': time_data['start'].strftime('%H:%M'),
                'end': time_data['end'].strftime('%H:%M'),
                'duration_minutes': time_data['duration_minutes']
            }
        
        return jsonify({
            'success': True,
            'date': target_date.isoformat(),
            'prayer_times': formatted_times,
            'timezone': 'Asia/Kuwait'
        })
        
    except ValueError:
        return jsonify({
            'error': 'Invalid date format. Use YYYY-MM-DD',
            'error_code': 'INVALID_DATE_FORMAT'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch prayer times',
            'error_code': 'PRAYER_TIMES_ERROR',
            'details': str(e)
        }), 500


@prayer_times_bp.route('/current', methods=['GET'])
def check_current_prayer():
    """Check if it's currently prayer time"""
    try:
        is_prayer, prayer_name = is_prayer_time()
        
        return jsonify({
            'success': True,
            'is_prayer_time': is_prayer,
            'prayer_name': prayer_name,
            'current_time': datetime.now(kuwait_tz).strftime('%H:%M'),
            'timezone': 'Asia/Kuwait'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to check prayer time',
            'error_code': 'PRAYER_CHECK_ERROR',
            'details': str(e)
        }), 500


@prayer_times_bp.route('/next', methods=['GET'])
def get_next_prayer_time():
    """Get the next upcoming prayer"""
    try:
        next_prayer = get_next_prayer()
        
        return jsonify({
            'success': True,
            'next_prayer': {
                'name': next_prayer['name'],
                'time': next_prayer['time'].strftime('%H:%M'),
                'date': next_prayer['date'].isoformat(),
                'time_until_minutes': next_prayer['time_until_minutes'],
                'time_until_formatted': _format_time_until(next_prayer['time_until_minutes'])
            },
            'current_time': datetime.now(kuwait_tz).strftime('%Y-%m-%d %H:%M'),
            'timezone': 'Asia/Kuwait'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get next prayer',
            'error_code': 'NEXT_PRAYER_ERROR',
            'details': str(e)
        }), 500


@prayer_times_bp.route('/range', methods=['GET'])
def get_prayer_times_range():
    """Get prayer times for a date range"""
    try:
        # Get query parameters
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            return jsonify({
                'error': 'Both start_date and end_date are required',
                'error_code': 'MISSING_PARAMETERS'
            }), 400
        
        # Parse dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        # Validate date range
        if start_date > end_date:
            return jsonify({
                'error': 'start_date must be before end_date',
                'error_code': 'INVALID_DATE_RANGE'
            }), 400
        
        if (end_date - start_date).days > 30:
            return jsonify({
                'error': 'Date range cannot exceed 30 days',
                'error_code': 'DATE_RANGE_TOO_LARGE'
            }), 400
        
        # Get prayer times for each day
        from services.prayer_times_service import prayer_times_service
        times_range = prayer_times_service.get_prayer_times_for_range(start_date, end_date)
        
        # Format response
        formatted_range = {}
        for date_str, times in times_range.items():
            formatted_times = {}
            for prayer, time_data in times.items():
                formatted_times[prayer] = {
                    'start': time_data['start'].strftime('%H:%M'),
                    'end': time_data['end'].strftime('%H:%M'),
                    'duration_minutes': time_data['duration_minutes']
                }
            formatted_range[date_str] = formatted_times
        
        return jsonify({
            'success': True,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'prayer_times': formatted_range,
            'timezone': 'Asia/Kuwait'
        })
        
    except ValueError:
        return jsonify({
            'error': 'Invalid date format. Use YYYY-MM-DD',
            'error_code': 'INVALID_DATE_FORMAT'
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch prayer times range',
            'error_code': 'PRAYER_RANGE_ERROR',
            'details': str(e)
        }), 500


@prayer_times_bp.route('/friday', methods=['GET'])
def get_friday_prayer():
    """Get Friday (Jummah) prayer time"""
    try:
        # Get next Friday or today if it's Friday
        today = date.today()
        days_until_friday = (4 - today.weekday()) % 7
        if days_until_friday == 0 and datetime.now(kuwait_tz).time() > timedelta(hours=14):
            # If it's Friday after 2 PM, get next Friday
            days_until_friday = 7
        
        next_friday = today + timedelta(days=days_until_friday)
        
        # Get Friday prayer time
        from services.prayer_times_service import prayer_times_service
        jummah_time = prayer_times_service.get_friday_prayer_time(next_friday)
        
        return jsonify({
            'success': True,
            'date': next_friday.isoformat(),
            'friday_prayer': {
                'khutbah_start': jummah_time['khutbah_start'].strftime('%H:%M'),
                'prayer_start': jummah_time['start'].strftime('%H:%M'),
                'end': jummah_time['end'].strftime('%H:%M')
            },
            'day_name': next_friday.strftime('%A'),
            'timezone': 'Asia/Kuwait'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get Friday prayer time',
            'error_code': 'FRIDAY_PRAYER_ERROR',
            'details': str(e)
        }), 500


def _format_time_until(minutes: int) -> str:
    """Format minutes into human-readable string"""
    if minutes < 60:
        return f"{minutes} minutes"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if hours == 1:
        if remaining_minutes == 0:
            return "1 hour"
        return f"1 hour {remaining_minutes} minutes"
    
    if remaining_minutes == 0:
        return f"{hours} hours"
    
    return f"{hours} hours {remaining_minutes} minutes"