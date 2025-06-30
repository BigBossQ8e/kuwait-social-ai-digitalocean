"""Kuwait-specific validators for compliance"""
import re
from datetime import datetime
import pytz

class KuwaitValidators:
    """Validators for Kuwait compliance requirements"""
    
    @staticmethod
    def validate_kuwait_phone(phone):
        """
        Validate Kuwait phone number
        Accepts: +965 XXXX XXXX format
        Valid prefixes: 5, 6, 9 (mobile), 2 (landline)
        """
        # Remove spaces and dashes
        phone = re.sub(r'[\s\-]', '', phone)
        
        # Check format
        kuwait_mobile_regex = r'^\+965[569]\d{7}$'
        kuwait_landline_regex = r'^\+9652\d{7}$'
        
        return bool(re.match(kuwait_mobile_regex, phone) or re.match(kuwait_landline_regex, phone))
    
    @staticmethod
    def validate_commercial_license(license_number):
        """
        Validate Kuwait commercial license format
        Format: XXXXX/YYYY (5 digits / 4 digit year)
        """
        license_regex = r'^\d{5}/\d{4}$'
        if not re.match(license_regex, license_number):
            return False
        
        # Check if year is reasonable (between 1990 and current year + 1)
        year = int(license_number.split('/')[1])
        current_year = datetime.now().year
        return 1990 <= year <= current_year + 1
    
    @staticmethod
    def validate_civil_id(civil_id):
        """
        Validate Kuwait Civil ID
        Format: 12 digits
        First digit: 1 (born before 2000) or 2 (born 2000 or after)
        """
        if not re.match(r'^\d{12}$', civil_id):
            return False
        
        # Basic validation - first digit should be 1 or 2
        return civil_id[0] in ['1', '2']
    
    @staticmethod
    def validate_paci_address(area, block, street, building):
        """
        Validate PACI address format
        All should be numeric except area which can have text
        """
        try:
            # Block, street, and building should be numeric
            int(block)
            int(street)
            # Building can have letters (e.g., "12A")
            if not re.match(r'^[0-9A-Za-z]+$', building):
                return False
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_prohibited_content(content):
        """
        Check if content contains prohibited terms for Kuwait
        Returns: (is_prohibited, list_of_found_terms)
        """
        # Prohibited terms in English and Arabic
        prohibited_terms = {
            # Alcohol
            'alcohol', 'beer', 'wine', 'vodka', 'whiskey', 'liquor',
            'كحول', 'خمر', 'بيرة', 'نبيذ', 'ويسكي',
            # Gambling
            'gambling', 'casino', 'betting', 'lottery',
            'قمار', 'كازينو', 'مراهنات', 'يانصيب',
            # Dating
            'dating', 'hookup', 'singles',
            'مواعدة', 'تعارف',
            # Inappropriate
            'nude', 'adult', 'xxx',
            'عاري', 'إباحي'
        }
        
        content_lower = content.lower()
        found_terms = []
        
        for term in prohibited_terms:
            if term in content_lower:
                found_terms.append(term)
        
        return len(found_terms) > 0, found_terms
    
    @staticmethod
    def get_prayer_times(date=None):
        """
        Get prayer times for Kuwait City
        This is a simplified version - in production, use an API like Aladhan
        """
        if date is None:
            date = datetime.now(pytz.timezone('Asia/Kuwait'))
        
        # Approximate prayer times for Kuwait (varies by date)
        prayer_times = {
            'Fajr': '04:30',
            'Dhuhr': '11:45',
            'Asr': '15:00',
            'Maghrib': '17:30',
            'Isha': '19:00'
        }
        
        # Friday prayer is special
        if date.weekday() == 4:  # Friday
            prayer_times['Jummah'] = '12:30'
        
        return prayer_times
    
    @staticmethod
    def is_during_prayer_time(time=None, buffer_minutes=15):
        """
        Check if current time is during prayer time (with buffer)
        """
        if time is None:
            time = datetime.now(pytz.timezone('Asia/Kuwait'))
        
        prayer_times = KuwaitValidators.get_prayer_times(time.date())
        current_time = time.time()
        
        for prayer, prayer_time_str in prayer_times.items():
            prayer_hour, prayer_minute = map(int, prayer_time_str.split(':'))
            prayer_datetime = time.replace(hour=prayer_hour, minute=prayer_minute, second=0)
            
            # Check if within buffer before or after prayer time
            time_diff = abs((time - prayer_datetime).total_seconds() / 60)
            if time_diff <= buffer_minutes:
                return True, prayer
        
        return False, None
    
    @staticmethod
    def is_kuwait_holiday(date=None):
        """
        Check if date is a Kuwait public holiday
        """
        if date is None:
            date = datetime.now(pytz.timezone('Asia/Kuwait')).date()
        
        # Fixed holidays
        fixed_holidays = [
            (2, 25),  # National Day
            (2, 26),  # Liberation Day
            (1, 1),   # New Year (for international businesses)
        ]
        
        for month, day in fixed_holidays:
            if date.month == month and date.day == day:
                return True
        
        # Islamic holidays would need a lunar calendar API
        # For now, return False
        return False
    
    @staticmethod
    def format_kuwait_phone_display(phone):
        """
        Format phone for display: +965 5XXX XXXX
        """
        if phone.startswith('+965'):
            phone_digits = phone[4:]
            if len(phone_digits) == 8:
                return f"+965 {phone_digits[:4]} {phone_digits[4:]}"
        return phone
    
    @staticmethod
    def validate_business_name_arabic(name):
        """
        Check if business name contains Arabic characters
        Kuwait businesses often require Arabic name
        """
        arabic_pattern = r'[\u0600-\u06FF]'
        return bool(re.search(arabic_pattern, name))