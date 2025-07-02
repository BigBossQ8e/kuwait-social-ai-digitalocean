#!/usr/bin/env python
"""
Setup test data for admin panel
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_factory import create_app
from models import db, PlatformConfig, FeatureFlag, FeatureSubflag, Package
from datetime import datetime

def setup_test_data():
    """Create test data for admin panel"""
    app = create_app('development')
    
    with app.app_context():
        # Create platforms if they don't exist
        platforms = [
            {'platform': 'instagram', 'display_name': 'Instagram', 'icon': '📷', 'is_enabled': True},
            {'platform': 'twitter', 'display_name': 'Twitter/X', 'icon': '🐦', 'is_enabled': True},
            {'platform': 'facebook', 'display_name': 'Facebook', 'icon': '👤', 'is_enabled': False},
            {'platform': 'linkedin', 'display_name': 'LinkedIn', 'icon': '💼', 'is_enabled': False},
            {'platform': 'tiktok', 'display_name': 'TikTok', 'icon': '🎵', 'is_enabled': True},
            {'platform': 'youtube', 'display_name': 'YouTube', 'icon': '📺', 'is_enabled': False},
        ]
        
        for p in platforms:
            existing = PlatformConfig.query.filter_by(platform=p['platform']).first()
            if not existing:
                platform = PlatformConfig(**p)
                db.session.add(platform)
                print(f"Created platform: {p['display_name']}")
        
        # Create feature flags
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
                'description': 'Support for Arabic and English content',
                'icon': '🌐',
                'is_enabled': True
            },
            {
                'feature_key': 'scheduling',
                'category': 'posting',
                'display_name': 'Post Scheduling',
                'description': 'Schedule posts for future publishing',
                'icon': '📅',
                'is_enabled': True
            },
            {
                'feature_key': 'analytics',
                'category': 'insights',
                'display_name': 'Analytics Dashboard',
                'description': 'View detailed analytics and insights',
                'icon': '📊',
                'is_enabled': True
            },
            {
                'feature_key': 'team_collaboration',
                'category': 'team',
                'display_name': 'Team Collaboration',
                'description': 'Collaborate with team members',
                'icon': '👥',
                'is_enabled': False
            },
            {
                'feature_key': 'bulk_upload',
                'category': 'content',
                'display_name': 'Bulk Upload',
                'description': 'Upload multiple posts at once',
                'icon': '📤',
                'is_enabled': True
            }
        ]
        
        for f in features:
            existing = FeatureFlag.query.filter_by(feature_key=f['feature_key']).first()
            if not existing:
                feature = FeatureFlag(**f)
                db.session.add(feature)
                print(f"Created feature: {f['display_name']}")
        
        # Create packages
        packages = [
            {
                'name': 'starter',
                'display_name': 'Starter Plan',
                'description': 'Perfect for individuals',
                'price_kwd': 9.99,
                'max_platforms': 2,
                'max_posts_per_month': 30,
                'is_active': True
            },
            {
                'name': 'professional',
                'display_name': 'Professional Plan',
                'description': 'For growing businesses',
                'price_kwd': 29.99,
                'max_platforms': 5,
                'max_posts_per_month': 100,
                'is_active': True
            },
            {
                'name': 'enterprise',
                'display_name': 'Enterprise Plan',
                'description': 'Full-featured for large teams',
                'price_kwd': 99.99,
                'max_platforms': 10,
                'max_posts_per_month': -1,  # unlimited
                'is_active': True
            }
        ]
        
        for p in packages:
            existing = Package.query.filter_by(name=p['name']).first()
            if not existing:
                package = Package(**p)
                db.session.add(package)
                print(f"Created package: {p['display_name']}")
        
        db.session.commit()
        print("\nTest data setup complete!")

if __name__ == '__main__':
    setup_test_data()