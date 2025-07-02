#!/usr/bin/env python3
"""Test CrewAI 0.100.0 tool patterns"""

from crewai import Agent, Task, Crew
from crewai.tools import tool

# Test 1: New @tool decorator
print("1️⃣ Testing @tool decorator:")
try:
    @tool("Search Tool")
    def search_tool(query: str) -> str:
        """Search for information"""
        return f"Search results for: {query}"
    
    print(f"✅ Tool created: {search_tool.name}")
    print(f"   Type: {type(search_tool)}")
    
    # Try using it with an agent
    agent = Agent(
        role="Test Agent",
        goal="Test tools",
        backstory="Testing tool patterns",
        tools=[search_tool]
    )
    print("✅ Agent created with @tool decorated function")
    
except Exception as e:
    print(f"❌ @tool decorator error: {e}")

# Test 2: LangChain Tool pattern
print("\n2️⃣ Testing LangChain Tool pattern:")
try:
    from langchain.tools import Tool
    
    def analyze_func(input: str) -> str:
        """Analyze something"""
        return f"Analysis of: {input}"
    
    langchain_tool = Tool(
        name="analyzer",
        func=analyze_func,
        description="Analyze input data"
    )
    
    print(f"✅ LangChain Tool created: {langchain_tool.name}")
    print(f"   Type: {type(langchain_tool)}")
    
    # Try using it with an agent
    agent2 = Agent(
        role="Test Agent 2",
        goal="Test langchain tools",
        backstory="Testing langchain tool patterns",
        tools=[langchain_tool]
    )
    print("✅ Agent created with LangChain Tool")
    
except Exception as e:
    print(f"❌ LangChain Tool error: {e}")

# Test 3: Direct function
print("\n3️⃣ Testing direct function:")
try:
    def simple_func(input: str) -> str:
        """Simple function"""
        return f"Result: {input}"
    
    # Set required attributes
    simple_func.name = "simple"
    simple_func.func = simple_func
    simple_func.description = "A simple function"
    
    agent3 = Agent(
        role="Test Agent 3",
        goal="Test direct functions",
        backstory="Testing direct function patterns",
        tools=[simple_func]
    )
    print("✅ Agent created with direct function")
    
except Exception as e:
    print(f"❌ Direct function error: {e}")

print("\n✅ Use @tool decorator from crewai.tools for cleanest code!")