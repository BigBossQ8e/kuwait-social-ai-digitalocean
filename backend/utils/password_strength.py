"""
Advanced Password Strength Assessment using zxcvbn
Provides comprehensive password security evaluation
"""

import zxcvbn
from typing import Dict, List, Tuple, Optional
import re


class PasswordStrengthChecker:
    """
    Advanced password strength checker using zxcvbn algorithm
    Provides detailed feedback and suggestions for password improvement
    """
    
    # Minimum requirements (can be customized per deployment)
    MIN_LENGTH = 8
    MIN_SCORE = 2  # zxcvbn score: 0-4 (2 = fair, 3 = good, 4 = strong)
    
    # Kuwait-specific common passwords to avoid
    KUWAIT_COMMON_PASSWORDS = [
        'kuwait123', 'q8q8q8', 'kuwait2024', 'password123',
        'admin123', '12345678', 'qwerty123', 'welcome123',
        'kuwait@123', 'q8admin', 'kuwait1234', 'password1'
    ]
    
    # Common Arabic passwords (transliterated)
    ARABIC_COMMON_PASSWORDS = [
        'allah123', 'inshallah', 'mashallah', 'bismillah',
        'salam123', 'habibi123', 'kuwait', 'q8'
    ]
    
    def __init__(self, 
                 min_length: int = None,
                 min_score: int = None,
                 custom_dictionary: List[str] = None):
        """
        Initialize password strength checker
        
        Args:
            min_length: Minimum password length (default: 8)
            min_score: Minimum zxcvbn score (default: 2)
            custom_dictionary: Additional words to check against
        """
        self.min_length = min_length or self.MIN_LENGTH
        self.min_score = min_score or self.MIN_SCORE
        
        # Build custom dictionary
        self.custom_dictionary = []
        self.custom_dictionary.extend(self.KUWAIT_COMMON_PASSWORDS)
        self.custom_dictionary.extend(self.ARABIC_COMMON_PASSWORDS)
        if custom_dictionary:
            self.custom_dictionary.extend(custom_dictionary)
    
    def check_password(self, 
                      password: str, 
                      user_inputs: List[str] = None) -> Dict:
        """
        Comprehensive password strength check
        
        Args:
            password: Password to check
            user_inputs: Related user data (username, email, company name, etc.)
                        to check if password contains this info
        
        Returns:
            Dict with strength assessment and recommendations
        """
        result = {
            'is_valid': False,
            'score': 0,
            'strength': 'too weak',
            'estimated_crack_time': 'instant',
            'warnings': [],
            'suggestions': [],
            'feedback': '',
            'contains_user_info': False,
            'meets_requirements': {}
        }
        
        # Basic length check
        if len(password) < self.min_length:
            result['warnings'].append(f'Password must be at least {self.min_length} characters long')
            result['meets_requirements']['length'] = False
        else:
            result['meets_requirements']['length'] = True
        
        # Build user dictionary for zxcvbn
        user_dict = self.custom_dictionary.copy()
        if user_inputs:
            # Add user inputs and their variations
            for input_str in user_inputs:
                if input_str:
                    user_dict.append(input_str.lower())
                    # Add without spaces
                    user_dict.append(input_str.replace(' ', '').lower())
                    # Add with numbers
                    user_dict.extend([
                        f"{input_str}123",
                        f"{input_str}2024",
                        f"{input_str}@123"
                    ])
        
        # Run zxcvbn analysis
        analysis = zxcvbn.zxcvbn(password, user_inputs=user_dict)
        
        # Extract results
        result['score'] = analysis['score']
        result['estimated_crack_time'] = self._format_crack_time(analysis)
        
        # Set strength label
        strength_labels = {
            0: 'too weak',
            1: 'weak',
            2: 'fair',
            3: 'good',
            4: 'strong'
        }
        result['strength'] = strength_labels.get(analysis['score'], 'unknown')
        
        # Check if meets minimum score
        if analysis['score'] >= self.min_score:
            result['is_valid'] = True
        else:
            result['warnings'].append(
                f'Password strength is {result["strength"]}. '
                f'Please create a stronger password.'
            )
        
        # Process feedback from zxcvbn
        feedback = analysis.get('feedback', {})
        
        # Add warnings
        if feedback.get('warning'):
            result['warnings'].append(feedback['warning'])
        
        # Add suggestions
        if feedback.get('suggestions'):
            result['suggestions'].extend(feedback['suggestions'])
        
        # Check for specific patterns
        self._check_patterns(password, result)
        
        # Check if password contains user information
        if user_inputs:
            self._check_user_info(password, user_inputs, result)
        
        # Add specific recommendations based on score
        if analysis['score'] < 3:
            result['suggestions'].extend(self._get_improvement_suggestions(password, analysis))
        
        # Create comprehensive feedback message
        result['feedback'] = self._create_feedback_message(result)
        
        return result
    
    def _format_crack_time(self, analysis: Dict) -> str:
        """Format crack time estimate in human-readable form"""
        crack_times = analysis.get('crack_times_display', {})
        
        # Use offline slow hashing as the metric (most realistic for stored passwords)
        time_estimate = crack_times.get('offline_slow_hashing_1e4_per_second', 'unknown')
        
        return time_estimate
    
    def _check_patterns(self, password: str, result: Dict):
        """Check for specific required patterns"""
        checks = {
            'uppercase': (r'[A-Z]', 'Password should contain at least one uppercase letter'),
            'lowercase': (r'[a-z]', 'Password should contain at least one lowercase letter'),
            'number': (r'[0-9]', 'Password should contain at least one number'),
            'special': (r'[!@#$%^&*(),.?":{}|<>]', 'Password should contain at least one special character')
        }
        
        for check_name, (pattern, message) in checks.items():
            if re.search(pattern, password):
                result['meets_requirements'][check_name] = True
            else:
                result['meets_requirements'][check_name] = False
                if result['score'] < 3:  # Only suggest for weak passwords
                    result['suggestions'].append(message)
    
    def _check_user_info(self, password: str, user_inputs: List[str], result: Dict):
        """Check if password contains user information"""
        password_lower = password.lower()
        
        for user_input in user_inputs:
            if user_input and len(user_input) > 2:
                # Check if user input is in password
                if user_input.lower() in password_lower:
                    result['contains_user_info'] = True
                    result['warnings'].append(
                        'Password contains personal information. '
                        'Avoid using your name, email, or company name in passwords.'
                    )
                    break
                
                # Check if password is based on user input with common modifications
                common_mods = ['123', '!', '@', '2024', '2023']
                for mod in common_mods:
                    if password_lower == f"{user_input.lower()}{mod}":
                        result['contains_user_info'] = True
                        result['warnings'].append(
                            'Password is too similar to your personal information.'
                        )
                        break
    
    def _get_improvement_suggestions(self, password: str, analysis: Dict) -> List[str]:
        """Get specific suggestions for password improvement"""
        suggestions = []
        
        # Length suggestion
        if len(password) < 12:
            suggestions.append('Consider using a longer password (12+ characters)')
        
        # Pattern suggestions based on what's in the password
        sequence_data = analysis.get('sequence', [])
        for seq in sequence_data:
            pattern = seq.get('pattern', '')
            if pattern == 'dictionary':
                suggestions.append('Avoid common dictionary words')
            elif pattern == 'sequence':
                suggestions.append('Avoid sequential characters (like "abc" or "123")')
            elif pattern == 'repeat':
                suggestions.append('Avoid repeated characters')
            elif pattern == 'date':
                suggestions.append('Avoid using dates in your password')
        
        # Suggest passphrase if very weak
        if analysis['score'] <= 1:
            suggestions.append(
                'Consider using a passphrase: combine 4-5 random words '
                'with numbers and symbols (e.g., "Coffee@Desert7Sunset!Moon")'
            )
        
        return suggestions
    
    def _create_feedback_message(self, result: Dict) -> str:
        """Create a comprehensive feedback message"""
        if result['is_valid']:
            if result['score'] >= 4:
                return f"Excellent! Your password is {result['strength']} and would take {result['estimated_crack_time']} to crack."
            else:
                return f"Your password is {result['strength']} and meets minimum requirements. Estimated crack time: {result['estimated_crack_time']}."
        else:
            issues = []
            if not result['meets_requirements'].get('length', True):
                issues.append(f"at least {self.min_length} characters")
            if result['score'] < self.min_score:
                issues.append("stronger complexity")
            
            return f"Password is {result['strength']}. Please create a password with {' and '.join(issues)}."
    
    def generate_password_hints(self) -> List[str]:
        """Generate helpful password creation hints"""
        return [
            "Use a mix of uppercase and lowercase letters, numbers, and symbols",
            "Make it at least 12 characters long for better security",
            "Avoid common words, personal information, or keyboard patterns",
            "Consider using a memorable passphrase with random words",
            "Don't reuse passwords from other accounts",
            "Avoid Kuwait-specific common passwords like 'kuwait123' or 'q8q8q8'"
        ]
    
    def validate_password_match(self, password: str, confirm_password: str) -> Tuple[bool, Optional[str]]:
        """Validate that passwords match"""
        if password != confirm_password:
            return False, "Passwords do not match"
        return True, None


# Convenience function for use in validators
def check_password_strength(password: str, 
                          user_inputs: List[str] = None,
                          min_score: int = 2) -> Dict:
    """
    Quick password strength check
    
    Args:
        password: Password to check
        user_inputs: User-related data to check against
        min_score: Minimum acceptable score (0-4)
    
    Returns:
        Dict with strength assessment
    """
    checker = PasswordStrengthChecker(min_score=min_score)
    return checker.check_password(password, user_inputs)


# Integration with existing validator
def validate_password_enhanced(password: str, 
                             username: str = None,
                             email: str = None,
                             company_name: str = None) -> Optional[str]:
    """
    Enhanced password validation for use in Marshmallow schemas
    
    Returns:
        Error message if invalid, None if valid
    """
    # Build user inputs list
    user_inputs = []
    if username:
        user_inputs.append(username)
    if email:
        # Add email username part
        user_inputs.append(email.split('@')[0])
    if company_name:
        user_inputs.append(company_name)
    
    # Check password strength
    result = check_password_strength(password, user_inputs)
    
    if not result['is_valid']:
        # Return the most important error message
        if result['warnings']:
            return result['warnings'][0]
        else:
            return result['feedback']
    
    return None