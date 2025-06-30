#!/bin/bash

echo "🔧 Fixing model imports..."

ssh root@209.38.176.129 << 'ENDSSH'
cd /opt/kuwait-social-ai/backend

echo "Step 1: Fixing competitor analysis imports..."
# Fix in services
sed -i 's/from models.competitor_analysis_models import/# from models.competitor_analysis_models import/' services/competitor_analysis_service.py

# Fix in routes
sed -i 's/from models.competitor_analysis_models import/# from models.competitor_analysis_models import/' routes/competitor.py

# Alternative: check if the models exist in models.py
echo ""
echo "Step 2: Checking if competitor models exist in models.py..."
grep -n "class Competitor" models.py | head -5 || echo "No competitor models found in models.py"

echo ""
echo "Step 3: Removing competitor blueprint temporarily..."
cp app_factory.py app_factory.py.bak
sed -i '/from routes.competitor import competitor_bp/d' app_factory.py
sed -i '/app.register_blueprint(competitor_bp/d' app_factory.py

echo ""
echo "Step 4: Clearing Python cache..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo ""
echo "Step 5: Restarting service..."
pkill -f gunicorn 2>/dev/null || true
sleep 2

# Start with environment
export $(cat .env | grep -v '^#' | xargs)
/usr/local/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --daemon wsgi:app

echo ""
echo "Step 6: Waiting and testing..."
sleep 5

echo -n "API test: "
curl -s http://localhost:5000/api/health -w " (HTTP %{http_code})\n" || echo "Failed"

echo ""
echo "Step 7: Checking for other import errors..."
tail -20 logs/error.log 2>/dev/null | grep -i "import\|module" | tail -5

echo ""
echo "✅ Import fixes applied!"
ENDSSH

echo ""
echo "🌐 Final test..."
curl -s https://kwtsocial.com/api/health