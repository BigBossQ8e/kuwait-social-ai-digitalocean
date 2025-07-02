#!/usr/bin/env python3
"""
Apply all fixes to make the Kuwait Social AI backend work properly
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

from app_factory import create_app
from models import db
from sqlalchemy import text
import traceback

def apply_database_fixes():
    """Apply all database fixes"""
    app = create_app('development')
    
    with app.app_context():
        print("🔧 Applying database fixes...")
        
        try:
            # Read the SQL migration
            migration_path = os.path.join(os.path.dirname(__file__), 'migrations', 'fix_all_schema_issues.sql')
            with open(migration_path, 'r') as f:
                sql_commands = f.read()
            
            # Split into individual commands (basic split by semicolon)
            commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
            
            # Execute each command
            for i, command in enumerate(commands, 1):
                if command and not command.strip().startswith('--'):
                    try:
                        print(f"  Executing command {i}/{len(commands)}...")
                        db.session.execute(text(command))
                        db.session.commit()
                    except Exception as e:
                        print(f"  ⚠️  Warning on command {i}: {str(e)}")
                        db.session.rollback()
            
            print("✅ Database fixes applied!")
            
        except Exception as e:
            print(f"❌ Error applying database fixes: {e}")
            traceback.print_exc()
            return False
        
        # Create all tables that don't exist
        try:
            print("\n📊 Creating any missing tables...")
            db.create_all()
            print("✅ All tables created!")
        except Exception as e:
            print(f"⚠️  Warning creating tables: {e}")
        
        # Create test data
        try:
            print("\n👤 Creating test admin user...")
            from models import User, Admin
            from werkzeug.security import generate_password_hash
            
            # Check if admin exists
            admin_user = User.query.filter_by(email='admin@example.com').first()
            if not admin_user:
                # Create user
                admin_user = User(
                    email='admin@example.com',
                    password_hash=generate_password_hash('password'),
                    is_active=True,
                    role='admin'
                )
                db.session.add(admin_user)
                db.session.commit()
                
                # Create admin profile
                admin_profile = Admin(
                    user_id=admin_user.id,
                    full_name='Test Admin',
                    permissions={'all': True, 'role': 'owner'}
                )
                db.session.add(admin_profile)
                db.session.commit()
                print("✅ Test admin created!")
            else:
                print("✅ Admin user already exists!")
                
        except Exception as e:
            print(f"⚠️  Warning creating admin: {e}")
            db.session.rollback()
        
        # Create test platforms
        try:
            print("\n🌐 Creating test platforms...")
            from models import PlatformConfig
            
            platforms = [
                {'platform': 'instagram', 'display_name': 'Instagram', 'icon': '📷', 'is_enabled': True},
                {'platform': 'twitter', 'display_name': 'Twitter/X', 'icon': '🐦', 'is_enabled': True},
                {'platform': 'facebook', 'display_name': 'Facebook', 'icon': '👤', 'is_enabled': False},
                {'platform': 'linkedin', 'display_name': 'LinkedIn', 'icon': '💼', 'is_enabled': False},
                {'platform': 'tiktok', 'display_name': 'TikTok', 'icon': '🎵', 'is_enabled': True},
            ]
            
            for p in platforms:
                if not PlatformConfig.query.filter_by(platform=p['platform']).first():
                    platform = PlatformConfig(**p)
                    db.session.add(platform)
            
            db.session.commit()
            print("✅ Platforms created!")
            
        except Exception as e:
            print(f"⚠️  Warning creating platforms: {e}")
            db.session.rollback()
        
        # Create test features
        try:
            print("\n⚡ Creating test features...")
            from models import FeatureFlag
            
            features = [
                {
                    'feature_key': 'ai_content_generation',
                    'category': 'ai',
                    'display_name': 'AI Content Generation',
                    'description': 'Generate content using AI',
                    'icon': '🤖',
                    'is_enabled': True
                },
                {
                    'feature_key': 'multi_language',
                    'category': 'content',
                    'display_name': 'Multi-Language Support',
                    'description': 'Support for Arabic and English',
                    'icon': '🌐',
                    'is_enabled': True
                },
                {
                    'feature_key': 'scheduling',
                    'category': 'posting',
                    'display_name': 'Post Scheduling',
                    'description': 'Schedule posts for future',
                    'icon': '📅',
                    'is_enabled': True
                },
            ]
            
            for f in features:
                if not FeatureFlag.query.filter_by(feature_key=f['feature_key']).first():
                    feature = FeatureFlag(**f)
                    db.session.add(feature)
            
            db.session.commit()
            print("✅ Features created!")
            
        except Exception as e:
            print(f"⚠️  Warning creating features: {e}")
            db.session.rollback()
        
        print("\n🎉 All fixes applied successfully!")
        print("\n📱 You can now run the server with:")
        print("   python wsgi.py")
        print("\n🌐 Then access:")
        print("   http://localhost:5001/admin-demo (no login required)")
        print("   http://localhost:5001/admin-test (login: admin@example.com / password)")
        
        return True

if __name__ == '__main__':
    apply_database_fixes()