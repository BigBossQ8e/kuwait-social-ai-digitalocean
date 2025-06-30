#!/usr/bin/env python3
"""
Analyze SQLAlchemy relationships to find mismatches
"""

import re
from collections import defaultdict

def analyze_relationships(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Find all class definitions
    class_pattern = r'class (\w+)\(.*?db\.Model\):'
    classes = re.findall(class_pattern, content)
    
    # Find all relationships
    rel_pattern = r'(\w+)\s*=\s*db\.relationship\([\'"](\w+)[\'"].*?back_populates=[\'"](\w+)[\'"]'
    relationships = re.findall(rel_pattern, content)
    
    # Build a map of relationships
    rel_map = defaultdict(list)
    for attr_name, target_class, back_ref in relationships:
        source_class = None
        # Find which class this relationship belongs to
        for line in content.split('\n'):
            if f'{attr_name} = db.relationship' in line:
                # Look backwards for the class definition
                idx = content.find(line)
                before = content[:idx]
                class_matches = list(re.finditer(r'class (\w+)\(.*?db\.Model\):', before))
                if class_matches:
                    source_class = class_matches[-1].group(1)
                    break
        
        if source_class:
            rel_map[source_class].append({
                'attribute': attr_name,
                'target': target_class,
                'back_populates': back_ref
            })
    
    # Check for mismatches
    mismatches = []
    for source_class, rels in rel_map.items():
        for rel in rels:
            target_class = rel['target']
            expected_back_ref = rel['back_populates']
            
            # Check if target class has the expected relationship back
            found = False
            if target_class in rel_map:
                for target_rel in rel_map[target_class]:
                    if (target_rel['attribute'] == expected_back_ref and 
                        target_rel['target'] == source_class):
                        found = True
                        break
            
            if not found:
                mismatches.append({
                    'source': source_class,
                    'target': target_class,
                    'attribute': rel['attribute'],
                    'expected_back_ref': expected_back_ref,
                    'status': 'MISSING'
                })
    
    return classes, rel_map, mismatches

if __name__ == '__main__':
    print("Analyzing relationships in models.py...")
    classes, relationships, mismatches = analyze_relationships('models.py')
    
    print(f"\nFound {len(classes)} model classes")
    print(f"Found {sum(len(rels) for rels in relationships.values())} relationships")
    
    if mismatches:
        print(f"\n⚠️  Found {len(mismatches)} relationship mismatches:")
        for m in mismatches:
            print(f"\n  - {m['source']}.{m['attribute']} -> {m['target']}")
            print(f"    Expected: {m['target']}.{m['expected_back_ref']} -> {m['source']}")
            print(f"    Status: {m['status']}")
    else:
        print("\n✅ All relationships are properly matched!")
    
    # Also check for backref usage
    with open('models.py', 'r') as f:
        content = f.read()
    backref_count = len(re.findall(r'backref=', content))
    if backref_count > 0:
        print(f"\n⚠️  Found {backref_count} uses of old 'backref' pattern - should migrate to 'back_populates'")