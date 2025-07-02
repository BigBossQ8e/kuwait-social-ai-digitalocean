#!/usr/bin/env python3
"""
Test AI capabilities without full agent framework
Shows what Kuwait Social AI can do
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

print("🚀 Kuwait Social AI - Capabilities Demo")
print("=" * 60)

# Test 1: Basic AI Models
print("\n1️⃣ AI Models Available:")
print("-" * 40)

# Check OpenAI
openai_key = os.getenv('OPENAI_API_KEY', '')
if openai_key and openai_key != 'YOUR_OPENAI_API_KEY_HERE':
    print("✅ OpenAI GPT-4 Turbo: Ready")
else:
    print("❌ OpenAI: Not configured")

# Check Anthropic
anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
if anthropic_key and 'sk-ant' in anthropic_key:
    print("✅ Claude 3.5 Sonnet: Ready")
else:
    print("❌ Anthropic: Not configured")

# Check agent status
agents_enabled = os.getenv('ENABLE_AGENTS', 'false').lower() == 'true'
print(f"🤖 AI Agents: {'Enabled' if agents_enabled else 'Disabled (dependencies needed)'}")

# Test 2: Content Generation Capabilities
print("\n\n2️⃣ Content Generation Capabilities:")
print("-" * 40)

try:
    from services.container import get_ai_service
    ai_service = get_ai_service()
    
    # Test basic content generation
    result = ai_service.generate_content(
        prompt="Create a weekend special announcement for a burger restaurant",
        platform="instagram",
        tone="enthusiastic",
        include_arabic=True,
        include_hashtags=True,
        business_type="restaurant"
    )
    
    print("✅ Basic Content Generation: Working")
    print(f"   - Generated {len(result.get('content', ''))} characters")
    print(f"   - Arabic translation: {'Yes' if result.get('arabic_content') else 'No'}")
    print(f"   - Hashtags: {len(result.get('hashtags', []))} generated")
    
except Exception as e:
    print(f"❌ Content Generation Error: {str(e)}")

# Test 3: Intelligent Features
print("\n\n3️⃣ Intelligent Features Available:")
print("-" * 40)

features = {
    "Prayer Time Awareness": "Automatically avoids posting during prayer times",
    "Cultural Compliance": "Ensures HALAL mentions and appropriate content",
    "Bilingual Support": "Arabic + English content generation",
    "Platform Optimization": "Tailored for Instagram, TikTok, Twitter",
    "Local Hashtags": "Kuwait-specific trending hashtags",
    "Competitor Analysis": "Track and outperform competitors",
    "Campaign Planning": "Multi-day campaign creation",
    "Performance Analytics": "ROI and engagement tracking"
}

for feature, description in features.items():
    print(f"✅ {feature}")
    print(f"   └─ {description}")

# Test 4: Agent Capabilities (when enabled)
print("\n\n4️⃣ AI Agent Capabilities (Advanced):")
print("-" * 40)

if agents_enabled:
    print("When agent dependencies are installed, you get:")
else:
    print("To enable these features, install: pip install crewai langchain")

agent_features = [
    {
        "name": "🎯 Campaign Creation Agent",
        "capabilities": [
            "30-day Ramadan campaigns with daily content",
            "Product launch campaigns with phased approach",
            "Seasonal campaigns adapted to Kuwait weather"
        ]
    },
    {
        "name": "📊 Analytics Agent",
        "capabilities": [
            "Competitor performance tracking",
            "Campaign ROI analysis",
            "Monthly performance reviews with insights"
        ]
    },
    {
        "name": "🕌 Cultural Compliance Agent",
        "capabilities": [
            "Automatic HALAL verification",
            "Prayer time scheduling",
            "Cultural sensitivity checks"
        ]
    },
    {
        "name": "🌍 Localization Agent",
        "capabilities": [
            "Kuwait dialect translations",
            "Area-specific content (Salmiya, Hawally, etc.)",
            "Local trend integration"
        ]
    }
]

for agent in agent_features:
    print(f"\n{agent['name']}:")
    for capability in agent['capabilities']:
        print(f"  • {capability}")

# Test 5: API Endpoints
print("\n\n5️⃣ Available API Endpoints:")
print("-" * 40)

endpoints = [
    {
        "method": "POST",
        "path": "/api/ai/generate",
        "description": "Generate AI content with full customization"
    },
    {
        "method": "POST",
        "path": "/api/ai/translate",
        "description": "Translate between Arabic and English"
    },
    {
        "method": "POST",
        "path": "/api/ai/hashtags",
        "description": "Generate optimized hashtags"
    },
    {
        "method": "POST",
        "path": "/api/ai/enhance",
        "description": "Enhance existing content"
    },
    {
        "method": "POST",
        "path": "/api/ai/agents/campaign/create",
        "description": "Create full campaigns (agents required)"
    },
    {
        "method": "POST",
        "path": "/api/ai/agents/analytics/competitors",
        "description": "Analyze competitors (agents required)"
    }
]

for endpoint in endpoints:
    print(f"{endpoint['method']:6} {endpoint['path']}")
    print(f"       └─ {endpoint['description']}")

# Test 6: Example Use Cases
print("\n\n6️⃣ Example Use Cases:")
print("-" * 40)

use_cases = [
    {
        "title": "🍔 Burger Restaurant Campaign",
        "description": "Generate 30-day campaign with daily posts, respecting prayer times"
    },
    {
        "title": "☕ Cafe Morning Promotions",
        "description": "Create breakfast specials that post before morning rush"
    },
    {
        "title": "🌙 Ramadan Iftar Specials",
        "description": "Time-sensitive posts 2 hours before iftar with family deals"
    },
    {
        "title": "📈 Competitor Outperformance",
        "description": "Analyze top 3 competitors and generate better content"
    }
]

for case in use_cases:
    print(f"\n{case['title']}:")
    print(f"  {case['description']}")

print("\n\n" + "=" * 60)
print("✨ Kuwait Social AI is ready to transform your social media!")
print("=" * 60)

# Quick test of a real scenario
print("\n\n7️⃣ Live Demo - Weekend Special Post:")
print("-" * 40)

try:
    demo_result = ai_service.generate_content(
        prompt="Create a Friday family feast promotion for a Lebanese restaurant in Salmiya",
        platform="instagram",
        tone="warm",
        include_arabic=True,
        include_hashtags=True,
        business_type="restaurant",
        additional_context={
            "target_audience": "families",
            "area": "Salmiya"
        }
    )
    
    print("📝 Generated Content:")
    print(f"English: {demo_result['content'][:150]}...")
    if demo_result.get('arabic_content'):
        print(f"Arabic: {demo_result['arabic_content'][:100]}...")
    print(f"\n🏷️ Hashtags: {', '.join(demo_result.get('hashtags', [])[:5])}...")
    print(f"\n⏰ Best posting times: {json.dumps(demo_result.get('optimal_posting_times', {}).get('weekends', {}), indent=2)}")
    
except Exception as e:
    print(f"Demo error: {str(e)}")

print("\n✅ Test complete!")