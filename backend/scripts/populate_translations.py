#!/usr/bin/env python3
"""
Script to populate the database with initial translations from JSON files
"""

import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import from the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_factory import create_app
from extensions import db
from models.translation import Translation, TranslationHistory
from models.user import User

def load_json_translations(file_path):
    """Load translations from a JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def process_nested(obj, prefix='', locale='en', category='common'):
    """Process nested translation objects and return flat list"""
    translations = []
    
    for key, value in obj.items():
        full_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict) and not any(isinstance(v, str) for v in value.values()):
            # This is a nested object, recurse
            new_category = key if not prefix else category
            translations.extend(process_nested(value, full_key, locale, new_category))
        elif isinstance(value, list):
            # Handle arrays by storing as JSON string
            translations.append({
                'key': full_key,
                'locale': locale,
                'value': json.dumps(value, ensure_ascii=False),
                'category': category
            })
        else:
            # This is a leaf value
            translations.append({
                'key': full_key,
                'locale': locale,
                'value': str(value),
                'category': category
            })
    
    return translations

def populate_translations():
    """Populate the database with translations"""
    app = create_app('development')
    
    with app.app_context():
        # Get the admin user (assuming ID 1 is admin)
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            print("No admin user found. Creating default admin user for translations.")
            admin_user = User(
                id=1,
                email='admin@kwtsocial.com',
                role='admin'
            )
            # Note: In production, you'd set a proper password
        
        # Path to translation files
        frontend_path = Path(__file__).parent.parent.parent / 'frontend-react'
        en_file = frontend_path / 'src' / 'i18n' / 'locales' / 'en' / 'translation.json'
        ar_file = frontend_path / 'src' / 'i18n' / 'locales' / 'ar' / 'translation.json'
        
        # Load translations
        print("Loading English translations...")
        en_translations = load_json_translations(en_file)
        en_flat = process_nested(en_translations, '', 'en')
        
        print("Loading Arabic translations...")
        ar_translations = load_json_translations(ar_file)
        ar_flat = process_nested(ar_translations, '', 'ar')
        
        # Clear existing translations (optional - comment out if you want to keep existing)
        print("Clearing existing translations...")
        Translation.query.delete()
        db.session.commit()
        
        # Insert translations
        print("Inserting translations...")
        inserted_count = 0
        
        # Process English translations
        for trans in en_flat:
            try:
                translation = Translation(
                    key=trans['key'],
                    locale=trans['locale'],
                    value=trans['value'],
                    category=trans['category'],
                    created_by=admin_user.id if admin_user else None
                )
                db.session.add(translation)
                inserted_count += 1
            except Exception as e:
                print(f"Error inserting {trans['key']} (en): {e}")
        
        # Process Arabic translations
        for trans in ar_flat:
            try:
                translation = Translation(
                    key=trans['key'],
                    locale=trans['locale'],
                    value=trans['value'],
                    category=trans['category'],
                    created_by=admin_user.id if admin_user else None
                )
                db.session.add(translation)
                inserted_count += 1
            except Exception as e:
                print(f"Error inserting {trans['key']} (ar): {e}")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\nSuccessfully inserted {inserted_count} translations!")
        
        # Show summary
        total_en = Translation.query.filter_by(locale='en').count()
        total_ar = Translation.query.filter_by(locale='ar').count()
        categories = db.session.query(Translation.category).distinct().all()
        
        print(f"\nSummary:")
        print(f"- English translations: {total_en}")
        print(f"- Arabic translations: {total_ar}")
        print(f"- Categories: {', '.join([c[0] for c in categories if c[0]])}")

if __name__ == '__main__':
    populate_translations()