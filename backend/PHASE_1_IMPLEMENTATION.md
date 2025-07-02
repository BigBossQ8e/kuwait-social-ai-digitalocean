# Phase 1 Implementation Guide - Quick Wins 🚀

Let's start implementing the Phase 1 features that will give immediate value to F&B clients.

## 1. Enhanced Templates System

### 1.1 Create Template Service
```python
# services/template_service.py

from typing import Dict, List, Optional
from datetime import datetime
import json

class TemplateService:
    """Advanced template management for multiple platforms and content types"""
    
    def __init__(self):
        self.templates = {
            'instagram': {
                'post': {
                    'daily_special': {
                        'structure': '{greeting} Today\'s special: {dish_name}! {description} {price} KWD. {cta}',
                        'hashtags': ['#DailySpecial', '#[Day]Special', '#KuwaitEats'],
                        'example': '🌟 Tuesday Special! Our famous Grilled Hammour with saffron rice. Fresh catch of the day! Only 4.5 KWD. Order now on Talabat!'
                    },
                    'weekend_family': {
                        'structure': '{emoji} Weekend Family Feast! {offer} Perfect for {family_size}. {features} {price} KWD {cta}',
                        'hashtags': ['#WeekendVibes', '#FamilyTime', '#KuwaitFamily'],
                        'example': '👨‍👩‍👧‍👦 Weekend Family Feast! Kids eat FREE with every adult meal! Perfect for families of 4-6. Includes drinks & dessert. Starting from 15 KWD. Reserve your table now!'
                    },
                    'delivery_promo': {
                        'structure': '{emoji} {platform} Exclusive! {offer} Use code: {code} {validity} {cta}',
                        'hashtags': ['#TalabatKuwait', '#DeliveryKuwait', '#OrderNow'],
                        'example': '🛵 Talabat Exclusive! 20% OFF on all orders above 5 KWD. Use code: TASTY20. Valid until midnight! Order now 👇'
                    }
                },
                'story': {
                    'behind_kitchen': {
                        'duration': 15,
                        'structure': 'Show {chef_action} with text overlay: {dish_name} in the making!',
                        'music': 'Upbeat, energetic',
                        'example': 'Chef preparing fresh pasta with overlay: "Fresh Fettuccine made daily!"'
                    },
                    'daily_special_story': {
                        'duration': 10,
                        'structure': 'Dish close-up with steam, price sticker animation',
                        'cta': 'Swipe up to order!'
                    }
                },
                'reels': {
                    'food_prep_30s': {
                        'structure': '0-5s: Hook, 5-25s: Process, 25-30s: Final result + CTA',
                        'music': 'Trending audio',
                        'text_overlay': 'Step-by-step captions',
                        'example': 'Making our famous Umm Ali from scratch!'
                    }
                }
            },
            'tiktok': {
                'trending_sounds': {
                    'structure': 'Match {food_action} to {sound_beat}',
                    'duration': '15-60s',
                    'hashtags': ['#KuwaitFoodie', '#Q8Food', '#FYP']
                }
            }
        }
        
        # F&B Specific templates
        self.f_and_b_templates = {
            'iftar_special': {
                'structure': '🌙 Iftar Special! Break your fast with our {dishes}. {features}. {price} KWD per person. {booking_info}',
                'required_elements': ['HALAL certified', 'Prayer time aware', 'Family sections'],
                'hashtags': ['#RamadanKuwait', '#IftarTime', '#رمضان_الكويت']
            },
            'weekend_breakfast': {
                'timing': 'Thursday-Friday 8AM-12PM',
                'structure': '🍳 Weekend Breakfast! {menu_highlights} All-day breakfast until {time}. {location}',
                'hashtags': ['#WeekendBrunch', '#KuwaitBreakfast', '#ThursdayVibes']
            },
            'diwaniya_catering': {
                'structure': '🏠 Diwaniya Catering Service! {package_details} Serves {guest_count}. {delivery_info}',
                'cultural_notes': 'Emphasize traditional items, generous portions',
                'hashtags': ['#DiwaniyaCatering', '#KuwaitTradition', '#ديوانية']
            }
        }

    def get_template(self, platform: str, content_type: str, template_name: str) -> Dict:
        """Get specific template with all details"""
        try:
            return self.templates[platform][content_type][template_name]
        except KeyError:
            # Fallback to F&B templates
            return self.f_and_b_templates.get(template_name, {})
    
    def generate_from_template(self, template_name: str, variables: Dict) -> str:
        """Generate content from template with variables"""
        template = self.get_template_by_name(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")
        
        content = template['structure']
        for key, value in variables.items():
            content = content.replace(f'{{{key}}}', str(value))
        
        return content
    
    def get_templates_by_category(self, category: str) -> List[Dict]:
        """Get all templates for a category (e.g., 'ramadan', 'delivery')"""
        result = []
        # Search through all templates
        for platform in self.templates.values():
            for content_type in platform.values():
                for name, template in content_type.items():
                    if category.lower() in name.lower():
                        result.append({
                            'name': name,
                            'template': template
                        })
        return result
```

