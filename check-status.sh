#!/bin/bash

echo "=== Kuwait Social AI Status Check ==="
echo ""

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    echo "Please make sure Docker Desktop is running"
    exit 1
fi

# Check container status
echo "📦 Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🌐 Access URLs:"
echo "Frontend: http://localhost:80 (or just http://localhost)"
echo "Backend API: http://localhost:5000"
echo "PostgreSQL: localhost:5432"
echo "Redis: localhost:6379"

echo ""
echo "📋 Checking logs for errors..."
echo ""

# Check backend logs for errors
echo "=== Backend Recent Logs ==="
docker logs kuwait-social-backend --tail 20 2>&1 | grep -E "(ERROR|error|Error|CRITICAL|Failed)" || echo "✅ No recent errors in backend"

echo ""
echo "=== Frontend Recent Logs ==="
docker logs kuwait-social-frontend --tail 20 2>&1 | grep -E "(ERROR|error|Error|CRITICAL|Failed)" || echo "✅ No recent errors in frontend"

echo ""
echo "💡 Troubleshooting:"
echo "- If containers are not running: docker-compose up -d --build"
echo "- To see all logs: docker-compose logs -f"
echo "- To restart: docker-compose restart"