#!/usr/bin/env python3
"""Fix tool class annotations for CrewAI 0.100.0 compatibility"""

import re
from pathlib import Path

def fix_tool_file(filepath):
    """Fix tool class annotations in a single file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Pattern to find tool classes with untyped attributes
    pattern = r'(class \w+Tool\(BaseTool\):\s*\n(?:\s*"""[^"]*"""\s*\n)?)'
    pattern += r'(\s*)(name = "[^"]+"\s*\n)'
    pattern += r'(\s*)(description = "[^"]+"\s*\n)'
    pattern += r'(\s*)(args_schema = \w+)'
    
    def replacement(match):
        class_def = match.group(1)
        indent1 = match.group(2)
        name_line = match.group(3)
        indent2 = match.group(4)
        desc_line = match.group(5)
        indent3 = match.group(6)
        schema_line = match.group(7)
        
        # Extract values
        name_value = re.search(r'name = (".*?")', name_line).group(1)
        desc_value = re.search(r'description = (".*?")', desc_line).group(1)
        schema_value = re.search(r'args_schema = (\w+)', schema_line).group(1)
        
        # Create typed versions
        new_name = f'{indent1}name: str = {name_value}\n'
        new_desc = f'{indent2}description: str = {desc_value}\n'
        new_schema = f'{indent3}args_schema: type[BaseModel] = {schema_value}'
        
        return class_def + new_name + new_desc + new_schema
    
    # Apply replacement
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Fixed: {filepath.name}")
        return True
    else:
        print(f"⚠️  No changes needed: {filepath.name}")
        return False

# Fix all tool files
tools_dir = Path("services/ai_agents/tools")
fixed_count = 0

for tool_file in tools_dir.glob("*_tools.py"):
    if fix_tool_file(tool_file):
        fixed_count += 1

print(f"\n✅ Fixed {fixed_count} files")