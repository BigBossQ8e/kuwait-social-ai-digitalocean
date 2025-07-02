"""
Kuwaiti NLP Service for dialect processing and localization
"""
import re
from typing import Dict, List, Optional


class KuwaitiNLPService:
    """Service for processing Kuwaiti dialect and cultural context"""
    
    def __init__(self):
        # Common Kuwaiti to Modern Standard Arabic mappings
        self.dialect_mappings = {
            # Greetings
            'شلونك': 'كيف حالك',
            'شلونج': 'كيف حالك',  # feminine
            'شخبارك': 'ما أخبارك',
            'هلا': 'أهلا',
            'حياك': 'أهلا وسهلا',
            
            # Common words
            'وايد': 'كثير',
            'شوي': 'قليل',
            'چذي': 'هكذا',
            'شنو': 'ماذا',
            'ليش': 'لماذا',
            'وين': 'أين',
            'متى': 'متى',
            'چم': 'كم',
            'منو': 'من',
            'شلون': 'كيف',
            
            # Expressions
            'ماكو': 'لا يوجد',
            'اكو': 'يوجد',
            'خوش': 'جيد',
            'زين': 'حسن',
            'مو زين': 'ليس جيد',
            'يبا': 'يريد',
            'ما يبا': 'لا يريد',
            
            # Food terms (keep as is for cultural context)
            # 'مجبوس': 'مجبوس',
            # 'هريس': 'هريس',
            # 'كرك': 'شاي كرك',
        }
        
        # Kuwaiti-specific emojis and their context
        self.emoji_context = {
            '🇰🇼': 'kuwait',
            '🕌': 'mosque/prayer',
            '☕': 'karak/coffee',
            '🌴': 'palm/traditional',
            '🐪': 'desert/heritage',
            '🌊': 'sea/gulf'
        }
        
        # Common Kuwaiti expressions for sentiment
        self.positive_expressions = [
            'الله يعطيك العافية',
            'تسلم',
            'يعطيك العافية',
            'ما قصرت',
            'خوش شغل',
            'عاش',
            'الله يحفظك'
        ]
        
        self.negative_expressions = [
            'خايس',
            'مو زين',
            'ما يسوى',
            'للأسف',
            'ما ينفع'
        ]
        
    def process_text(self, text: str, dialect: str = 'auto', 
                    custom_context: Optional[Dict] = None) -> str:
        """
        Process Kuwaiti dialect text
        
        Args:
            text: Input text
            dialect: 'auto', 'kuwaiti', 'gulf', 'msa'
            custom_context: Additional context mappings
            
        Returns:
            Processed text
        """
        if not text:
            return text
            
        processed = text
        
        # Detect dialect if auto
        if dialect == 'auto':
            dialect = self._detect_dialect(text)
        
        # Apply dialect processing
        if dialect in ['kuwaiti', 'gulf']:
            processed = self._apply_dialect_mappings(processed, custom_context)
        
        # Normalize text
        processed = self._normalize_arabic(processed)
        
        return processed
    
    def _detect_dialect(self, text: str) -> str:
        """Detect if text contains Kuwaiti dialect"""
        kuwaiti_indicators = ['شلونك', 'وايد', 'چذي', 'شنو', 'اكو', 'ماكو']
        
        for indicator in kuwaiti_indicators:
            if indicator in text:
                return 'kuwaiti'
        
        return 'msa'  # Default to Modern Standard Arabic
    
    def _apply_dialect_mappings(self, text: str, 
                               custom_context: Optional[Dict] = None) -> str:
        """Apply dialect to MSA mappings"""
        # Apply custom mappings first
        if custom_context:
            for dialect_word, msa_word in custom_context.items():
                text = text.replace(dialect_word, msa_word)
        
        # Apply default mappings
        for kuwaiti, msa in self.dialect_mappings.items():
            # Use word boundaries to avoid partial replacements
            pattern = r'\b' + re.escape(kuwaiti) + r'\b'
            text = re.sub(pattern, msa, text)
        
        return text
    
    def _normalize_arabic(self, text: str) -> str:
        """Normalize Arabic text"""
        # Normalize Arabic letters
        text = re.sub(r'[إأآا]', 'ا', text)
        text = re.sub(r'[ىي]', 'ي', text)
        text = re.sub(r'ة', 'ه', text)
        
        # Remove diacritics
        arabic_diacritics = re.compile(r'[\u064B-\u0652\u0670\u0640]')
        text = arabic_diacritics.sub('', text)
        
        return text
    
    def extract_cultural_context(self, text: str) -> Dict:
        """Extract Kuwaiti cultural context from text"""
        context = {
            'has_greetings': False,
            'has_food_terms': False,
            'has_locations': False,
            'sentiment': 'neutral',
            'cultural_elements': []
        }
        
        # Check for greetings
        greetings = ['هلا', 'حياك', 'شلونك', 'شخبارك']
        if any(greeting in text for greeting in greetings):
            context['has_greetings'] = True
            context['cultural_elements'].append('greeting')
        
        # Check for food terms
        food_terms = ['مجبوس', 'هريس', 'مطبق', 'كرك', 'درابيل']
        if any(food in text for food in food_terms):
            context['has_food_terms'] = True
            context['cultural_elements'].append('food')
        
        # Check for locations
        locations = ['الأفنيوز', 'السالمية', 'حولي', 'الجهراء']
        if any(location in text for location in locations):
            context['has_locations'] = True
            context['cultural_elements'].append('location')
        
        # Analyze sentiment
        if any(expr in text for expr in self.positive_expressions):
            context['sentiment'] = 'positive'
        elif any(expr in text for expr in self.negative_expressions):
            context['sentiment'] = 'negative'
        
        return context
    
    def generate_localized_response(self, prompt: str, context: Dict) -> str:
        """Generate a response considering Kuwaiti context"""
        # Add cultural awareness to the prompt
        cultural_prompt = prompt
        
        if context.get('has_greetings'):
            cultural_prompt = f"Respond with appropriate Kuwaiti greeting. {prompt}"
        
        if context.get('has_food_terms'):
            cultural_prompt = f"Consider Kuwaiti cuisine context. {prompt}"
        
        if context.get('sentiment') == 'positive':
            cultural_prompt = f"Maintain positive tone with Kuwaiti expressions. {prompt}"
        
        return cultural_prompt
    
    def add_cultural_flavor(self, text: str, style: str = 'formal') -> str:
        """Add Kuwaiti cultural elements to text"""
        if style == 'casual':
            # Add casual Kuwaiti touches
            if not any(greeting in text for greeting in ['هلا', 'حياك']):
                text = f"هلا والله! {text}"
            
            # Add common endings
            if not text.endswith(('الله يعطيك العافية', 'تسلم')):
                text = f"{text} 🇰🇼"
        
        elif style == 'formal':
            # Keep formal but add light cultural touch
            if 'شكرا' in text:
                text = text.replace('شكرا', 'يعطيك العافية')
        
        return text