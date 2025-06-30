from flask import Blueprint, jsonify, request
from models import Translation

translations_bp = Blueprint('translations', __name__)

@translations_bp.route('/translations', methods=['GET'])
def get_translations():
    """Get all translations in the format expected by the frontend"""
    try:
        locale = request.args.get('locale', 'en')
        
        # Get all translations from database
        translations = Translation.query.all()
        
        # Format for frontend consumption
        result = {}
        for trans in translations:
            # Use the appropriate language column
            value = trans.text_en if locale == 'en' else trans.text_ar
            
            # Create nested structure from key (e.g., "common.buttons.submit" -> common: { buttons: { submit: value } })
            keys = trans.key.split('.')
            current = result
            for i, key in enumerate(keys):
                if i == len(keys) - 1:
                    current[key] = value
                else:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
        
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_translations: {str(e)}")
        # Return static fallback data
        if locale == 'ar':
            return jsonify({
                "common": {
                    "appName": "كويت سوشيال AI",
                    "language": "العربية",
                    "buttons": {
                        "login": "تسجيل الدخول",
                        "signup": "إنشاء حساب",
                        "logout": "تسجيل الخروج"
                    }
                }
            })
        else:
            return jsonify({
                "common": {
                    "appName": "Kuwait Social AI",
                    "language": "English",
                    "buttons": {
                        "login": "Login",
                        "signup": "Sign Up",
                        "logout": "Logout"
                    }
                }
            })
EOF < /dev/null
