#!/usr/bin/env python3
"""Test new tool pattern with CrewAI 0.100.0"""

import sys
sys.path.insert(0, '.')

from crewai import Agent
from crewai.tools import tool

# Create a simple tool using @tool decorator
@tool("Restaurant Analyzer")
def analyze_restaurant(name: str) -> str:
    """Analyze a restaurant's performance"""
    return f"Analysis for {name}: Great food, excellent service, popular on weekends"

# Test creating an agent with the new tool
try:
    agent = Agent(
        role="Food Critic",
        goal="Analyze restaurants",
        backstory="Expert food critic in Kuwait",
        tools=[analyze_restaurant]
    )
    print("✅ Agent created successfully with @tool decorator!")
    print(f"   Tool name: {analyze_restaurant.name}")
    print(f"   Tool type: {type(analyze_restaurant)}")
except Exception as e:
    print(f"❌ Failed: {e}")

# Now let's see if we need to update our approach
print("\n💡 Solution: Update tools to use @tool decorator from crewai.tools")