### 1.2 Add Template Endpoints
```python
# routes/templates.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from services.template_service import TemplateService

templates_bp = Blueprint('templates', __name__, url_prefix='/api/templates')
template_service = TemplateService()

@templates_bp.route('/list', methods=['GET'])
@jwt_required()
def list_templates():
    """List all available templates"""
    platform = request.args.get('platform', 'instagram')
    content_type = request.args.get('type', 'post')
    
    templates = template_service.templates.get(platform, {}).get(content_type, {})
    
    return jsonify({
        'platform': platform,
        'content_type': content_type,
        'templates': list(templates.keys()),
        'details': templates
    })

@templates_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_from_template():
    """Generate content from template"""
    data = request.json
    template_name = data.get('template')
    variables = data.get('variables', {})
    
    try:
        content = template_service.generate_from_template(template_name, variables)
        return jsonify({
            'success': True,
            'content': content,
            'template_used': template_name
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

## 2. Prayer Time Smart Scheduling

### 2.1 Enhance Prayer Time Service
```python
# services/prayer_scheduler.py

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pytz

class PrayerAwareScheduler:
    """Smart scheduling that respects prayer times"""
    
    def __init__(self, prayer_service):
        self.prayer_service = prayer_service
        self.kuwait_tz = pytz.timezone('Asia/Kuwait')
        self.buffer_before = 10  # minutes before prayer
        self.buffer_after = 15   # minutes after prayer
    
    def is_prayer_time(self, timestamp: datetime) -> bool:
        """Check if given time conflicts with prayer"""
        prayer_times = self.prayer_service.get_prayer_times()
        
        for prayer, time_str in prayer_times.items():
            prayer_time = datetime.strptime(time_str, '%H:%M').replace(
                year=timestamp.year,
                month=timestamp.month,
                day=timestamp.day
            )
            
            # Create buffer window
            start_buffer = prayer_time - timedelta(minutes=self.buffer_before)
            end_buffer = prayer_time + timedelta(minutes=self.buffer_after)
            
            if start_buffer <= timestamp <= end_buffer:
                return True
        
        return False
    
    def get_next_available_slot(self, desired_time: datetime) -> datetime:
        """Find next available slot after prayer time"""
        if not self.is_prayer_time(desired_time):
            return desired_time
        
        # Try every 5 minutes for the next 2 hours
        current_time = desired_time
        for _ in range(24):  # 2 hours / 5 minutes
            current_time += timedelta(minutes=5)
            if not self.is_prayer_time(current_time):
                return current_time
        
        return desired_time + timedelta(hours=2)
    
    def get_optimal_posting_times(self, date: datetime) -> List[Dict]:
        """Get optimal posting times for a given day avoiding prayer times"""
        optimal_slots = []
        
        # Define potential posting times for F&B
        potential_times = [
            {'time': '08:00', 'type': 'breakfast', 'audience': 'early_risers'},
            {'time': '11:30', 'type': 'lunch_prep', 'audience': 'office_workers'},
            {'time': '14:00', 'type': 'lunch_late', 'audience': 'families'},
            {'time': '17:30', 'type': 'tea_time', 'audience': 'afternoon_crowd'},
            {'time': '19:30', 'type': 'dinner', 'audience': 'families'},
            {'time': '21:00', 'type': 'late_dinner', 'audience': 'young_adults'}
        ]
        
        for slot in potential_times:
            time = datetime.strptime(slot['time'], '%H:%M').replace(
                year=date.year, month=date.month, day=date.day
            )
            
            # Check if conflicts with prayer
            if self.is_prayer_time(time):
                adjusted_time = self.get_next_available_slot(time)
                slot['adjusted'] = True
                slot['original_time'] = slot['time']
                slot['time'] = adjusted_time.strftime('%H:%M')
                slot['reason'] = 'Adjusted for prayer time'
            
            optimal_slots.append(slot)
        
        return optimal_slots
```

## 3. Weather-Responsive Content

### 3.1 Weather Integration Service
```python
# services/weather_content_service.py

import requests
from typing import Dict, Optional
from datetime import datetime

