#!/usr/bin/env python3
"""Test to reproduce the agent error"""
import sys
sys.path.insert(0, '.')

from crewai import Agent

# Try basic agent creation
try:
    agent = Agent(
        role="Test Agent",
        goal="Test the system",
        backstory="A test agent"
    )
    print("✅ Basic Agent creation works")
except Exception as e:
    print(f"❌ Basic Agent creation failed: {e}")

# Try importing our custom agent
try:
    from services.ai_agents.base_agent import KuwaitBaseAgent
    print("✅ KuwaitBaseAgent import successful")
    
    # Try creating an instance
    kuwait_agent = KuwaitBaseAgent(
        role="Test Kuwait Agent",
        goal="Test Kuwait functionality",
        backstory="A Kuwait test agent"
    )
    print("✅ KuwaitBaseAgent instantiation successful")
    
except Exception as e:
    print(f"❌ KuwaitBaseAgent error: {e}")
    import traceback
    traceback.print_exc()