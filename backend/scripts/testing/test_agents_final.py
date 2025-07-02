#!/usr/bin/env python3
"""Final test for agent framework after CrewAI 0.100.0 upgrade"""

import sys
sys.path.insert(0, '.')

print("🧪 Testing Agent Framework")
print("=" * 60)

# Test 1: Import all components
print("\n1️⃣ Testing imports:")
try:
    from services.ai_agents import KuwaitFBAgents
    print("✅ KuwaitFBAgents imported")
    
    from services.ai_agents.base_agent import KuwaitBaseAgent
    print("✅ KuwaitBaseAgent imported")
    
    from services.ai_agents.tools.research_tools import CompetitorAnalysisTool
    print("✅ CompetitorAnalysisTool imported")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Create agents
print("\n2️⃣ Testing agent creation:")
try:
    agents = KuwaitFBAgents()
    print("✅ KuwaitFBAgents created")
    print(f"   - Market researcher: {agents.market_researcher.role}")
    print(f"   - Cultural compliance: {agents.cultural_compliance.role}")
    print(f"   - Content creator: {agents.content_creator.role}")
    print(f"   - Timing expert: {agents.timing_expert.role}")
    
except Exception as e:
    print(f"❌ Agent creation error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Check tools
print("\n3️⃣ Testing tools:")
try:
    tool = CompetitorAnalysisTool
    print(f"✅ Tool available: {tool.name}")
    print(f"   - Description: {tool.description[:50]}...")
    print(f"   - Type: {type(tool)}")
    
except Exception as e:
    print(f"❌ Tool error: {e}")

# Test 4: Full AI service test
print("\n4️⃣ Testing AI service with agents:")
try:
    from services.container import get_ai_service
    ai_service = get_ai_service()
    
    if hasattr(ai_service, 'agents_available') and ai_service.agents_available:
        print("✅ Agents are available in AI service")
    else:
        print("⚠️  Agents not available in AI service")
        
except Exception as e:
    print(f"❌ AI service error: {e}")

print("\n" + "=" * 60)
print("🎉 Test complete!")