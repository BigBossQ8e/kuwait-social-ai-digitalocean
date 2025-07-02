#!/usr/bin/env python3
"""List all available API routes"""

from app_factory import create_app

app = create_app('development')

print("🌐 AVAILABLE API ROUTES")
print("=" * 60)

with app.app_context():
    routes = []
    for rule in app.url_map.iter_rules():
        if 'static' not in rule.endpoint:
            methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
            routes.append((rule.rule, methods))
    
    # Sort and display
    for route, methods in sorted(routes):
        print(f"{methods:8} {route}")

print("\n📝 Example API Calls:")
print("=" * 60)
print("# Health Check")
print("curl http://localhost:5001/api/health")
print("\n# Generate AI Content (requires auth)")
print("curl -X POST http://localhost:5001/api/ai/generate \\")
print("  -H 'Content-Type: application/json' \\")
print("  -H 'Authorization: Bearer YOUR_TOKEN' \\")
print("  -d '{\"prompt\": \"Create a post about burgers\", \"platform\": \"instagram\"}'")