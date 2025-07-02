#!/usr/bin/env python3
"""Test Arabic content generation and support"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.content_generator import ContentGenerator
from utils.validators import validate_content_for_kuwait, validate_hashtags

def test_arabic_translation():
    """Test Arabic translation functionality"""
    print("=== Testing Arabic Translation ===\n")
    
    try:
        generator = ContentGenerator()
        
        test_texts = [
            "Welcome to our restaurant!",
            "Special offer: 20% discount on all meals",
            "Happy Friday! Enjoy family time with our special lunch",
            "Ramadan Mubarak! Check our Iftar menu"
        ]
        
        for text in test_texts:
            print(f"English: {text}")
            arabic = generator._translate_to_arabic(text)
            if arabic:
                print(f"Arabic: {arabic}")
                print("✅ Translation successful\n")
            else:
                print("❌ Translation failed\n")
                
    except Exception as e:
        print(f"❌ Error during translation test: {e}\n")

def test_bilingual_content_generation():
    """Test bilingual content generation"""
    print("=== Testing Bilingual Content Generation ===\n")
    
    try:
        generator = ContentGenerator()
        
        prompts = [
            {
                "prompt": "Create a post for a Friday lunch special at a Kuwaiti restaurant featuring Majboos",
                "platform": "instagram",
                "tone": "friendly"
            },
            {
                "prompt": "Announce Ramadan Iftar buffet at 15 KWD per person",
                "platform": "instagram", 
                "tone": "respectful"
            },
            {
                "prompt": "Promote a new coffee shop opening in Salmiya",
                "platform": "instagram",
                "tone": "exciting"
            }
        ]
        
        for test in prompts:
            print(f"Prompt: {test['prompt']}")
            print("-" * 50)
            
            result = generator.generate_content(
                prompt=test['prompt'],
                include_arabic=True,
                platform=test['platform'],
                tone=test['tone'],
                include_hashtags=True
            )
            
            print(f"English Caption:\n{result.get('caption_en', 'N/A')}\n")
            print(f"Arabic Caption:\n{result.get('caption_ar', 'N/A')}\n")
            print(f"Hashtags: {', '.join(result.get('hashtags', []))}\n")
            
            if result.get('caption_ar'):
                print("✅ Bilingual content generated successfully")
            else:
                print("⚠️  Arabic content not generated")
                
            print("=" * 70 + "\n")
            
    except Exception as e:
        print(f"❌ Error during content generation: {e}\n")

def test_arabic_hashtags():
    """Test Arabic hashtag validation"""
    print("=== Testing Arabic Hashtag Support ===\n")
    
    arabic_hashtags = [
        "#مطاعم_الكويت",
        "#رمضان_كريم", 
        "#القهوة_العربية",
        "#العيد_الوطني_الكويتي",
        "#جمعة_مباركة"
    ]
    
    mixed_hashtags = arabic_hashtags + ["#kuwaitfood", "#q8restaurants", "#kuwaitcoffee"]
    
    validation = validate_hashtags(mixed_hashtags)
    
    print(f"Total hashtags tested: {len(mixed_hashtags)}")
    print(f"Valid hashtags: {validation['valid_count']}")
    print(f"Invalid hashtags: {len(validation['invalid'])}")
    
    if validation['warnings']:
        print(f"\nWarnings: {', '.join(validation['warnings'])}")
    
    if validation['suggestions']:
        print(f"Suggestions: {', '.join(validation['suggestions'])}")
    
    if validation['valid_count'] == len(mixed_hashtags):
        print("\n✅ All Arabic and English hashtags are valid")
    else:
        print(f"\n❌ Some hashtags failed validation: {validation['invalid']}")

def test_kuwait_content_validation():
    """Test Kuwait-specific content validation"""
    print("\n=== Testing Kuwait Content Validation ===\n")
    
    test_contents = [
        {
            "text": "تفضلوا لتناول أشهى المأكولات الكويتية",
            "expected": True,
            "description": "Valid Arabic content"
        },
        {
            "text": "Enjoy our special pork dishes",
            "expected": False,
            "description": "Invalid - contains prohibited content"
        },
        {
            "text": "Visit us during Ramadan for Iftar",
            "expected": True,
            "description": "Valid Ramadan content"
        },
        {
            "text": "Wine tasting event this Friday",
            "expected": False,
            "description": "Invalid - alcohol reference"
        }
    ]
    
    for test in test_contents:
        result = validate_content_for_kuwait(test['text'])
        
        print(f"Content: {test['text']}")
        print(f"Description: {test['description']}")
        print(f"Validation: {'✅ Valid' if result['is_valid'] else '❌ Invalid'}")
        
        if not result['is_valid']:
            print(f"Issues: {', '.join(result['issues'])}")
        
        if result['warnings']:
            print(f"Warnings: {', '.join(result['warnings'])}")
            
        print("-" * 50)

def test_f_and_b_arabic_content():
    """Test F&B specific Arabic content generation"""
    print("\n=== Testing F&B Arabic Content ===\n")
    
    try:
        generator = ContentGenerator()
        
        # Test F&B templates with Arabic
        fb_prompts = [
            {
                "template": "friday-lunch",
                "prompt": 'Generate a social media post for our dish "Majboos Diyay". It\'s a Friday lunch special. The tone should be warm and inviting, mentioning sharing and tradition for a family gathering in Kuwait.',
                "language": "both"
            },
            {
                "template": "ramadan-offer", 
                "prompt": 'Draft a respectful and warm social media post announcing our special Ramadan menu. Include details like the price: 12 KWD per person and key dishes: Harees, Tashreeb, Luqaimat. End with a traditional blessing like "Ramadan Kareem" or "Mubarak Alaikum Al Shahar".',
                "language": "ar"
            }
        ]
        
        for test in fb_prompts:
            print(f"Template: {test['template']}")
            print(f"Language: {test['language']}")
            print("-" * 50)
            
            # Generate with language preference
            result = generator.generate_content(
                prompt=test['prompt'],
                include_arabic=(test['language'] in ['both', 'ar']),
                platform='instagram',
                tone='warm',
                include_hashtags=True
            )
            
            if test['language'] == 'ar' or test['language'] == 'both':
                if result.get('caption_ar'):
                    print(f"Arabic:\n{result['caption_ar']}\n")
                    print("✅ Arabic content generated")
                else:
                    print("❌ Arabic content missing")
            
            if test['language'] == 'en' or test['language'] == 'both':
                print(f"English:\n{result.get('caption_en', 'N/A')}\n")
            
            print("=" * 70 + "\n")
            
    except Exception as e:
        print(f"❌ Error: {e}\n")

def main():
    print("=== Kuwait Social AI - Arabic Content Support Test ===\n")
    
    # Test 1: Basic translation
    test_arabic_translation()
    
    # Test 2: Bilingual content generation
    test_bilingual_content_generation()
    
    # Test 3: Arabic hashtags
    test_arabic_hashtags()
    
    # Test 4: Kuwait content validation
    test_kuwait_content_validation()
    
    # Test 5: F&B Arabic content
    test_f_and_b_arabic_content()
    
    print("\n✅ Arabic content support testing completed!")

if __name__ == "__main__":
    main()