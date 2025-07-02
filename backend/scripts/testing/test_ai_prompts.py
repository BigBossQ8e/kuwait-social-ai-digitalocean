#!/usr/bin/env python3
"""
Test AI Prompts System
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ai_prompts():
    """Test AI prompts functionality"""
    print("Testing AI Prompts System...")
    print("=" * 50)
    
    # Test models
    try:
        from models.ai_prompts import AIPrompt, AIPromptTemplate, AIPromptVersion
        print("✅ AI Prompt models imported successfully")
    except Exception as e:
        print(f"❌ Failed to import models: {e}")
        return
    
    # Test Kuwaiti NLP service
    try:
        from services.kuwaiti_nlp_service import KuwaitiNLPService
        nlp = KuwaitiNLPService()
        print("✅ Kuwaiti NLP service imported successfully")
        
        # Test dialect processing
        test_text = "شلونك؟ وايد زين المطعم"
        processed = nlp.process_text(test_text)
        print(f"\nDialect Processing Test:")
        print(f"  Original: {test_text}")
        print(f"  Processed: {processed}")
        
    except Exception as e:
        print(f"❌ Failed to test NLP service: {e}")
    
    # Test database
    try:
        import sqlite3
        conn = sqlite3.connect('kuwait_social.db')
        cursor = conn.cursor()
        
        # Check templates
        cursor.execute("SELECT COUNT(*) FROM ai_prompt_templates")
        template_count = cursor.fetchone()[0]
        print(f"\n✅ Database has {template_count} prompt templates")
        
        # List templates
        cursor.execute("SELECT name, category FROM ai_prompt_templates")
        templates = cursor.fetchall()
        print("\nAvailable Templates:")
        for name, category in templates:
            print(f"  - {name} ({category})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    print("\n" + "=" * 50)
    print("AI Prompts UI available at:")
    print("  http://localhost:5001/admin-prompts")
    print("\nFeatures:")
    print("  - Create/edit AI prompts")
    print("  - Enable Kuwaiti NLP processing")
    print("  - Version control with rollback")
    print("  - Test prompts in playground")
    print("  - Use pre-built templates")

if __name__ == "__main__":
    test_ai_prompts()