class WeatherContentService:
    """Generate weather-appropriate content for Kuwait F&B"""
    
    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.kuwait_lat = 29.3759
        self.kuwait_lon = 47.9774
        
        # Temperature thresholds for Kuwait
        self.temp_thresholds = {
            'extreme_heat': 45,  # Celsius
            'very_hot': 40,
            'hot': 35,
            'pleasant': 25,
            'cool': 20
        }
        
        # Weather-based content suggestions
        self.weather_templates = {
            'extreme_heat': {
                'focus': ['ice_cream', 'cold_drinks', 'AC_seating', 'delivery'],
                'hashtags': ['#BeatTheHeat', '#KuwaitSummer', '#StayCool'],
                'promos': [
                    'FREE ice cream with every meal! 🍦',
                    'Ice-cold beverages all day! ❄️',
                    'Stay cool in our fully AC dining area!'
                ]
            },
            'sandstorm': {
                'focus': ['indoor_dining', 'delivery', 'comfort_food'],
                'hashtags': ['#IndoorDining', '#DeliveryAvailable'],
                'promos': [
                    'Skip the sandstorm - we deliver! 🚗',
                    'Cozy indoor seating available'
                ]
            },
            'pleasant': {
                'focus': ['outdoor_seating', 'shisha', 'garden'],
                'hashtags': ['#OutdoorDining', '#KuwaitWeather', '#GardenSeating'],
                'promos': [
                    'Enjoy our outdoor terrace! 🌿',
                    'Perfect weather for shisha & dinner'
                ]
            }
        }
    
    def get_current_weather(self) -> Dict:
        """Get current Kuwait weather"""
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': self.kuwait_lat,
                'lon': self.kuwait_lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params)
            return response.json()
        except:
            # Fallback data
            return {'main': {'temp': 38}, 'weather': [{'main': 'Clear'}]}
    
    def generate_weather_content(self, restaurant_type: str) -> Dict:
        """Generate weather-appropriate content suggestions"""
        weather = self.get_current_weather()
        temp = weather['main']['temp']
        conditions = weather['weather'][0]['main']
        
        # Determine weather category
        if temp >= self.temp_thresholds['extreme_heat']:
            category = 'extreme_heat'
        elif 'sand' in conditions.lower() or 'dust' in conditions.lower():
            category = 'sandstorm'
        elif temp <= self.temp_thresholds['cool']:
            category = 'pleasant'
        else:
            category = 'hot'
        
        template = self.weather_templates.get(category, self.weather_templates['hot'])
        
        return {
            'temperature': temp,
            'conditions': conditions,
            'category': category,
            'content_suggestions': template['promos'],
            'focus_areas': template['focus'],
            'hashtags': template['hashtags'],
            'emoji_suggestions': self._get_weather_emojis(category)
        }
    
    def _get_weather_emojis(self, category: str) -> List[str]:
        """Get relevant emojis for weather category"""
        emoji_map = {
            'extreme_heat': ['🥵', '☀️', '🔥', '🧊', '❄️'],
            'sandstorm': ['🌪️', '😷', '🏠', '🚗'],
            'pleasant': ['😊', '🌤️', '🌿', '☕'],
            'hot': ['☀️', '😎', '🥤', '🍹']
        }
        return emoji_map.get(category, ['☀️'])
```

## 4. Quick Implementation Tasks

### 4.1 Update AI Service with Templates
```python
# In services/ai_service.py, add:

def generate_from_template(self, template_name: str, variables: Dict) -> Dict:
    """Generate content using predefined templates"""
    template_service = get_template_service()
    
    # Get template
    template = template_service.get_template_by_name(template_name)
    
    # Generate base content
    base_content = template_service.generate_from_template(template_name, variables)
    
    # Enhance with AI
    enhanced = self.enhance_content(
        base_content,
        enhancement_type='platform_optimization'
    )
    
    # Add weather context if applicable
    weather_service = get_weather_content_service()
    weather_suggestions = weather_service.generate_weather_content(
        variables.get('restaurant_type', 'general')
    )
    
    return {
        'content': enhanced,
        'template_used': template_name,
        'weather_context': weather_suggestions,
        'posting_time': self._get_optimal_time(template_name)
    }
```

### 4.2 Frontend Quick Add Components
```typescript
// components/TemplateSelector.tsx
interface Template {
  name: string;
  category: string;
  preview: string;
  variables: string[];
}

const TemplateSelector: React.FC = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selected, setSelected] = useState<string>('');
  
  const categories = [
    'Daily Specials',
    'Weekend Offers', 
    'Delivery Promos',
    'Ramadan',
    'Weather-Based'
  ];
  
  return (
    <div className="template-selector">
      <CategoryTabs categories={categories} />
      <TemplateGrid templates={templates} onSelect={setSelected} />
      <VariableInputs template={selected} />
      <PreviewPane />
    </div>
  );
};
```

## 5. Testing Phase 1 Features

### 5.1 Test Prayer Time Scheduling
```python
# test_prayer_scheduling.py
def test_prayer_aware_scheduling():
    scheduler = PrayerAwareScheduler()
    
    # Test during prayer time
    prayer_time = datetime(2025, 7, 1, 12, 15)  # Dhuhr time
    assert scheduler.is_prayer_time(prayer_time) == True
    
    # Test outside prayer time
    safe_time = datetime(2025, 7, 1, 10, 0)
    assert scheduler.is_prayer_time(safe_time) == False
    
    # Test next available slot
    next_slot = scheduler.get_next_available_slot(prayer_time)
    assert next_slot > prayer_time + timedelta(minutes=15)
```

## Next Steps

1. **Week 1**: Implement template service and basic templates
2. **Week 2**: Add prayer time scheduling and weather integration
3. **Week 3**: Create frontend components
4. **Week 4**: Test with pilot restaurants

This Phase 1 implementation will immediately provide value to F&B clients with practical, Kuwait-specific features!