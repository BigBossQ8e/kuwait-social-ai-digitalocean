#!/bin/bash

echo "🚨 Emergency Backend Fix..."

ssh root@209.38.176.129 << 'ENDSSH'
cd /opt/kuwait-social-ai/backend

echo "1. Stopping all processes..."
pkill -f gunicorn
pkill -f python
sleep 2

echo "2. Disabling all problematic services and routes..."
# Disable services
for file in hashtag_strategy_service.py normalized_query_examples.py competitor_analysis_service.py; do
    [ -f "services/$file" ] && mv "services/$file" "services/$file.disabled" 2>/dev/null
done

# Disable routes
for file in competitors.py; do
    [ -f "routes/client/$file" ] && mv "routes/client/$file" "routes/client/$file.disabled" 2>/dev/null
done

echo "3. Fixing all imports..."
# Fix service imports
find . -name "*.py" -type f -exec grep -l "hashtag_strategy_service\|normalized_query_examples\|competitor_analysis_service" {} \; | while read file; do
    echo "  Fixing: $file"
    sed -i 's/from services.hashtag_strategy_service/# from services.hashtag_strategy_service/g' "$file"
    sed -i 's/from services.normalized_query_examples/# from services.normalized_query_examples/g' "$file"
    sed -i 's/from services.competitor_analysis_service/# from services.competitor_analysis_service/g' "$file"
    sed -i 's/import HashtagStrategyService/# import HashtagStrategyService/g' "$file"
    sed -i 's/import CompetitorAnalysisService/# import CompetitorAnalysisService/g' "$file"
done

# Fix model imports
find . -name "*.py" -type f -exec grep -l "from models\." {} \; | grep -v "from models import" | while read file; do
    echo "  Fixing model imports in: $file"
    sed -i 's/from models\./# from models./g' "$file"
done

echo "4. Removing usage of disabled services..."
# Comment out service usages
sed -i 's/competitor_service = CompetitorAnalysisService/# competitor_service = CompetitorAnalysisService/g' routes/client/*.py 2>/dev/null
sed -i 's/hashtag_service = HashtagStrategyService/# hashtag_service = HashtagStrategyService/g' routes/client/*.py 2>/dev/null

echo "5. Cleaning Python cache..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo "6. Starting backend with environment..."
export $(grep -v '^#' .env | xargs)
/usr/local/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 3 \
    --daemon \
    --pid /tmp/gunicorn.pid \
    --error-logfile logs/error.log \
    --access-logfile logs/access.log \
    wsgi:app

echo "7. Waiting for startup..."
sleep 7

echo "8. Checking status..."
if ps -p $(cat /tmp/gunicorn.pid 2>/dev/null) > /dev/null 2>&1; then
    echo "✅ Backend is running!"
    ps aux | grep gunicorn | grep -v grep
else
    echo "❌ Backend failed to start"
    echo "Last errors:"
    tail -20 logs/error.log | grep -A3 -B3 "Error\|error"
fi

echo ""
echo "9. Testing API..."
curl -s http://localhost:5000/api/health || echo "API test failed"

ENDSSH

echo ""
echo "10. External test..."
curl -s https://kwtsocial.com/api/health