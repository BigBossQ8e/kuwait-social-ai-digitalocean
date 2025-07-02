#!/usr/bin/env python3
"""
Fix Arabic encoding issues in Flask responses
"""

import os

def add_json_encoder_fix():
    """Add custom JSON encoder to handle Arabic properly"""
    
    config_fix = '''
# JSON encoder configuration for proper Arabic support
class Config(object):
    # ... existing config ...
    
    # Ensure JSON responses don't escape Unicode
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    JSONIFY_MIMETYPE = 'application/json; charset=utf-8'
'''
    
    print("Adding JSON_AS_ASCII = False to configuration files...")
    
    # Check config files
    config_files = [
        'config/config.py',
        'config/development.py',
        'config/production.py'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                content = f.read()
            
            if 'JSON_AS_ASCII' not in content:
                print(f"✅ Fixing {config_file}")
                # Add the configuration
                with open(config_file, 'a') as f:
                    f.write('\n    # Arabic/Unicode support\n')
                    f.write('    JSON_AS_ASCII = False\n')
                    f.write('    JSONIFY_MIMETYPE = "application/json; charset=utf-8"\n')
            else:
                print(f"✓ {config_file} already has JSON_AS_ASCII setting")

def fix_content_generator():
    """Ensure content generator returns proper Unicode"""
    
    print("\nChecking content generator...")
    
    # Add ensure_ascii=False to any json.dumps calls
    files_to_check = [
        'services/content_generator.py',
        'services/ai_service.py',
        'routes/ai_content.py'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check if file has json.dumps without ensure_ascii=False
            if 'json.dumps' in content and 'ensure_ascii=False' not in content:
                print(f"⚠️  {file_path} may need ensure_ascii=False in json.dumps calls")
            else:
                print(f"✓ {file_path} looks OK")

def create_arabic_test_endpoint():
    """Create a test endpoint for Arabic content"""
    
    test_route = '''# Arabic encoding test endpoint
@ai_content_bp.route('/api/test/arabic', methods=['GET'])
def test_arabic_encoding():
    """Test endpoint to verify Arabic encoding"""
    
    test_data = {
        "message": "مرحبا بكم في الكويت",
        "restaurant": "مطعم بيت بيروت",
        "area": "السالمية",
        "special": "عرض خاص للعائلات",
        "mixed": "Special offer - عرض خاص"
    }
    
    return jsonify({
        "status": "success",
        "arabic_test": test_data,
        "encoding": "UTF-8"
    })
'''
    
    print("\nCreating Arabic test endpoint...")
    print("Add this to routes/ai_content.py:")
    print(test_route)

if __name__ == "__main__":
    print("🔧 Fixing Arabic Encoding Issues")
    print("=" * 50)
    
    add_json_encoder_fix()
    fix_content_generator()
    create_arabic_test_endpoint()
    
    print("\n✅ Configuration changes made!")
    print("\nNext steps:")
    print("1. Deploy these changes to production")
    print("2. Restart the Flask app")
    print("3. Test with: curl http://kwtsocial.com/api/test/arabic")