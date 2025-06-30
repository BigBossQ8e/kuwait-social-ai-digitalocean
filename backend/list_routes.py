#!/usr/bin/env python3
"""List all registered routes in the Flask application"""

from dotenv import load_dotenv
load_dotenv()

from app_factory import create_app
from tabulate import tabulate

app = create_app()

with app.app_context():
    print("=== Kuwait Social AI - Registered Routes ===\n")
    
    routes = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        routes.append([
            rule.endpoint,
            methods,
            str(rule)
        ])
    
    # Sort by URL
    routes.sort(key=lambda x: x[2])
    
    print(tabulate(routes, headers=['Endpoint', 'Methods', 'URL'], tablefmt='grid'))
    
    print(f"\nTotal routes: {len(routes)}")
    
    # Group by blueprint
    print("\n=== Routes by Blueprint ===")
    blueprints = {}
    for rule in app.url_map.iter_rules():
        blueprint = rule.endpoint.split('.')[0] if '.' in rule.endpoint else 'core'
        if blueprint not in blueprints:
            blueprints[blueprint] = []
        blueprints[blueprint].append(str(rule))
    
    for bp, urls in sorted(blueprints.items()):
        print(f"\n{bp}:")
        for url in sorted(urls):
            print(f"  {url}")