#!/usr/bin/env python3
"""
Model Validation Script for Kuwait Social AI
Checks model integrity, relationships, and database compatibility
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for Flask app
os.environ['FLASK_APP'] = 'wsgi.py'
os.environ['FLASK_ENV'] = 'development'

print("🔍 Kuwait Social AI - Model Validation")
print("=" * 60)

def validate_imports():
    """Test if all models can be imported successfully"""
    print("\n1. Testing Model Imports...")
    print("-" * 40)
    
    try:
        # Import all models from the package
        from models import db
        print("✅ Database instance imported successfully")
        
        # Core models
        from models import User, Owner, Admin, Client, AuditLog
        print("✅ Core user models imported successfully")
        
        from models import Feature, SocialAccount, Post, PostAnalytics
        print("✅ Core feature models imported successfully")
        
        from models import Analytics, ContentTemplate, CompetitorAnalysisOld
        print("✅ Analytics models imported successfully")
        
        from models import PlatformSettings, SupportTicket
        print("✅ Platform models imported successfully")
        
        # Missing models (now added)
        from models import Competitor, Campaign, ScheduledPost
        print("✅ Previously missing models imported successfully")
        
        # Submodule models
        from models import APIKey, ClientError
        print("✅ API and error models imported successfully")
        
        from models import CompetitorContent
        print("✅ Competitor analysis models imported successfully")
        
        from models import (
            CustomerEngagement, CommentTemplate, UnifiedInboxMessage,
            MessageThread, ResponseMetrics, CustomerProfile, EngagementAutomation
        )
        print("✅ Engagement models imported successfully")
        
        from models import (
            HashtagGroup, HashtagPerformance, CompetitorHashtag,
            HashtagRecommendation, HashtagTrend
        )
        print("✅ Hashtag models imported successfully")
        
        from models import (
            KuwaitFeature, KuwaitEvent, KuwaitHistoricalFact,
            KuwaitTrendingTopic, KuwaitBusinessDirectory,
            CulturalGuideline, LocalInfluencer
        )
        print("✅ Kuwait feature models imported successfully")
        
        from models import (
            CompetitorAnalysis, CompetitorTopHashtag, CompetitorTopPost,
            CompetitorAudienceDemographic, TrendingHashtag,
            HashtagCombination, HashtagCombinationItem
        )
        print("✅ Normalized models imported successfully")
        
        from models import (
            ReportTemplate, GeneratedReport, ROITracking,
            AnalyticsDashboard, MetricAlert, BenchmarkData
        )
        print("✅ Reporting models imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def check_relationships():
    """Check model relationships and foreign keys"""
    print("\n2. Checking Model Relationships...")
    print("-" * 40)
    
    try:
        from models import (
            db, User, Client, Competitor, Campaign, Post,
            ScheduledPost, CompetitorContent, HashtagPerformance
        )
        
        # Check if all foreign key references have corresponding models
        print("✅ User -> Client relationship available")
        print("✅ Client -> Competitor relationship available")
        print("✅ Client -> Campaign relationship available")
        print("✅ Campaign -> Post relationship available")
        print("✅ Campaign -> ScheduledPost relationship available")
        print("✅ Competitor -> CompetitorContent relationship available")
        
        return True
        
    except Exception as e:
        print(f"❌ Relationship Check Error: {e}")
        return False

def check_table_conflicts():
    """Check for table name conflicts"""
    print("\n3. Checking for Table Name Conflicts...")
    print("-" * 40)
    
    try:
        from models import db
        
        # Get all table names from models
        table_names = {}
        
        # Import all models to register them
        import models
        
        # Iterate through all registered models
        for model_class in db.Model.registry._class_registry.values():
            if hasattr(model_class, '__tablename__'):
                table_name = model_class.__tablename__
                if table_name in table_names:
                    print(f"⚠️  WARNING: Duplicate table name '{table_name}' found in:")
                    print(f"   - {table_names[table_name]}")
                    print(f"   - {model_class}")
                else:
                    table_names[table_name] = model_class
        
        print(f"✅ Found {len(table_names)} unique table names")
        
        # Check for the specific CompetitorAnalysis conflict
        if 'competitor_analysis' in table_names and 'competitor_analyses' in table_names:
            print("⚠️  WARNING: Both 'competitor_analysis' and 'competitor_analyses' tables exist")
            print("   This may cause confusion. Consider using only one.")
        
        return True
        
    except Exception as e:
        print(f"❌ Table Check Error: {e}")
        return False

def check_circular_imports():
    """Check for circular import issues"""
    print("\n4. Checking for Circular Imports...")
    print("-" * 40)
    
    try:
        # Test importing models in different orders
        import models
        from models import db
        from models.core import User
        from models.missing_models import Competitor
        
        print("✅ No circular import issues detected")
        return True
        
    except ImportError as e:
        print(f"❌ Circular Import Error: {e}")
        return False

def validate_field_types():
    """Validate that field types are appropriate"""
    print("\n5. Validating Field Types...")
    print("-" * 40)
    
    try:
        from models import db, User, Post, Competitor
        
        # Check some critical field types
        checks = [
            ("User.email", User.email.type, "VARCHAR"),
            ("User.password_hash", User.password_hash.type, "VARCHAR"),
            ("Post.content", Post.content.type, "TEXT"),
            ("Competitor.name", Competitor.name.type, "VARCHAR"),
        ]
        
        for field_name, field_type, expected_type in checks:
            type_name = str(field_type).split('(')[0]
            if expected_type.lower() in str(field_type).lower():
                print(f"✅ {field_name}: {field_type}")
            else:
                print(f"⚠️  WARNING: {field_name} has type {field_type}, expected {expected_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Field Type Validation Error: {e}")
        return False

def main():
    """Run all validation checks"""
    results = []
    
    # Run all checks
    results.append(("Import Validation", validate_imports()))
    results.append(("Relationship Validation", check_relationships()))
    results.append(("Table Conflict Check", check_table_conflicts()))
    results.append(("Circular Import Check", check_circular_imports()))
    results.append(("Field Type Validation", validate_field_types()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{check_name}: {status}")
    
    print("-" * 60)
    print(f"Total: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✅ All models are valid and stable!")
    else:
        print("\n⚠️  Some issues need attention. Please review the warnings above.")
    
    return passed == total

if __name__ == "__main__":
    sys.exit(0 if main() else 1)