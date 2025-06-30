"""
F&B (Food & Beverage) specific configuration for Kuwait Social AI
"""

# F&B Business Types
F&B_BUSINESS_TYPES = [
    'restaurant',
    'cafe',
    'coffee_shop',
    'bakery',
    'food_truck',
    'catering',
    'cloud_kitchen',
    'fine_dining',
    'casual_dining',
    'fast_food',
    'dessert_shop',
    'juice_bar',
    'shisha_cafe'
]

# Kuwait Popular Cuisines
KUWAIT_CUISINES = {
    'local': ['Kuwaiti', 'Gulf', 'Khaleeji'],
    'middle_eastern': ['Lebanese', 'Syrian', 'Palestinian', 'Egyptian', 'Turkish'],
    'asian': ['Indian', 'Pakistani', 'Japanese', 'Chinese', 'Thai', 'Filipino'],
    'western': ['Italian', 'American', 'French', 'Mexican'],
    'fusion': ['Asian Fusion', 'Modern Arabic', 'International']
}

# F&B Specific Hashtags
F&B_HASHTAGS = {
    'general': [
        '#KuwaitFood', '#Q8Food', '#KuwaitRestaurants', '#Q8Restaurants',
        '#KuwaitFoodies', '#مطاعم_الكويت', '#طعام_الكويت', '#Q8Eats',
        '#KuwaitDining', '#FoodieKuwait', '#KuwaitCafe', '#Q8Cafe'
    ],
    'delivery': [
        '#KuwaitDelivery', '#Q8Delivery', '#توصيل_الكويت',
        '#OrderOnline', '#FoodDeliveryKuwait'
    ],
    'halal': [
        '#HalalFood', '#HalalKuwait', '#حلال', '#HalalRestaurant'
    ],
    'trending': [
        '#InstaFoodKuwait', '#Q8Foodie', '#KuwaitEats',
        '#FoodBloggerKuwait', '#RestaurantKuwait'
    ],
    'ramadan': [
        '#RamadanKuwait', '#IftarKuwait', '#SuhoorKuwait',
        '#رمضان_الكويت', '#افطار', '#سحور'
    ]
}

# F&B Keywords
F&B_KEYWORDS = {
    'must_mention': ['halal', 'family-friendly', 'air-conditioned'],
    'quality': ['fresh', 'authentic', 'homemade', 'premium', 'organic'],
    'service': ['delivery', 'dine-in', 'takeaway', 'catering', 'reservation'],
    'atmosphere': ['cozy', 'modern', 'traditional', 'outdoor seating', 'private dining'],
    'dietary': ['vegan', 'vegetarian', 'gluten-free', 'sugar-free', 'keto-friendly']
}

# Meal Times in Kuwait
KUWAIT_MEAL_TIMES = {
    'breakfast': {'start': '06:00', 'end': '11:00', 'days': 'all'},
    'brunch': {'start': '10:00', 'end': '14:00', 'days': 'friday,saturday'},
    'lunch': {'start': '12:00', 'end': '15:00', 'days': 'all'},
    'afternoon_tea': {'start': '16:00', 'end': '18:00', 'days': 'all'},
    'dinner': {'start': '19:00', 'end': '23:00', 'days': 'all'},
    'late_night': {'start': '23:00', 'end': '02:00', 'days': 'all'},
    'iftar': {'seasonal': 'ramadan', 'time': 'sunset'},
    'suhoor': {'seasonal': 'ramadan', 'start': '02:00', 'end': '04:00'}
}

# Popular F&B Areas in Kuwait
KUWAIT_F&B_AREAS = [
    'Kuwait City', 'Salmiya', 'Hawally', 'Jabriya', 'Ahmadi',
    'Mahboula', 'Mangaf', 'Fahaheel', 'Avenues Mall', 'Marina Mall',
    'Al Kout Mall', 'The Gate Mall', '360 Mall'
]

# F&B Content Templates
F&B_TEMPLATES = {
    'announcements': {
        'new_item': "🎉 NEW: {item_name}! {description} Only {price} KWD. Try it today!",
        'opening_hours': "📍 We're open {days} from {open_time} to {close_time}. See you soon!",
        'delivery': "🚗 Craving {cuisine}? We deliver! Order now: {contact}",
    },
    'promotions': {
        'discount': "🔥 {discount}% OFF on {items}! Valid {duration}. T&C apply.",
        'combo': "👨‍👩‍👧‍👦 Family Combo: {items} for only {price} KWD!",
        'happy_hour': "⏰ Happy Hour {time}! Special prices on selected items.",
    },
    'engagement': {
        'question': "What's your favorite {category} from our menu? Comment below! 👇",
        'poll': "Help us decide tomorrow's special! React with: 🍕 for {option1} 🍔 for {option2}",
        'review': "Thank you {customer} for this amazing review! ❤️ {review_snippet}",
    }
}

# Emojis for F&B
F&B_EMOJIS = {
    'general': ['🍽️', '🍴', '👨‍🍳', '😋', '🤤'],
    'breakfast': ['☕', '🥐', '🍳', '🥞', '🧇'],
    'lunch_dinner': ['🍖', '🍗', '🥘', '🍛', '🍝'],
    'desserts': ['🍰', '🧁', '🍪', '🍩', '🍨'],
    'drinks': ['🥤', '🧃', '☕', '🍵', '🥛'],
    'delivery': ['🚗', '📱', '📦', '🛵', '⏰'],
    'halal': ['✅', '👍', '💯', '☪️'],
    'special': ['🌟', '✨', '🎉', '🔥', '💎']
}

# Price Ranges (in KWD)
PRICE_CATEGORIES = {
    'budget': {'symbol': '💰', 'range': '1-5 KWD'},
    'moderate': {'symbol': '💰💰', 'range': '5-15 KWD'},
    'premium': {'symbol': '💰💰💰', 'range': '15-30 KWD'},
    'luxury': {'symbol': '💰💰💰💰', 'range': '30+ KWD'}
}

# Seasonal F&B Events
F&B_SEASONAL_EVENTS = {
    'ramadan': {
        'focus': 'Iftar buffets, Suhoor specials, family packages',
        'keywords': ['ramadan kareem', 'iftar', 'suhoor', 'family gathering']
    },
    'summer': {
        'focus': 'Cold beverages, ice cream, indoor dining with AC',
        'keywords': ['beat the heat', 'summer special', 'refreshing', 'ice cold']
    },
    'national_day': {
        'focus': 'Kuwaiti traditional dishes, patriotic themes',
        'keywords': ['kuwait national day', 'hala february', 'kuwaiti cuisine']
    },
    'eid': {
        'focus': 'Celebration meals, sweets, family gatherings',
        'keywords': ['eid mubarak', 'celebration', 'special menu']
    }
}