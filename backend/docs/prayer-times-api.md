# Prayer Times API Documentation

## Overview

The Kuwait Social AI platform provides accurate, dynamic prayer times for Kuwait through external APIs. This ensures that prayer times are always up-to-date and account for seasonal variations.

## Features

1. **Dynamic Prayer Times**: Fetches accurate prayer times from external APIs
2. **Fallback Support**: Uses cached times if APIs are unavailable
3. **Caching**: Prayer times are cached for 1 hour to reduce API calls
4. **Multiple API Sources**: Fallback to alternative APIs if primary fails
5. **Seasonal Adjustments**: Accounts for seasonal prayer time variations
6. **Friday Prayer**: Special handling for Jummah prayers

## API Endpoints

### Get Today's Prayer Times
```
GET /api/prayer-times/today
```

**Response:**
```json
{
    "success": true,
    "date": "2024-01-15",
    "prayer_times": {
        "Fajr": {
            "start": "05:15",
            "end": "06:30",
            "duration_minutes": 75
        },
        "Sunrise": {
            "start": "06:30",
            "end": "06:45",
            "duration_minutes": 15
        },
        "Dhuhr": {
            "start": "11:50",
            "end": "12:35",
            "duration_minutes": 45
        },
        "Asr": {
            "start": "14:45",
            "end": "15:30",
            "duration_minutes": 45
        },
        "Maghrib": {
            "start": "17:15",
            "end": "18:00",
            "duration_minutes": 45
        },
        "Isha": {
            "start": "18:45",
            "end": "19:45",
            "duration_minutes": 60
        }
    },
    "timezone": "Asia/Kuwait"
}
```

### Get Prayer Times by Date
```
GET /api/prayer-times/date/2024-01-20
```

**Response:** Same format as today's prayer times

### Check Current Prayer
```
GET /api/prayer-times/current
```

**Response:**
```json
{
    "success": true,
    "is_prayer_time": true,
    "prayer_name": "Dhuhr",
    "current_time": "12:15",
    "timezone": "Asia/Kuwait"
}
```

### Get Next Prayer
```
GET /api/prayer-times/next
```

**Response:**
```json
{
    "success": true,
    "next_prayer": {
        "name": "Asr",
        "time": "14:45",
        "date": "2024-01-15",
        "time_until_minutes": 150,
        "time_until_formatted": "2 hours 30 minutes"
    },
    "current_time": "2024-01-15 12:15",
    "timezone": "Asia/Kuwait"
}
```

### Get Prayer Times Range
```
GET /api/prayer-times/range?start_date=2024-01-15&end_date=2024-01-20
```

**Response:**
```json
{
    "success": true,
    "start_date": "2024-01-15",
    "end_date": "2024-01-20",
    "prayer_times": {
        "2024-01-15": {
            "Fajr": {"start": "05:15", "end": "06:30", "duration_minutes": 75},
            // ... other prayers
        },
        "2024-01-16": {
            // ... prayer times
        }
        // ... more dates
    },
    "timezone": "Asia/Kuwait"
}
```

### Get Friday Prayer Time
```
GET /api/prayer-times/friday
```

**Response:**
```json
{
    "success": true,
    "date": "2024-01-19",
    "friday_prayer": {
        "khutbah_start": "11:50",
        "prayer_start": "12:20",
        "end": "13:20"
    },
    "day_name": "Friday",
    "timezone": "Asia/Kuwait"
}
```

## Integration in Application

### Content Scheduling
The application uses prayer times to:
- Warn users about scheduling posts during prayer times
- Suggest alternative posting times
- Automatically pause campaigns during prayer times

### Example Usage in Code
```python
from config.platform_config import PlatformConfig

# Check if current time is prayer time
is_prayer, prayer_name = PlatformConfig.is_prayer_time()
if is_prayer:
    print(f"It's {prayer_name} time")

# Get today's prayer times
prayer_times = PlatformConfig.get_prayer_times()
for prayer, times in prayer_times.items():
    print(f"{prayer}: {times['start']} - {times['end']}")
```

## External APIs Used

### Primary: Aladhan API
- **Endpoint**: `http://api.aladhan.com/v1/timingsByCity`
- **Method**: Gulf Region calculation method
- **School**: Shafi
- **Features**: 
  - Accurate calculations for Kuwait
  - Multiple calculation methods
  - Hijri calendar support

### Fallback APIs
1. Islamic Finder API (when available)
2. Local calculation based on sun position

## Caching Strategy

1. **TTL Cache**: 1-hour cache for API responses
2. **Date-based Keys**: Cache key includes date for accuracy
3. **Fallback Data**: Hardcoded times used if all APIs fail

## Error Handling

### API Failures
- Automatic fallback to next API in list
- Use cached data if available
- Resort to hardcoded times with seasonal adjustment

### Invalid Requests
- Date validation (must be within 1 year)
- Date range limits (max 30 days for range queries)
- Proper error messages with error codes

## Configuration

### Environment Variables
```bash
# Optional: Custom prayer calculation method
PRAYER_CALCULATION_METHOD=8  # Gulf Region

# Optional: Prayer time adjustments (minutes)
PRAYER_TIME_ADJUSTMENT_FAJR=0
PRAYER_TIME_ADJUSTMENT_DHUHR=0
PRAYER_TIME_ADJUSTMENT_ASR=0
PRAYER_TIME_ADJUSTMENT_MAGHRIB=0
PRAYER_TIME_ADJUSTMENT_ISHA=0
```

### Customization
Prayer durations can be customized in the service:
```python
durations = {
    'Fajr': 60,      # Until sunrise
    'Sunrise': 15,   # Brief period
    'Dhuhr': 45,     # Standard prayer duration
    'Asr': 45,       
    'Maghrib': 45,   
    'Isha': 60       
}
```

## Best Practices

1. **Cache Warmup**: Pre-fetch prayer times at application startup
2. **Error Monitoring**: Log API failures for monitoring
3. **User Timezone**: Always display times in Kuwait timezone
4. **Graceful Degradation**: Ensure app works even if prayer API fails
5. **Update Notifications**: Notify users if prayer times change significantly

## Testing

```python
# Test prayer time fetching
from services.prayer_times_service import get_prayer_times
from datetime import date

# Get today's times
times = get_prayer_times()
assert 'Fajr' in times
assert times['Fajr']['start'] < times['Fajr']['end']

# Get specific date
tomorrow = date.today() + timedelta(days=1)
times = get_prayer_times(tomorrow)
assert times is not None
```

## Troubleshooting

### "Prayer times API failed"
- Check internet connection
- Verify API endpoints are accessible
- Check for API rate limits
- Review fallback times configuration

### Incorrect Prayer Times
- Verify timezone settings
- Check calculation method configuration
- Ensure location is set to Kuwait City
- Compare with official Kuwait prayer time sources