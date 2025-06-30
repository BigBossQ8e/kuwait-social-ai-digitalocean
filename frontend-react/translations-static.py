from flask import Blueprint, jsonify, request

translations_bp = Blueprint('translations', __name__)

# Static translations data
TRANSLATIONS = {
    "en": {
        "common": {
            "appName": "Kuwait Social AI",
            "language": "English",
            "buttons": {
                "login": "Login",
                "signup": "Sign Up",
                "logout": "Logout",
                "submit": "Submit",
                "cancel": "Cancel"
            }
        },
        "landing": {
            "hero": {
                "title": "Kuwait Social AI",
                "subtitle": "Transform your social media presence with AI-powered content creation",
                "cta": "Get Started"
            }
        },
        "auth": {
            "login": {
                "title": "Sign In",
                "email": "Email Address",
                "password": "Password",
                "remember": "Remember me",
                "forgotPassword": "Forgot Password?",
                "noAccount": "Don\'t have an account?",
                "signupLink": "Sign up"
            }
        }
    },
    "ar": {
        "common": {
            "appName": "كويت سوشيال AI",
            "language": "العربية",
            "buttons": {
                "login": "تسجيل الدخول",
                "signup": "إنشاء حساب",
                "logout": "تسجيل الخروج",
                "submit": "إرسال",
                "cancel": "إلغاء"
            }
        },
        "landing": {
            "hero": {
                "title": "كويت سوشيال AI",
                "subtitle": "حوّل تواجدك على وسائل التواصل الاجتماعي باستخدام إنشاء المحتوى المدعوم بالذكاء الاصطناعي",
                "cta": "ابدأ الآن"
            }
        },
        "auth": {
            "login": {
                "title": "تسجيل الدخول",
                "email": "البريد الإلكتروني",
                "password": "كلمة المرور",
                "remember": "تذكرني",
                "forgotPassword": "نسيت كلمة المرور؟",
                "noAccount": "ليس لديك حساب؟",
                "signupLink": "إنشاء حساب"
            }
        }
    }
}

@translations_bp.route('/translations', methods=['GET'])
def get_translations():
    """Get translations for the specified locale"""
    locale = request.args.get('locale', 'en')
    if locale not in TRANSLATIONS:
        locale = 'en'
    
    return jsonify(TRANSLATIONS[locale])
EOF < /dev/null
